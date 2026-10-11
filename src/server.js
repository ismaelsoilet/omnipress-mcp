#!/usr/bin/env node
/**
 * OmniPress MCP Server — Pure Node.js implementation (Zero dependencies, native stdio JSON-RPC).
 * Compatible with Node.js 18+ / 20+ / 24+ without requiring `npm install`.
 */

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const readline = require('node:readline');
const http = require('node:http');
const url = require('node:url');
const { execFile } = require('node:child_process');

// ==========================================
// Environment & Configuration
// ==========================================
const PROJECT_ROOT = path.resolve(__dirname, '..');

// Basic .env parser to avoid third-party dependencies
function loadEnv() {
  const envPath = path.join(PROJECT_ROOT, '.env');
  if (fs.existsSync(envPath)) {
    const lines = fs.readFileSync(envPath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx !== -1) {
        const key = trimmed.slice(0, eqIdx).trim();
        const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
        if (!process.env[key]) {
          process.env[key] = val;
        }
      }
    }
  }
}
loadEnv();

function getArticlesDir() {
  return path.resolve(process.env.ARTICLES_DIR || path.join(PROJECT_ROOT, 'articles'));
}
function getMediaStagingDir() {
  return path.resolve(process.env.MEDIA_STAGING_DIR || path.join(PROJECT_ROOT, 'media', 'staging'));
}
const BUFFER_ACCESS_TOKEN = process.env.BUFFER_ACCESS_TOKEN || '';
const BUFFER_LINKEDIN_PROFILE_ID = process.env.BUFFER_LINKEDIN_PROFILE_ID || '';
const BUFFER_X_PROFILE_ID = process.env.BUFFER_X_PROFILE_ID || '';
const BUFFER_THREADS_PROFILE_ID = process.env.BUFFER_THREADS_PROFILE_ID || '';
const BUFFER_INSTAGRAM_PROFILE_ID = process.env.BUFFER_INSTAGRAM_PROFILE_ID || '';

// YouTube & Video settings
const YOUTUBE_WEBHOOK_URL = process.env.YOUTUBE_WEBHOOK_URL || '';
const TIKTOK_WEBHOOK_URL = process.env.TIKTOK_WEBHOOK_URL || '';

// Reddit API credentials
const REDDIT_CLIENT_ID = process.env.REDDIT_CLIENT_ID || '';
const REDDIT_CLIENT_SECRET = process.env.REDDIT_CLIENT_SECRET || '';
const REDDIT_USERNAME = process.env.REDDIT_USERNAME || '';
const REDDIT_PASSWORD = process.env.REDDIT_PASSWORD || '';
const REDDIT_DEFAULT_SUBREDDIT = process.env.REDDIT_DEFAULT_SUBREDDIT || 'SideProject';

const OMNIPRESS_WEBHOOK_URL = process.env.OMNIPRESS_WEBHOOK_URL || '';
const OMNIPRESS_WEBHOOK_SECRET = process.env.OMNIPRESS_WEBHOOK_SECRET || '';

// ==========================================
// Privacy & De-Identification Sanitizer
// ==========================================
const CNJ_REGEX = /\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b/g;
const CPF_REGEX = /\b\d{3}\.\d{3}\.\d{3}-\d{2}\b/g;
const CNPJ_REGEX = /\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b/g;
const EMAIL_REGEX = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b/g;

function inspectSensitiveData(text) {
  const findings = [];
  let match;
  
  const cnjMatches = text.match(CNJ_REGEX) || [];
  cnjMatches.forEach(m => findings.push({ type: 'lawsuit_number', match: m }));

  const cpfMatches = text.match(CPF_REGEX) || [];
  cpfMatches.forEach(m => findings.push({ type: 'cpf', match: m }));

  const cnpjMatches = text.match(CNPJ_REGEX) || [];
  cnpjMatches.forEach(m => findings.push({ type: 'cnpj', match: m }));

  const emailMatches = text.match(EMAIL_REGEX) || [];
  emailMatches.forEach(m => findings.push({ type: 'email', match: m }));

  return findings;
}

function sanitizeText(text) {
  const findings = inspectSensitiveData(text);
  let sanitized = text
    .replace(CNJ_REGEX, '[PROCESSO ANÔNIMO]')
    .replace(CPF_REGEX, '[CPF PROTEGIDO]')
    .replace(CNPJ_REGEX, '[CNPJ PROTEGIDO]')
    .replace(EMAIL_REGEX, '[EMAIL PROTEGIDO]');
  return { sanitized, findings };
}

function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/[-\s]+/g, '-');
}

// ==========================================
// Core Publishing Logic
// ==========================================
function saveArticle({ title, contentMarkdown, category = 'technology', tags = [], author = 'OmniPress', sanitize = true }) {
  let content = contentMarkdown;
  let findings = [];

  if (sanitize) {
    const res = sanitizeText(contentMarkdown);
    content = res.sanitized;
    findings = res.findings;
  }

  const now = new Date();
  const yyyy = now.getUTCFullYear().toString();
  const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(now.getUTCDate()).padStart(2, '0');
  const dateStr = `${yyyy}-${mm}-${dd}`;
  const slug = slugify(title) || `article-${Date.now()}`;

  const baseDir = getArticlesDir();
  const targetDir = path.join(baseDir, yyyy, mm);
  fs.mkdirSync(targetDir, { recursive: true });

  const filename = `${dateStr}-${slug}.md`;
  const filepath = path.join(targetDir, filename);

  const yamlTags = (tags || []).map(t => `  - ${t}`).join('\n');
  const frontmatter = [
    '---',
    `title: "${title}"`,
    `date: "${now.toISOString()}"`,
    `category: "${category}"`,
    `author: "${author}"`,
    'tags:',
    yamlTags,
    'status: draft',
    '---',
    '',
    ''
  ].join('\n');

  fs.writeFileSync(filepath, frontmatter + content.trim() + '\n', 'utf8');

  // If webhook configured, dispatch async event
  if (OMNIPRESS_WEBHOOK_URL) {
    dispatchWebhook('article_saved', { title, filename, filepath, category, tags });
  }

  let report = [
    `✅ Article archived successfully: **${filename}**`,
    `📁 Path: \`${filepath}\``,
    `🏷️ Category: \`${category}\` | Tags: ${JSON.stringify(tags || [])}`
  ];

  if (findings.length > 0) {
    report.push(`\n🔒 Anonymized ${findings.length} sensitive item(s):`);
    findings.forEach(f => report.push(`  - ${f.type}: ${f.match}`));
  }

  return report.join('\n');
}

async function postToReddit({ title, text, subreddit }) {
  if (!REDDIT_CLIENT_ID || !REDDIT_CLIENT_SECRET || !REDDIT_USERNAME || !REDDIT_PASSWORD) {
    return {
      success: false,
      error: 'Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD) not configured in .env'
    };
  }

  try {
    const authString = Buffer.from(`${REDDIT_CLIENT_ID}:${REDDIT_CLIENT_SECRET}`).toString('base64');
    const tokenParams = new URLSearchParams({
      grant_type: 'password',
      username: REDDIT_USERNAME,
      password: REDDIT_PASSWORD
    });

    const tokenRes = await fetch('https://www.reddit.com/api/v1/access_token', {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${authString}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': `OmniPress/0.1.0 by /u/${REDDIT_USERNAME}`
      },
      body: tokenParams
    });

    if (!tokenRes.ok) {
      const err = await tokenRes.text();
      return { success: false, error: `Reddit token error (${tokenRes.status}): ${err}` };
    }

    const tokenData = await tokenRes.json();
    if (!tokenData.access_token) {
      return { success: false, error: `Reddit auth failed: ${JSON.stringify(tokenData)}` };
    }

    const submitParams = new URLSearchParams({
      api_type: 'json',
      kind: 'self',
      sr: subreddit,
      title: title,
      text: text
    });

    const postRes = await fetch('https://oauth.reddit.com/api/submit', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenData.access_token}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': `OmniPress/0.1.0 by /u/${REDDIT_USERNAME}`
      },
      body: submitParams
    });

    const postData = await postRes.json();
    if (postData.json?.errors?.length > 0) {
      return {
        success: false,
        error: `Reddit submit error: ${JSON.stringify(postData.json.errors)}`
      };
    }

    const postUrl = postData.json?.data?.url || `https://reddit.com/r/${subreddit}`;
    return {
      success: true,
      url: postUrl,
      id: postData.json?.data?.id
    };
  } catch (err) {
    return { success: false, error: `Reddit request exception: ${err.message}` };
  }
}

// ==========================================
// Social Media Helpers (Instagram, YouTube, X, Dark Channels)
// ==========================================
function formatInstagramCaption(text, tags = []) {
  let cleaned = (text || '').trim();
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');

  if (tags && tags.length > 0) {
    const formattedTags = tags.map(t => t.startsWith('#') ? t : `#${t.replace(/\s+/g, '')}`).join(' ');
    cleaned = `${cleaned}\n\n.\n.\n${formattedTags}`;
  }

  if (cleaned.length > 2200) {
    cleaned = cleaned.slice(0, 2197) + '...';
  }
  return cleaned;
}

function segmentTwitterThread(text, maxTweetLen = 280) {
  const raw = (text || '').trim();
  if (raw.includes('---')) {
    const segments = raw.split(/\n\s*---\s*\n/).map(s => s.trim()).filter(Boolean);
    if (segments.length > 1) {
      return segments.map((seg, idx) => `${idx + 1}/${segments.length} ${seg}`);
    }
  }

  const tweetTagRegex = /\[(?:TWEET|POST)\s*\d*\]/i;
  if (tweetTagRegex.test(raw)) {
    const segments = raw.split(/\[(?:TWEET|POST)\s*\d*\]/i).map(s => s.trim()).filter(Boolean);
    if (segments.length > 1) {
      return segments.map((seg, idx) => `${idx + 1}/${segments.length} ${seg}`);
    }
  }

  if (raw.length <= maxTweetLen) {
    return [raw];
  }

  const paragraphs = raw.split(/\n\n+/);
  const chunks = [];
  let currentChunk = '';

  for (const p of paragraphs) {
    if ((currentChunk + '\n\n' + p).length <= maxTweetLen) {
      currentChunk = currentChunk ? currentChunk + '\n\n' + p : p;
    } else {
      if (currentChunk) chunks.push(currentChunk);
      if (p.length <= maxTweetLen) {
        currentChunk = p;
      } else {
        const sentences = p.match(/[^.!?]+[.!?]+|\s*[^.!?]+$/g) || [p];
        for (const sent of sentences) {
          if ((currentChunk + ' ' + sent).length <= maxTweetLen) {
            currentChunk = currentChunk ? currentChunk + ' ' + sent.trim() : sent.trim();
          } else {
            if (currentChunk) chunks.push(currentChunk);
            currentChunk = sent.trim();
          }
        }
      }
    }
  }
  if (currentChunk) chunks.push(currentChunk);

  return chunks.map((c, idx) => `${idx + 1}/${chunks.length} ${c}`);
}

function stageYouTubeVideo({
  title,
  description,
  tags = [],
  isShort = false,
  categoryId = '27',
  privacyStatus = 'private',
  mediaUrls = [],
  thumbnailUrl = null,
  scheduleTime = null
}) {
  let cleanTitle = (title || 'Vídeo Sem Título').trim();
  if (isShort && !cleanTitle.toLowerCase().includes('#shorts')) {
    cleanTitle = `${cleanTitle} #Shorts`;
  }
  if (cleanTitle.length > 100) {
    cleanTitle = cleanTitle.slice(0, 97) + '...';
  }

  let formattedDesc = (description || '').trim();
  if (tags && tags.length > 0) {
    const hashTags = tags.slice(0, 5).map(t => t.startsWith('#') ? t : `#${t.replace(/\s+/g, '')}`).join(' ');
    formattedDesc += `\n\n${hashTags}`;
  }

  const now = new Date();
  const yyyy = now.getUTCFullYear().toString();
  const mm = String(now.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(now.getUTCDate()).padStart(2, '0');
  const dateStr = `${yyyy}-${mm}-${dd}`;
  const slug = slugify(cleanTitle) || `yt-${Date.now()}`;

  const baseDir = getMediaStagingDir();
  const targetDir = path.join(baseDir, 'youtube', yyyy, mm);
  fs.mkdirSync(targetDir, { recursive: true });

  const manifest = {
    platform: isShort ? 'youtube_shorts' : 'youtube',
    title: cleanTitle,
    description: formattedDesc,
    tags: tags.map(t => t.replace(/^#/, '')),
    categoryId,
    privacyStatus,
    isShort,
    mediaUrls,
    thumbnailUrl,
    scheduleTime,
    stagedAt: now.toISOString(),
    status: 'staged_draft'
  };

  const filename = `${dateStr}-${slug}.json`;
  const filepath = path.join(targetDir, filename);
  fs.writeFileSync(filepath, JSON.stringify(manifest, null, 2), 'utf8');

  return { filepath, filename, manifest };
}

function prepareDarkScript({
  topic,
  format = 'all',
  tone = 'mystery',
  targetAudience = 'geral'
}) {
  const tones = {
    mystery: {
      mood: 'Enigmático, sombrio e revelador',
      voice: 'pt-BR-AntonioNeural (grave, pausado, tom documental investigativo)',
      bgm: 'Dark Ambient / Drone misterioso com sub-graves (80-90 BPM)',
      pacing: 'Pausas dramáticas a cada 5 segundos'
    },
    wealth: {
      mood: 'Poder, psicologia financeira, segredos da elite',
      voice: 'pt-BR-FabioNeural (firme, articulado, alta autoridade)',
      bgm: 'Cinematic Orchestral / Neo-Classical com piano tenso',
      pacing: 'Dinâmico com números e quebras de crença'
    },
    dramatic: {
      mood: 'Urgente, visceral e cinematográfico',
      voice: 'pt-BR-AntonioNeural (intenso com modulação de perigo)',
      bgm: 'Suspense Cinematic Thriller com percussão crescente',
      pacing: 'Cortes rápidos de 2 a 3 segundos'
    },
    philosophical: {
      mood: 'Estóico, provocador, reflexão profunda',
      voice: 'pt-BR-AntonioNeural (sereno, profundo, compassado)',
      bgm: 'Minimalist Lo-Fi Dark / Ambient Strings',
      pacing: 'Frases curtas com impacto reflexivo'
    }
  };

  const selectedTone = tones[tone] || tones.mystery;
  const cleanTopic = (topic || '').trim();

  const bundle = {
    topic: cleanTopic,
    tone,
    targetAudience,
    audioDirection: selectedTone,
    shortScript: {
      durationSeconds: 55,
      hook_0_3s: `Você NUNCA deveria saber sobre isso... mas a verdade sobre ${cleanTopic} finalmente veio à tona.`,
      retention_3_15s: `A maioria das pessoas acredita na versão que contam por aí. Mas se você analisar os registros confidenciais, algo perturbador não fecha.`,
      development_15_45s: `Nos bastidores, o que realmente aconteceu foi orquestrado em silêncio. Três anomalias foram apagadas dos livros: o sumiço dos relatórios originais, o isolamento dos envolvidos e o padrão que continua se repetindo hoje sem você perceber.`,
      climax_45_50s: `E a pergunta que ninguém quer responder é: quem realmente lucrou com o silêncio desse caso?`,
      cta_50_55s: `Comente sua teoria abaixo e se inscreva antes que derrubem este conteúdo.`
    },
    visualScenePrompts: [
      {
        scene: 1,
        timecode: '00:00 - 00:03',
        description: 'Gancho visual chocante e cinematográfico',
        aiPrompt: `Cinematic 8k, dark moody atmosphere, mysterious silhouette holding classified dossier, dramatic volumetric lighting, foggy background, cold blue and amber tones, photorealistic, 9:16 aspect ratio, ultra-detailed`
      },
      {
        scene: 2,
        timecode: '00:03 - 00:15',
        description: 'Documentos e evidências confidenciais',
        aiPrompt: `Close-up macro of ancient classified parchment papers with redacted black marks, vintage magnifying glass, dark wooden archival desk, eerie candlelight, hyper-detailed textures, 9:16 aspect ratio, photorealistic`
      },
      {
        scene: 3,
        timecode: '00:15 - 00:30',
        description: 'O mecanismo ou local oculto',
        aiPrompt: `Epic wide angle of an underground vault or forgotten monolithic chamber, brutalist architecture, moody dark cinematography, ominous shadows, dust particles in ray of light, photorealistic, 9:16 aspect ratio`
      },
      {
        scene: 4,
        timecode: '00:30 - 00:45',
        description: 'Figuras sombrias e os bastidores',
        aiPrompt: `Dramatic high contrast portrait of powerful shadowy figures around a dimly lit boardroom map, cinematic rim lighting, mysterious tension, 8k resolution, photorealistic, 9:16 aspect ratio`
      },
      {
        scene: 5,
        timecode: '00:45 - 00:55',
        description: 'A pergunta final e o clímax',
        aiPrompt: `Surreal conceptual artwork of a clock ticking backwards inside a shattered hourglass, dark cosmic backdrop, cinematic illumination, award-winning concept art, photorealistic, 9:16 aspect ratio`
      }
    ],
    instagramCarousel: {
      slide1_cover: `O que esconderam sobre: ${cleanTopic} ⚠️`,
      slide2_context: `Durante anos nos disseram apenas o que era conveniente. Mas os registros desclassificados revelam um cenário completamente diferente.`,
      slide3_point1: `1. O primeiro rastro: Documentos e transferências que sumiram no mesmo dia em que o caso veio à tona.`,
      slide4_point2: `2. O padrão: Por que as mesmas organizações tomaram medidas idênticas em segredo absoluto?`,
      slide5_point3: `3. O impacto atual: Como essa decisão moldou diretamente a estrutura que vivemos hoje.`,
      slide6_insight: `Quando você junta os fatos reais, não há espaço para coincidências. Foi tudo calculado.`,
      slide7_cta: `Salve este carrossel para não esquecer e siga a página para os próximos relatórios sem censura.`
    },
    instagramCaption: formatInstagramCaption(
      `O que eles tentaram apagar sobre ${cleanTopic}.\n\nQuando você examina os documentos desclassificados e ignora o ruído da superfície, a verdade se torna inegável.\n\nQual é a sua opinião sobre isso? Deixe seu comentário. 👇`,
      ['darkchannel', 'misterio', 'historiaoculta', 'documentario', 'curiosidades', 'fatoscuriosos', 'investigacao', 'conhecimento']
    ),
    xThread: [
      `1/6 O dossiê proibido sobre ${cleanTopic} que você nunca viu nos noticiários. Uma thread investigativa necessária: 🧵👇`,
      `2/6 A história oficial sempre tentou vender uma versão simples e digerível. Mas quem tem acesso aos arquivos sabe que pontos cruciais foram deliberadamente ignorados.`,
      `3/6 O primeiro indício: relatórios preliminares foram alterados em menos de 24 horas. Testemunhas-chave simplesmente pararam de prestar declarações.`,
      `4/6 Seguindo o fluxo de influência e poder, os mesmos nomes continuam surgindo em posições estratégicas até hoje.`,
      `5/6 Não estamos falando de especulação, mas de congruência factual. Quando você alinha data, hora e interesse, o padrão fica óbvio.`,
      `6/6 Se essa investigação foi útil para você, dê RT no primeiro tweet para apoiar nosso trabalho e siga para mais dossiês confidenciais toda semana.`
    ],
    youtubeMetadata: {
      title: `O Segredo Oculto Sobre ${cleanTopic} (O Que Apagaram da História)`,
      description: `Investigação aprofundada revelando os detalhes e anomalias documentadas sobre ${cleanTopic}.\n\n⏱️ Capítulos:\n00:00 - A Revelação Inicial\n01:10 - Documentos Desaparecidos\n02:35 - O Que Aconteceu nos Bastidores\n04:15 - Consequências Atuais\n05:10 - O Desfecho\n\n🔔 Inscreva-se e ative as notificações para acompanhar novos dossiês.`,
      tags: [cleanTopic, 'misterio', 'documentario dark', 'historia oculta', 'curiosidades', 'segredos revelados', 'canal dark'],
      suggestedThumbnail: `Texto em amarelo: "ELES APAGARAM ISSO?". Imagem de fundo contrastada em preto e dourado com iluminação dramática nos olhos ou no documento central.`
    }
  };

  return bundle;
}

function brainstormChannel({
  niche = 'historia',
  tone = 'mystery',
  targetAudience = 'geral',
  language = 'pt-BR'
}) {
  const cleanNiche = (niche || 'historia').toLowerCase().trim();
  let concepts = [];
  let pillars = [];
  let viralTopics = [];

  if (cleanNiche.includes('hist') || cleanNiche.includes('antig') || cleanNiche.includes('passad') || cleanNiche.includes('guerra')) {
    concepts = [
      {
        name: 'Dossiê Histórico',
        handle: '@dossiehistorico',
        tagline: 'O que os livros oficiais apagaram do passado.',
        ctrAngle: 'Gatilho de segredo de estado e conspiração desclassificada.',
        visualPalette: ['#0A0C10', '#D4AF37', '#8B0000'],
        avatarPrompt: 'Cinematic silhouette of a 19th century archivist examining a glowing ancient dossier, dark moody background, amber rim light, 1:1'
      },
      {
        name: 'Crônicas Ocultas',
        handle: '@cronicasocultas.oficial',
        tagline: 'Fatos reais que parecem pesadelo ou ficção.',
        ctrAngle: 'Gatilho de bizarrice e choque factual.',
        visualPalette: ['#070809', '#C0C0C0', '#4A0E17'],
        avatarPrompt: 'Mysterious antique hourglass with black sand, golden filigree details, dark gothic studio lighting, photorealistic, 1:1'
      },
      {
        name: 'O Passado Redigido',
        handle: '@passadoredigido',
        tagline: 'Documentos confidenciais que você nunca deveria ler.',
        ctrAngle: 'Gatilho de censura e conhecimento proibido.',
        visualPalette: ['#111215', '#E63946', '#F1FAEE'],
        avatarPrompt: 'Top-secret archival stamp with redacted black marker bars over a historical sepia portrait, high contrast, 1:1'
      },
      {
        name: 'Sombras da História',
        handle: '@sombrasdahistoria',
        tagline: 'As decisões mais sombrias que moldaram o mundo moderno.',
        ctrAngle: 'Gatilho de poder, decisões secretas de bastidores.',
        visualPalette: ['#050505', '#DAA520', '#1C2541'],
        avatarPrompt: 'Shadowy figures in vintage military trench coats in a dimly lit rainy alleyway, atmospheric volumetric lighting, 1:1'
      },
      {
        name: 'Arquivos do Tempo',
        handle: '@arquivosdotempo',
        tagline: 'Investigação profunda das maiores anomalias da humanidade.',
        ctrAngle: 'Gatilho investigativo e documental solene.',
        visualPalette: ['#0D1117', '#C9D1D9', '#58A6FF'],
        avatarPrompt: 'Macro shot of an ancient brass astrolabe mechanism surrounded by forgotten manuscripts, cinematic golden hour lighting, 1:1'
      }
    ];

    pillars = [
      {
        pillar: '1. Documentos Desclassificados & Conspirações Reais',
        description: 'Operações militares secretas, arquivos de inteligência liberados após décadas e fraudes históricas desmascaradas.'
      },
      {
        pillar: '2. Batalhas Bizarras & O Pior Erro Militar',
        description: 'Conflitos onde generais perderam tudo por arrogância, blefes lendários e exércitos que lutaram contra si mesmos.'
      },
      {
        pillar: '3. Anomalias & Mistérios Não Resolvidos',
        description: 'Civilizações esquecidas, surtos coletivos bizarros e artefatos arqueológicos fora do seu tempo.'
      }
    ];

    viralTopics = [
      {
        id: 1,
        title: 'O Exército Fantasma da Segunda Guerra',
        hook_0_3s: 'Você sabia que os EUA venceram uma das batalhas mais decisivas da história usando tanques de borracha e caixas de som?',
        curiosityLoop: 'O 23º Quartel-General de Tropas Especiais enganou 20 divisões alemãs com cenografia de Hollywood.',
        format: 'Shorts / Reels (9:16) + X Thread'
      },
      {
        id: 2,
        title: 'A Dança de São Vito de 1518',
        hook_0_3s: 'Em julho de 1518, uma mulher começou a dançar na rua. Em 30 dias, 400 pessoas dançavam sem conseguir parar até o coração explodir.',
        curiosityLoop: 'A histeria coletiva de Estrasburgo que médicos e padres tentaram conter com música ao vivo.',
        format: 'Shorts / Reels (9:16) + Instagram Carrossel'
      },
      {
        id: 3,
        title: 'A Batalha de Karánsebes (O Exército que se Autodestruiu)',
        hook_0_3s: 'Esta foi a batalha mais bizarra de todos os tempos: um exército perdeu 10.000 soldados sem que houvesse um único inimigo por perto.',
        curiosityLoop: 'Uma briga por barris de aguardente causou fogo amigo generalizado no exército austríaco.',
        format: 'Shorts / Reels (9:16) + Artigo'
      },
      {
        id: 4,
        title: 'O Submarino B-59 e o Homem que Salvou o Mundo',
        hook_0_3s: 'Em outubro de 1962, a Terceira Guerra Mundial foi evitada pelo voto solitário de um único oficial soviético.',
        curiosityLoop: 'Vasili Arkhipov se recusou a autorizar o lançamento de um torpedo nuclear a 50 metros de profundidade.',
        format: 'Shorts / Reels (9:16) + X Thread'
      },
      {
        id: 5,
        title: 'O Mecanismo de Anticítera',
        hook_0_3s: 'Mergulhadores encontraram um computador analógico da Grécia Antiga no fundo do mar. Como ele existiu há 2.000 anos?',
        curiosityLoop: 'Engrenagens de bronze capazes de calcular eclipses que desafiam a linha do tempo tecnológica.',
        format: 'Shorts / Reels (9:16) + Carrossel'
      },
      {
        id: 6,
        title: 'A Cidade Subterrânea de Derinkuyu',
        hook_0_3s: 'Em 1963, um homem derrubou a parede de sua casa na Turquia e descobriu uma metrópole subterrânea para 20.000 pessoas.',
        curiosityLoop: 'Túneis de 85 metros de profundidade com ventilação perfeita e portas de pedra inexpugnáveis.',
        format: 'Shorts / Reels (9:16)'
      },
      {
        id: 7,
        title: 'O Mistério da Expedição Franklin',
        hook_0_3s: 'Dois navios modernos e 129 marinheiros entraram no Ártico em 1845. Nenhum deles retornou com vida.',
        curiosityLoop: 'Envenenamento por chumbo nas latas de comida e registros de canibalismo congelados no gelo.',
        format: 'Shorts / Reels (9:16) + Artigo Completo'
      },
      {
        id: 8,
        title: 'O Veneno dos Médici',
        hook_0_3s: 'Como a família mais poderosa da Renascença eliminava cardeais e duques em banquetes sem deixar vestígios.',
        curiosityLoop: 'As receitas químicas de arsênico e belladonna disfarçadas em vinhos da Toscana.',
        format: 'Instagram Carrossel + X Thread'
      },
      {
        id: 9,
        title: 'A Batalha de Pelúsio (A Tática dos Gatos)',
        hook_0_3s: 'Os persas conquistaram o Egito usando gatos amarrados aos seus escudos porque sabiam que os egípcios não atacariam animais sagrados.',
        curiosityLoop: 'Uma das maiores guerras psicológicas da antiguidade.',
        format: 'Shorts / Reels (9:16)'
      },
      {
        id: 10,
        title: 'O Julgamento do Cadáver (O Sínodo do Cadáver)',
        hook_0_3s: 'Em 897, a Igreja exumou o corpo de um Papa falecido há 9 meses, vestiu-o com roupas papais e colocou-o em julgamento.',
        curiosityLoop: 'O Papa Estêvão VI gritando com o cadáver do Papa Formoso no tribunal de Roma.',
        format: 'Shorts / Reels (9:16) + Carrossel'
      }
    ];
  } else {
    concepts = [
      {
        name: `${cleanNiche.toUpperCase()} Revelado`,
        handle: `@${slugify(cleanNiche)}.revelado`,
        tagline: `Os segredos e bastidores que ninguém te conta sobre ${cleanNiche}.`,
        ctrAngle: 'Gatilho de revelação de bastidores.',
        visualPalette: ['#0A0C10', '#3B82F6', '#F3F4F6']
      },
      {
        name: `Dossiê ${cleanNiche.toUpperCase()}`,
        handle: `@dossie.${slugify(cleanNiche)}`,
        tagline: `Investigação aprofundada e fatos sem filtro.`,
        ctrAngle: 'Gatilho de autoridade documental.',
        visualPalette: ['#111827', '#E5E7EB', '#EF4444']
      }
    ];
    pillars = [
      { pillar: '1. O que não te contam', description: 'Casos e anomalias ocultas.' },
      { pillar: '2. Histórias de impacto', description: 'Narrativas de alta retenção.' },
      { pillar: '3. Análise crítica', description: 'Visão de longo prazo e conclusões.' }
    ];
    viralTopics = [
      { id: 1, title: `O maior segredo sobre ${cleanNiche}`, hook_0_3s: `A maioria das pessoas ignora esse fato crucial...`, format: 'Shorts / Reels (9:16)' }
    ];
  }

  return {
    niche: cleanNiche,
    tone,
    targetAudience,
    channelConcepts: concepts,
    contentPillars: pillars,
    viralTopicsBacklog: viralTopics,
    productionSpecs: {
      audioVoice: 'pt-BR-AntonioNeural (Edge-TTS gravado com tom documental solene)',
      audioBgm: 'Dark Ambient / Drone com sub-graves em 80-90 BPM',
      visualAiPrompts: 'Cinematic 8k, dark moody atmosphere, historical archival textures, volumetric amber rim lighting, 9:16 aspect ratio',
      recommendedPacing: 'Cortes visuais a cada 3 a 5 segundos, pausas dramáticas na locução'
    }
  };
}

function runMediaScript(args) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(PROJECT_ROOT, 'scripts', 'generate_dark_media.py');
    const venvPython = path.join(PROJECT_ROOT, '.venv', 'bin', 'python');
    const uvPath = path.join(os.homedir(), '.local', 'bin', 'uv');
    const hasUv = fs.existsSync(uvPath) || (process.env.PATH && process.env.PATH.includes('uv'));
    let binary = 'python3';
    let execArgs = [scriptPath, ...args];

    if (fs.existsSync(venvPython)) {
      binary = venvPython;
      execArgs = [scriptPath, ...args];
    } else if (hasUv) {
      binary = fs.existsSync(uvPath) ? uvPath : 'uv';
      execArgs = ['run', '-q', 'python', scriptPath, ...args];
    }

    execFile(binary, execArgs, { cwd: PROJECT_ROOT, maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) {
        if (binary !== 'python3') {
          execFile('python3', [scriptPath, ...args], { cwd: PROJECT_ROOT, maxBuffer: 10 * 1024 * 1024 }, (err2, stdout2, stderr2) => {
            if (err2) return reject(new Error(stderr2 || stderr || err2.message));
            try {
              resolve(JSON.parse(stdout2.trim()));
            } catch (e) {
              resolve({ success: true, rawOutput: stdout2.trim() });
            }
          });
          return;
        }
        return reject(new Error(stderr || err.message));
      }
      try {
        const parsed = JSON.parse(stdout.trim());
        resolve(parsed);
      } catch (e) {
        resolve({ success: true, rawOutput: stdout.trim() });
      }
    });
  });
}

async function generateSpeech({ text, voice = 'pt-BR-AntonioNeural', outputFilename = null }) {
  const now = Date.now();
  const filename = outputFilename || `speech-${now}.mp3`;
  const outPath = path.join(PROJECT_ROOT, 'media', 'output', filename);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const res = await runMediaScript([
    '--text', text,
    '--voice', voice,
    '--output', outPath,
    '--audio-only',
    '--json'
  ]);
  return res;
}

async function renderDarkVideo({
  text = null,
  audioPath = null,
  imagePaths = [],
  outputFilename = null,
  aspectRatio = '9:16',
  voice = 'pt-BR-AntonioNeural'
}) {
  const now = Date.now();
  const filename = outputFilename || `video-${now}.mp4`;
  const outPath = path.join(PROJECT_ROOT, 'media', 'output', filename);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const args = [
    '--output', outPath,
    '--ratio', aspectRatio,
    '--voice', voice,
    '--json'
  ];
  if (text) args.push('--text', text);
  if (audioPath) args.push('--audio-path', audioPath);
  if (imagePaths && imagePaths.length > 0) {
    args.push('--images', ...imagePaths);
  }

  const res = await runMediaScript(args);
  return res;
}

async function queueMediaPost({
  title = null,
  caption,
  platforms = ['instagram', 'x'],
  mediaType = 'image',
  mediaUrls = [],
  tags = [],
  thumbnailUrl = null,
  scheduleTime = null,
  sanitize = true
}) {
  let processedCaption = caption || '';
  let processedTitle = title || '';
  let findings = [];

  if (sanitize) {
    const resCap = sanitizeText(processedCaption);
    processedCaption = resCap.sanitized;
    findings = findings.concat(resCap.findings);

    if (processedTitle) {
      const resTitle = sanitizeText(processedTitle);
      processedTitle = resTitle.sanitized;
      findings = findings.concat(resTitle.findings);
    }
  }

  const results = [];
  const normalizedPlatforms = platforms.map(p => p.toLowerCase().trim());

  // 1. Instagram Handling
  if (normalizedPlatforms.includes('instagram') || normalizedPlatforms.includes('ig') || normalizedPlatforms.includes('all')) {
    if (!mediaUrls || mediaUrls.length === 0) {
      results.push('⚠️ Aviso Instagram: O Instagram exige ao menos uma imagem ou vídeo (media_urls). Adicione uma URL ou caminho de arquivo.');
    }
    const igCaption = formatInstagramCaption(processedCaption, tags);
    if (BUFFER_ACCESS_TOKEN && BUFFER_INSTAGRAM_PROFILE_ID) {
      try {
        const formData = new URLSearchParams();
        formData.append('access_token', BUFFER_ACCESS_TOKEN);
        formData.append('profile_ids[]', BUFFER_INSTAGRAM_PROFILE_ID);
        formData.append('text', igCaption);
        formData.append('top', 'false');
        formData.append('now', 'false');
        if (scheduleTime) formData.append('scheduled_at', scheduleTime);
        if (mediaUrls && mediaUrls.length > 0) formData.append('media[link]', mediaUrls[0]);

        const response = await fetch('https://api.bufferapp.com/1/updates/create.json', {
          method: 'POST',
          body: formData
        });
        if (response.ok) {
          results.push(`✅ Queued to Instagram via Buffer (Profile: ${BUFFER_INSTAGRAM_PROFILE_ID}) as Draft.`);
        } else {
          results.push(`⚠️ Buffer Instagram error (${response.status}): ${await response.text()}`);
        }
      } catch (err) {
        results.push(`⚠️ Buffer Instagram request failed: ${err.message}`);
      }
    } else {
      results.push(
        '📷 Instagram Draft Formatted (Configure BUFFER_INSTAGRAM_PROFILE_ID in .env for direct sync):\n' +
        '```text\n' + igCaption + '\n```' +
        (mediaUrls.length > 0 ? `\nAttached media: ${mediaUrls.join(', ')}` : '')
      );
    }
  }

  // 2. YouTube / YouTube Shorts Staging
  const isYtShort = normalizedPlatforms.includes('youtube_shorts') || normalizedPlatforms.includes('shorts') || mediaType === 'short';
  const isYtLong = normalizedPlatforms.includes('youtube') || normalizedPlatforms.includes('yt');
  if (isYtShort || isYtLong || normalizedPlatforms.includes('all')) {
    const ytStaged = stageYouTubeVideo({
      title: processedTitle || (processedCaption.split('\n')[0] || 'Novo Vídeo Dark'),
      description: processedCaption,
      tags,
      isShort: isYtShort,
      mediaUrls,
      thumbnailUrl,
      scheduleTime
    });

    results.push(
      `🎬 YouTube (${isYtShort ? 'Shorts' : 'Long-form'}) Staged:\n` +
      `  - File: \`${ytStaged.filepath}\`\n` +
      `  - Title: "${ytStaged.manifest.title}"\n` +
      `  - Tags: ${JSON.stringify(ytStaged.manifest.tags)}`
    );

    const ytWebhook = YOUTUBE_WEBHOOK_URL || OMNIPRESS_WEBHOOK_URL;
    if (ytWebhook) {
      const whRes = await dispatchWebhook('youtube_video_staged', ytStaged.manifest);
      if (whRes.success) {
        results.push(`  ✓ Event dispatched to YouTube upload pipeline.`);
      }
    }
  }

  // 3. X (Twitter) Dispatch (Thread-aware)
  if (normalizedPlatforms.includes('x') || normalizedPlatforms.includes('twitter') || normalizedPlatforms.includes('all')) {
    const threadTweets = segmentTwitterThread(processedCaption);
    if (BUFFER_ACCESS_TOKEN && BUFFER_X_PROFILE_ID) {
      try {
        const formData = new URLSearchParams();
        formData.append('access_token', BUFFER_ACCESS_TOKEN);
        formData.append('profile_ids[]', BUFFER_X_PROFILE_ID);
        formData.append('text', threadTweets[0]);
        formData.append('top', 'false');
        formData.append('now', 'false');
        if (scheduleTime) formData.append('scheduled_at', scheduleTime);
        if (mediaUrls && mediaUrls.length > 0) formData.append('media[link]', mediaUrls[0]);

        const response = await fetch('https://api.bufferapp.com/1/updates/create.json', {
          method: 'POST',
          body: formData
        });
        if (response.ok) {
          results.push(`✅ Queued Tweet 1/${threadTweets.length} to X via Buffer as Draft.`);
        } else {
          results.push(`⚠️ Buffer X error (${response.status}): ${await response.text()}`);
        }
      } catch (err) {
        results.push(`⚠️ Buffer X request failed: ${err.message}`);
      }
    } else {
      results.push(
        `🐦 X (Twitter) Thread Formatted (${threadTweets.length} tweet(s)):\n` +
        threadTweets.map((tw, i) => `--- Tweet ${i + 1} ---\n${tw}`).join('\n\n')
      );
    }
  }

  // 4. Threads Dispatch
  if (normalizedPlatforms.includes('threads')) {
    if (BUFFER_ACCESS_TOKEN && BUFFER_THREADS_PROFILE_ID) {
      try {
        const formData = new URLSearchParams();
        formData.append('access_token', BUFFER_ACCESS_TOKEN);
        formData.append('profile_ids[]', BUFFER_THREADS_PROFILE_ID);
        formData.append('text', processedCaption);
        formData.append('top', 'false');
        formData.append('now', 'false');
        if (scheduleTime) formData.append('scheduled_at', scheduleTime);
        if (mediaUrls && mediaUrls.length > 0) formData.append('media[link]', mediaUrls[0]);

        const response = await fetch('https://api.bufferapp.com/1/updates/create.json', {
          method: 'POST',
          body: formData
        });
        if (response.ok) results.push(`✅ Queued to Threads via Buffer as Draft.`);
      } catch (err) {
        results.push(`⚠️ Threads error: ${err.message}`);
      }
    } else {
      results.push(`🧵 Threads Draft Formatted:\n\`\`\`text\n${processedCaption}\n\`\`\``);
    }
  }

  // 5. Webhook Dispatch
  if (OMNIPRESS_WEBHOOK_URL) {
    await dispatchWebhook('media_post_queued', {
      title: processedTitle,
      caption: processedCaption,
      platforms,
      mediaType,
      mediaUrls,
      tags,
      thumbnailUrl,
      scheduleTime
    });
    results.push(`📡 Dispatched rich media post event to Webhook.`);
  }

  if (findings.length > 0) {
    results.push(`🔒 Masked ${findings.length} sensitive item(s) across title and caption.`);
  }

  return results.join('\n\n');
}

async function queuePost({ text, platforms = ['linkedin'], title = null, mediaUrls = [], scheduleTime = null, sanitize = true }) {
  let processedText = text;
  let findings = [];

  if (sanitize) {
    const res = sanitizeText(text);
    processedText = res.sanitized;
    findings = res.findings;
  }

  const results = [];
  const normalizedPlatforms = platforms.map(p => p.toLowerCase().trim());

  // Check Instagram media requirement
  if ((normalizedPlatforms.includes('instagram') || normalizedPlatforms.includes('ig')) && (!mediaUrls || mediaUrls.length === 0)) {
    results.push('⚠️ Aviso Instagram: O Instagram exige ao menos uma imagem ou vídeo.');
  }

  // 1. Buffer Dispatch (LinkedIn, X, Threads, Instagram)
  if (BUFFER_ACCESS_TOKEN && (BUFFER_LINKEDIN_PROFILE_ID || BUFFER_X_PROFILE_ID || BUFFER_THREADS_PROFILE_ID || BUFFER_INSTAGRAM_PROFILE_ID)) {
    const profileIds = [];
    if ((normalizedPlatforms.includes('linkedin') || normalizedPlatforms.includes('all')) && BUFFER_LINKEDIN_PROFILE_ID) {
      profileIds.push(BUFFER_LINKEDIN_PROFILE_ID);
    }
    if ((normalizedPlatforms.includes('x') || normalizedPlatforms.includes('twitter') || normalizedPlatforms.includes('all')) && BUFFER_X_PROFILE_ID) {
      profileIds.push(BUFFER_X_PROFILE_ID);
    }
    if ((normalizedPlatforms.includes('threads') || normalizedPlatforms.includes('all')) && BUFFER_THREADS_PROFILE_ID) {
      profileIds.push(BUFFER_THREADS_PROFILE_ID);
    }
    if ((normalizedPlatforms.includes('instagram') || normalizedPlatforms.includes('ig') || normalizedPlatforms.includes('all')) && BUFFER_INSTAGRAM_PROFILE_ID) {
      profileIds.push(BUFFER_INSTAGRAM_PROFILE_ID);
    }

    if (profileIds.length > 0) {
      try {
        const formData = new URLSearchParams();
        formData.append('access_token', BUFFER_ACCESS_TOKEN);
        profileIds.forEach(id => formData.append('profile_ids[]', id));
        formData.append('text', processedText);
        formData.append('top', 'false');
        formData.append('now', 'false'); // Always draft queue
        if (scheduleTime) formData.append('scheduled_at', scheduleTime);
        if (mediaUrls && mediaUrls.length > 0) formData.append('media[link]', mediaUrls[0]);

        const response = await fetch('https://api.bufferapp.com/1/updates/create.json', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          results.push(`✅ Queued to Buffer for ${platforms.join(', ')} (${profileIds.length} profile(s)) as Draft.`);
        } else {
          const errText = await response.text();
          results.push(`⚠️ Buffer API error (${response.status}): ${errText}`);
        }
      } catch (err) {
        results.push(`⚠️ Buffer request failed: ${err.message}`);
      }
    }
  }

  // 2. Direct Reddit Dispatch
  const redditPlatform = normalizedPlatforms.find(p => p === 'reddit' || p.startsWith('reddit:'));
  if (redditPlatform) {
    const targetSub = redditPlatform.includes(':')
      ? redditPlatform.split(':')[1].trim()
      : REDDIT_DEFAULT_SUBREDDIT;

    let postTitle = title;
    let postBody = processedText;
    if (!postTitle) {
      const lines = processedText.trim().split('\n');
      postTitle = lines[0].replace(/^[#* \t]+/, '').trim();
      if (postTitle.length > 250) postTitle = postTitle.slice(0, 247) + '...';
      postBody = lines.slice(1).join('\n').trim() || processedText;
    }

    const redditRes = await postToReddit({
      title: postTitle,
      text: postBody,
      subreddit: targetSub
    });

    if (redditRes.success) {
      results.push(`✅ Published to Reddit r/${targetSub}: ${redditRes.url}`);
    } else {
      results.push(`⚠️ Reddit notice: ${redditRes.error}`);
    }
  }

  // 3. YouTube Staging Dispatch (if youtube or shorts requested)
  if (normalizedPlatforms.includes('youtube') || normalizedPlatforms.includes('youtube_shorts') || normalizedPlatforms.includes('shorts')) {
    const isShort = normalizedPlatforms.includes('youtube_shorts') || normalizedPlatforms.includes('shorts');
    const ytStaged = stageYouTubeVideo({
      title: title || processedText.split('\n')[0],
      description: processedText,
      tags: [],
      isShort,
      mediaUrls,
      scheduleTime
    });
    results.push(`🎬 Staged YouTube (${isShort ? 'Shorts' : 'Long'}) metadata at \`${ytStaged.filepath}\``);
  }

  // 4. Webhook Dispatch
  if (OMNIPRESS_WEBHOOK_URL) {
    const whResult = await dispatchWebhook('social_post_queued', {
      text: processedText,
      platforms,
      mediaUrls,
      scheduleTime,
      draft: true
    });
    if (whResult.success) {
      results.push(`✅ Dispatched event to Webhook pipeline.`);
    } else {
      results.push(`⚠️ Webhook error: ${whResult.error}`);
    }
  }

  // 5. Fallback when no keys configured
  const hasConfiguredService = BUFFER_ACCESS_TOKEN || REDDIT_CLIENT_ID || OMNIPRESS_WEBHOOK_URL;
  if (!hasConfiguredService) {
    // If multiple tweets or thread formatting, show threaded view
    if (normalizedPlatforms.includes('x') || normalizedPlatforms.includes('twitter')) {
      const threadTweets = segmentTwitterThread(processedText);
      results.push(
        '🐦 X (Twitter) Content Formatted:\n' +
        threadTweets.map((t, i) => `--- Tweet ${i + 1} ---\n${t}`).join('\n\n')
      );
    } else {
      results.push(
        'ℹ️ No external provider configured in `.env` (BUFFER_ACCESS_TOKEN, REDDIT_CLIENT_ID, or OMNIPRESS_WEBHOOK_URL).\n' +
        'Content formatted and de-identified successfully. Ready for copy-paste:\n\n' +
        '```text\n' + processedText + '\n```'
      );
    }
  }

  if (findings.length > 0) {
    results.push(`🔒 Masked ${findings.length} sensitive item(s) prior to queuing.`);
  }

  return results.join('\n');
}

async function dispatchWebhook(eventType, payload) {
  if (!OMNIPRESS_WEBHOOK_URL) return { success: false, error: 'No URL configured' };

  const body = JSON.stringify({
    event: eventType,
    source: 'omnipress-mcp',
    timestamp: new Date().toISOString(),
    data: payload
  });

  const headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'OmniPress-MCP/0.1.0'
  };

  if (OMNIPRESS_WEBHOOK_SECRET) {
    const hmac = crypto.createHmac('sha256', OMNIPRESS_WEBHOOK_SECRET);
    hmac.update(body);
    headers['X-OmniPress-Signature'] = hmac.digest('hex');
  }

  try {
    const res = await fetch(OMNIPRESS_WEBHOOK_URL, {
      method: 'POST',
      headers,
      body
    });
    return { success: res.ok, status: res.status };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

function listRecentArticles(limit = 5) {
  const baseDir = getArticlesDir();
  if (!fs.existsSync(baseDir)) {
    return 'No articles directory found.';
  }

  function getMarkdownFiles(dir) {
    let files = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files = files.concat(getMarkdownFiles(fullPath));
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        const stats = fs.statSync(fullPath);
        files.push({ name: entry.name, path: fullPath, mtime: stats.mtime, size: stats.size });
      }
    }
    return files;
  }

  const allFiles = getMarkdownFiles(baseDir);
  allFiles.sort((a, b) => b.mtime - a.mtime);
  const selected = allFiles.slice(0, limit);

  if (selected.length === 0) {
    return 'No articles archived yet.';
  }

  const lines = [`📚 Recent Articles (${selected.length}):`];
  selected.forEach(f => {
    lines.push(`- **${f.name}** (${f.size} bytes) — Modified: ${f.mtime.toISOString()}`);
  });
  return lines.join('\n');
}

// ==========================================
// MCP Protocol Constants & Tool Annotations
// ==========================================
const MCP_TOOL_ANNOTATIONS = {
  omnipress_publish_article: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: false
  },
  omnipress_queue_post: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: true
  },
  omnipress_inspect_content: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false
  },
  omnipress_list_articles: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false
  },
  omnipress_queue_media_post: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: true
  },
  omnipress_prepare_dark_script: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false
  },
  omnipress_brainstorm_channel: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false
  },
  omnipress_generate_speech: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: false
  },
  omnipress_render_dark_video: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: false
  }
};

// ==========================================
// MCP JSON-RPC 2.0 Protocol Handler
// ==========================================
const TOOLS_DEFINITIONS = [
  {
    name: 'omnipress_publish_article',
    title: 'Publish and Archive Article',
    description: `Saves a complete, publication-ready long-form article to the local archive with YAML frontmatter (for Substack, Jusbrasil, Medium, or static blog) and optional event dispatch.

Use when:
- Archiving a completed markdown article with structured frontmatter metadata.
- Publishing long-form thought leadership, legal tech, or tax analysis articles.
- Ensuring content is checked and de-identified against CNJ court process numbers, CPFs, CNPJs, and personal emails before persistence.

Do NOT use when:
- Queuing short social media updates or micro-posts (use omnipress_queue_post instead).
- Only checking for sensitive PII without writing files (use omnipress_inspect_content instead).

Returns:
- Formatted confirmation with filename, full storage path, category/tags, and detailed log of any sanitized privacy items.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_publish_article,
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', minLength: 1, maxLength: 300, description: 'Article title' },
        content_markdown: { type: 'string', minLength: 1, description: 'Complete article body in GitHub-flavored Markdown' },
        category: {
          type: 'string',
          enum: ['technology', 'tributario', 'pericia', 'govtech', 'general'],
          description: 'Topic category (technology, tributario, pericia, govtech, general)'
        },
        tags: { type: 'array', items: { type: 'string' }, description: 'Array of keyword tags for categorization' },
        author: { type: 'string', description: 'Author name (default OmniPress)' },
        sanitize: { type: 'boolean', description: 'Whether to sanitize court numbers and PII (default true)' }
      },
      required: ['title', 'content_markdown']
    }
  },
  {
    name: 'omnipress_queue_post',
    title: 'Queue Social Post or Thread',
    description: `Queues a post, thread segment, or social announcement to distribution channels (LinkedIn, X/Twitter, Threads via Buffer, or Reddit) in draft/review mode.

Use when:
- Scheduling or queuing social media posts for human review or automated publishing.
- Distributing snippets, summaries, or threads derived from long-form articles.
- Targeting specific platforms such as LinkedIn, Threads, X, or a Reddit subreddit.

Do NOT use when:
- Storing long-form articles with frontmatter locally (use omnipress_publish_article instead).
- Running a non-publishing privacy check (use omnipress_inspect_content instead).

Returns:
- Dispatch status report indicating successful queuing across configured providers (Buffer, Reddit, Webhook) or formatted draft fallback with sanitization notices.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_queue_post,
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', minLength: 1, description: 'Post text or thread segment' },
        platforms: {
          type: 'array',
          items: { type: 'string' },
          description: 'Target platforms: ["linkedin"], ["x"], ["threads"], ["reddit:subreddit_name"], or ["all"]'
        },
        title: { type: 'string', description: 'Optional post title (used for Reddit or headline feeds)' },
        media_urls: { type: 'array', items: { type: 'string' }, description: 'Optional media URLs or links' },
        schedule_time: { type: 'string', description: 'Optional ISO timestamp or schedule format' },
        sanitize: { type: 'boolean', description: 'Whether to sanitize sensitive IDs before queuing (default true)' }
      },
      required: ['text']
    }
  },
  {
    name: 'omnipress_inspect_content',
    title: 'Inspect Content for PII and Legal IDs',
    description: `Pre-flight compliance scan that analyzes draft content for Brazilian lawsuit numbers (CNJ), tax IDs (CPF/CNPJ), personal emails, and phone numbers without modifying or publishing content.

Use when:
- Auditing draft text for LGPD compliance, judicial confidentiality (segredo de justiça), or privacy leaks before publishing.
- Verifying if content requires anonymization or de-identification.

Do NOT use when:
- Saving the article to disk (use omnipress_publish_article instead).
- Queuing social posts (use omnipress_queue_post instead).

Returns:
- Summary report stating whether the text is clean, or a detailed itemized list of detected sensitive matches with their classification types.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_inspect_content,
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', minLength: 1, description: 'Draft text to scan for sensitive PII or legal process IDs' }
      },
      required: ['text']
    }
  },
  {
    name: 'omnipress_list_articles',
    title: 'List Archived Articles',
    description: `Retrieves metadata of recently archived long-form articles from the local repository directory.

Use when:
- Discovering existing articles, file paths, and modification dates.
- Verifying recently published drafts or checking past article slugs.

Do NOT use when:
- Inspecting text content for privacy leaks (use omnipress_inspect_content instead).
- Publishing new content (use omnipress_publish_article instead).

Returns:
- Formatted list of recent articles including filename, file size in bytes, and ISO-8601 modification timestamp.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_list_articles,
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'integer', minimum: 1, maximum: 100, default: 5, description: 'Maximum number of articles to return (1-100, default 5)' }
      }
    }
  },
  {
    name: 'omnipress_prepare_dark_script',
    title: 'Prepare Dark Channel Script and Production Bundle',
    description: `Generates a high-retention viral dark channel script, scene-by-scene AI image prompts, voice narration specs (TTS), Instagram carousel/caption, X viral thread, and YouTube SEO metadata.

Use when:
- Creating a complete production bundle for dark channels across YouTube, Instagram, X (Twitter), and TikTok.
- Generating scene-by-scene visual image prompts for AI generators.
- Formatting YouTube SEO tags, descriptions with timestamps, and Instagram carousel copy.

Do NOT use when:
- Queuing media or posts directly to distribution channels (use omnipress_queue_media_post or omnipress_queue_post).

Returns:
- Complete production bundle containing short script, visual prompts, audio specs, Instagram carousel, X thread, and YouTube metadata.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_prepare_dark_script,
    inputSchema: {
      type: 'object',
      properties: {
        topic: { type: 'string', minLength: 1, description: 'Core topic, mystery, historical anomaly, or theme' },
        format: {
          type: 'string',
          enum: ['all', 'short', 'video', 'carousel', 'thread'],
          default: 'all',
          description: 'Format to generate (all, short, video, carousel, thread)'
        },
        tone: {
          type: 'string',
          enum: ['mystery', 'wealth', 'dramatic', 'philosophical'],
          default: 'mystery',
          description: 'Tone style: mystery, wealth, dramatic, philosophical'
        },
        target_audience: { type: 'string', default: 'geral', description: 'Target audience descriptor' }
      },
      required: ['topic']
    }
  },
  {
    name: 'omnipress_queue_media_post',
    title: 'Queue Rich Media Post (Instagram, YouTube, X, Threads)',
    description: `Queues rich media content (Images, Carousels, Video Reels, YouTube Shorts) to Instagram, YouTube, X/Twitter, and Threads with platform-specific formatting and asset staging.

Use when:
- Scheduling or staging video content (YouTube Shorts, YouTube long-form, Instagram Reels).
- Publishing image carousels to Instagram or media posts to X with attachments.
- Dispatching video upload jobs to staging and webhooks.

Do NOT use when:
- Storing long-form text articles (use omnipress_publish_article).
- Just generating the script without queuing (use omnipress_prepare_dark_script).

Returns:
- Multi-platform status report confirming Instagram formatting/queue, YouTube staging path, X thread breakdown, and webhook dispatches.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_queue_media_post,
    inputSchema: {
      type: 'object',
      properties: {
        caption: { type: 'string', minLength: 1, description: 'Post caption, script, or description' },
        platforms: {
          type: 'array',
          items: { type: 'string' },
          description: 'Target platforms: ["instagram"], ["youtube_shorts"], ["youtube"], ["x"], ["threads"], ["all"]'
        },
        title: { type: 'string', description: 'Optional post or video title (vital for YouTube)' },
        media_urls: { type: 'array', items: { type: 'string' }, description: 'Array of media URLs or local file paths (image/video)' },
        media_type: {
          type: 'string',
          enum: ['image', 'carousel', 'video', 'short'],
          default: 'image',
          description: 'Media format type: image, carousel, video, short'
        },
        tags: { type: 'array', items: { type: 'string' }, description: 'Array of keyword tags or hashtags' },
        thumbnail_url: { type: 'string', description: 'Thumbnail/cover URL or local path for video' },
        schedule_time: { type: 'string', description: 'Optional ISO schedule time' },
        sanitize: { type: 'boolean', description: 'Whether to sanitize sensitive IDs before queuing (default true)' }
      },
      required: ['caption', 'platforms']
    }
  },
  {
    name: 'omnipress_brainstorm_channel',
    title: 'Brainstorm Channel Strategy and Backlog',
    description: `Generates high-retention channel concepts, psychological CTR names, 3 core content pillars, and a backlog of 10 viral video topics with tested 0-3s scroll-stop hooks for dark or niche channels (History, Tech, Geopolitics, Finance).

Use when:
- Bootstrapping or brainstorming a new content channel on YouTube, Instagram, TikTok, or X.
- Looking for viral topic ideas with proven high-retention hooks and psychological curiosity loops.
- Defining brand positioning, visual palettes, and neural TTS voice personas.

Do NOT use when:
- Writing a full script for an already chosen topic (use omnipress_prepare_dark_script instead).

Returns:
- JSON bundle with 5 channel name concepts, 3 content pillars, 10 viral backlog topics with hooks, and audio/visual production specs.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_brainstorm_channel,
    inputSchema: {
      type: 'object',
      properties: {
        niche: {
          type: 'string',
          description: 'Channel niche or theme (e.g., historia, misterios, geopolitica, tecnologia, financas)',
          default: 'historia'
        },
        tone: {
          type: 'string',
          enum: ['mystery', 'documentary', 'dramatic', 'philosophical'],
          default: 'mystery',
          description: 'Narrative tone and aesthetic style'
        },
        target_audience: {
          type: 'string',
          description: 'Intended audience (default "geral")',
          default: 'geral'
        },
        language: {
          type: 'string',
          description: 'Primary channel language code (default "pt-BR")',
          default: 'pt-BR'
        }
      }
    }
  },
  {
    name: 'omnipress_generate_speech',
    title: 'Generate Neural Speech Audio (TTS)',
    description: `Synthesizes natural, high-definition neural narration audio (Edge-TTS) for Dark Channels, Reels, Shorts, and long-form storytelling.

Use when:
- Converting script narrations into immersive MP3 voice files.
- Producing documentary voiceovers with grave, solemn pacing (pt-BR-AntonioNeural).

Do NOT use when:
- Only formatting text or scripts (use omnipress_prepare_dark_script instead).

Returns:
- Path to generated MP3 file, audio size in bytes, and voice specifications.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_generate_speech,
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Script or narrative text to be converted to speech' },
        voice: {
          type: 'string',
          description: 'Neural voice name (default "pt-BR-AntonioNeural" - solemn dark documentary tone)',
          default: 'pt-BR-AntonioNeural'
        },
        output_filename: {
          type: 'string',
          description: 'Optional output filename (e.g., exercito_fantasma.mp3)'
        }
      },
      required: ['text']
    }
  },
  {
    name: 'omnipress_render_dark_video',
    title: 'Render Dark Video with Narration and Visuals',
    description: `Renders an MP4 video (vertical 9:16 for Shorts/Reels/TikTok or 16:9 for YouTube) by combining neural audio narration with images or atmospheric visuals using ffmpeg.

Use when:
- Producing ready-to-publish MP4 video files from script narrations and generated scene images.
- Creating automated Ken Burns zoom-effect videos for high-retention dark channels.

Do NOT use when:
- Staging YouTube metadata or queuing Buffer drafts without rendering video (use omnipress_queue_media_post instead).

Returns:
- Path to rendered MP4 video, audio file path, aspect ratio, and video dimensions.`,
    annotations: MCP_TOOL_ANNOTATIONS.omnipress_render_dark_video,
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Narrative text to synthesize (optional if audio_path is provided)' },
        audio_path: { type: 'string', description: 'Path to pre-existing MP3 audio file' },
        image_paths: {
          type: 'array',
          items: { type: 'string' },
          description: 'List of local image file paths to stitch into the video slideshow'
        },
        output_filename: { type: 'string', description: 'Target output video filename (e.g. video_01.mp4)' },
        aspect_ratio: {
          type: 'string',
          enum: ['9:16', '16:9'],
          default: '9:16',
          description: 'Video aspect ratio: 9:16 for vertical Shorts/Reels/TikTok, 16:9 for YouTube long-form'
        },
        voice: {
          type: 'string',
          default: 'pt-BR-AntonioNeural',
          description: 'Neural voice persona if text is provided'
        }
      }
    }
  }
];

async function handleRpcRequest(message) {
  const { id, method, params } = message;

  switch (method) {
    case 'initialize':
      return {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'omnipress', version: '0.1.0' }
        }
      };

    case 'notifications/initialized':
      return null;

    case 'tools/list':
      return {
        jsonrpc: '2.0',
        id,
        result: { tools: TOOLS_DEFINITIONS }
      };

    case 'tools/call': {
      const toolName = params?.name;
      const args = params?.arguments || {};
      let resultText = '';

      try {
        if (toolName === 'omnipress_publish_article') {
          resultText = saveArticle({
            title: args.title,
            contentMarkdown: args.content_markdown,
            category: args.category,
            tags: args.tags,
            author: args.author,
            sanitize: args.sanitize !== false
          });
        } else if (toolName === 'omnipress_queue_post') {
          resultText = await queuePost({
            text: args.text,
            platforms: args.platforms,
            title: args.title,
            mediaUrls: args.media_urls,
            scheduleTime: args.schedule_time,
            sanitize: args.sanitize !== false
          });
        } else if (toolName === 'omnipress_inspect_content') {
          const findings = inspectSensitiveData(args.text || '');
          if (findings.length === 0) {
            resultText = '✅ Content is clean! No sensitive lawsuit numbers, tax IDs, or PII detected.';
          } else {
            resultText = `⚠️ Found ${findings.length} sensitive item(s):\n` +
              findings.map(f => `  - [${f.type.toUpperCase()}]: ${f.match}`).join('\n');
          }
        } else if (toolName === 'omnipress_list_articles' || toolName === 'omnipress_list_recent') {
          resultText = listRecentArticles(args.limit || 5);
        } else if (toolName === 'omnipress_prepare_dark_script') {
          const bundle = prepareDarkScript({
            topic: args.topic,
            format: args.format || 'all',
            tone: args.tone || 'mystery',
            targetAudience: args.target_audience || 'geral'
          });
          resultText = JSON.stringify(bundle, null, 2);
        } else if (toolName === 'omnipress_queue_media_post') {
          resultText = await queueMediaPost({
            caption: args.caption,
            platforms: args.platforms,
            title: args.title,
            mediaUrls: args.media_urls,
            mediaType: args.media_type || 'image',
            tags: args.tags,
            thumbnailUrl: args.thumbnail_url,
            scheduleTime: args.schedule_time,
            sanitize: args.sanitize !== false
          });
        } else if (toolName === 'omnipress_brainstorm_channel') {
          const strategy = brainstormChannel({
            niche: args.niche || 'historia',
            tone: args.tone || 'mystery',
            targetAudience: args.target_audience || 'geral',
            language: args.language || 'pt-BR'
          });
          resultText = JSON.stringify(strategy, null, 2);
        } else if (toolName === 'omnipress_generate_speech') {
          const res = await generateSpeech({
            text: args.text,
            voice: args.voice || 'pt-BR-AntonioNeural',
            outputFilename: args.output_filename || null
          });
          resultText = JSON.stringify(res, null, 2);
        } else if (toolName === 'omnipress_render_dark_video') {
          const res = await renderDarkVideo({
            text: args.text,
            audioPath: args.audio_path,
            imagePaths: args.image_paths || [],
            outputFilename: args.output_filename || null,
            aspectRatio: args.aspect_ratio || '9:16',
            voice: args.voice || 'pt-BR-AntonioNeural'
          });
          resultText = JSON.stringify(res, null, 2);
        } else {
          return {
            jsonrpc: '2.0',
            id,
            error: { code: -32601, message: `Tool not found: ${toolName}` }
          };
        }

        return {
          jsonrpc: '2.0',
          id,
          result: {
            content: [{ type: 'text', text: resultText }]
          }
        };
      } catch (err) {
        return {
          jsonrpc: '2.0',
          id,
          error: { code: -32000, message: err.message }
        };
      }
    }

    case 'ping':
      return { jsonrpc: '2.0', id, result: {} };

    default:
      if (id !== undefined) {
        return {
          jsonrpc: '2.0',
          id,
          error: { code: -32601, message: `Method not found: ${method}` }
        };
      }
      return null;
  }
}

// ==========================================
// HTTP Server & ChatGPT OpenAPI Gateway
// ==========================================
function parseRequestBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', chunk => { raw += chunk; });
    req.on('end', () => {
      if (!raw.trim()) return resolve({});
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(new Error('Invalid JSON payload: ' + err.message));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, statusCode, data) {
  const json = JSON.stringify(data, null, 2);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(json),
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key'
  });
  res.end(json);
}

function createHttpServer() {
  const server = http.createServer(async (req, res) => {
    // CORS Preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key'
      });
      return res.end();
    }

    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = parsedUrl.pathname;

    try {
      // 1. Root / Health
      if (pathname === '/' || pathname === '/health') {
        return sendJson(res, 200, {
          status: 'ok',
          service: 'omnipress-mcp',
          version: '0.1.0',
          endpoints: {
            openapi: '/openapi.json',
            publish_article: 'POST /api/publish_article',
            queue_post: 'POST /api/queue_post',
            inspect_content: 'POST /api/inspect_content',
            list_articles: 'GET /api/list_articles',
            list_recent: 'GET /api/list_recent',
            mcp_rpc: 'POST /mcp'
          }
        });
      }

      // 2. OpenAPI 3.1 Spec for ChatGPT Actions
      if (pathname === '/openapi.json' && req.method === 'GET') {
        const openApiPath = path.join(PROJECT_ROOT, 'config', 'openapi.json');
        let spec = {};
        if (fs.existsSync(openApiPath)) {
          spec = JSON.parse(fs.readFileSync(openApiPath, 'utf8'));
        }
        // Dynamically adjust server URL based on request host
        const hostHeader = req.headers['host'] || 'localhost:3333';
        const proto = req.headers['x-forwarded-proto'] || 'http';
        spec.servers = [
          {
            url: `${proto}://${hostHeader}`,
            description: 'Current OmniPress Server Endpoint'
          }
        ];
        return sendJson(res, 200, spec);
      }

      // 3. MCP JSON-RPC 2.0 endpoint (for HTTP/remote MCP clients)
      if (pathname === '/mcp' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        const rpcRes = await handleRpcRequest(body);
        return sendJson(res, 200, rpcRes || {});
      }

      // 4. REST Endpoints for ChatGPT Custom GPT Actions
      if (pathname === '/api/publish_article' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        if (!body.title || !body.contentMarkdown) {
          return sendJson(res, 400, {
            success: false,
            error: 'Missing required fields: title and contentMarkdown are mandatory.'
          });
        }
        const report = saveArticle({
          title: body.title,
          contentMarkdown: body.contentMarkdown,
          category: body.category || 'technology',
          tags: body.tags || [],
          author: body.author || 'OmniPress',
          sanitize: body.sanitize !== false
        });
        return sendJson(res, 200, { success: true, message: report });
      }

      if (pathname === '/api/queue_post' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        if (!body.text) {
          return sendJson(res, 400, {
            success: false,
            error: 'Missing required field: text is mandatory.'
          });
        }
        const report = await queuePost({
          text: body.text,
          platforms: body.platforms || ['linkedin'],
          title: body.title || null,
          mediaUrls: body.mediaUrls || body.media_urls || [],
          scheduleTime: body.scheduleTime || body.schedule_time || null,
          sanitize: body.sanitize !== false
        });
        return sendJson(res, 200, { success: true, message: report });
      }

      if (pathname === '/api/prepare_dark_script' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        if (!body.topic) {
          return sendJson(res, 400, {
            success: false,
            error: 'Missing required field: topic is mandatory.'
          });
        }
        const bundle = prepareDarkScript({
          topic: body.topic,
          format: body.format || 'all',
          tone: body.tone || 'mystery',
          targetAudience: body.targetAudience || body.target_audience || 'geral'
        });
        return sendJson(res, 200, { success: true, bundle });
      }

      if (pathname === '/api/queue_media_post' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        if (!body.caption) {
          return sendJson(res, 400, {
            success: false,
            error: 'Missing required field: caption is mandatory.'
          });
        }
        const report = await queueMediaPost({
          caption: body.caption,
          platforms: body.platforms || ['instagram', 'x'],
          title: body.title || null,
          mediaUrls: body.mediaUrls || body.media_urls || [],
          mediaType: body.mediaType || body.media_type || 'image',
          tags: body.tags || [],
          thumbnailUrl: body.thumbnailUrl || body.thumbnail_url || null,
          scheduleTime: body.scheduleTime || body.schedule_time || null,
          sanitize: body.sanitize !== false
        });
        return sendJson(res, 200, { success: true, message: report });
      }

      if (pathname === '/api/inspect_content' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        const findings = inspectSensitiveData(body.text || '');
        return sendJson(res, 200, {
          clean: findings.length === 0,
          findings,
          message: findings.length === 0
            ? 'Content is clean! No sensitive lawsuit numbers, tax IDs, or PII detected.'
            : `Found ${findings.length} sensitive item(s).`
        });
      }

      if ((pathname === '/api/list_articles' || pathname === '/api/list_recent') && (req.method === 'GET' || req.method === 'POST')) {
        let limit = 5;
        if (req.method === 'GET') {
          limit = parseInt(parsedUrl.searchParams.get('limit'), 10) || 5;
        } else {
          const body = await parseRequestBody(req);
          limit = parseInt(body.limit, 10) || 5;
        }
        const report = listRecentArticles(limit);
        return sendJson(res, 200, { success: true, message: report });
      }

      if (pathname === '/api/brainstorm_channel' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        const strategy = brainstormChannel({
          niche: body.niche || 'historia',
          tone: body.tone || 'mystery',
          targetAudience: body.targetAudience || body.target_audience || 'geral',
          language: body.language || 'pt-BR'
        });
        return sendJson(res, 200, { success: true, strategy });
      }

      if (pathname === '/api/generate_speech' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        if (!body.text) {
          return sendJson(res, 400, { success: false, error: 'Missing required field: text is mandatory.' });
        }
        const speechRes = await generateSpeech({
          text: body.text,
          voice: body.voice || 'pt-BR-AntonioNeural',
          outputFilename: body.outputFilename || body.output_filename || null
        });
        return sendJson(res, 200, speechRes);
      }

      if (pathname === '/api/render_video' && req.method === 'POST') {
        const body = await parseRequestBody(req);
        const videoRes = await renderDarkVideo({
          text: body.text || null,
          audioPath: body.audioPath || body.audio_path || null,
          imagePaths: body.imagePaths || body.image_paths || [],
          outputFilename: body.outputFilename || body.output_filename || null,
          aspectRatio: body.aspectRatio || body.aspect_ratio || '9:16',
          voice: body.voice || 'pt-BR-AntonioNeural'
        });
        return sendJson(res, 200, videoRes);
      }

      // Not Found
      return sendJson(res, 404, { error: `Endpoint not found: ${req.method} ${pathname}` });
    } catch (err) {
      return sendJson(res, 500, { error: err.message || 'Internal server error' });
    }
  });

  return server;
}

function startHttpServer(port = 3333, host = '0.0.0.0') {
  const server = createHttpServer();
  server.listen(port, host, () => {
    console.log(`🌐 OmniPress HTTP & OpenAPI Gateway active at http://${host === '0.0.0.0' ? 'localhost' : host}:${port}`);
    console.log(`📜 OpenAPI Specification: http://localhost:${port}/openapi.json`);
    console.log(`🛠️ REST Actions:`);
    console.log(`   - POST /api/publish_article`);
    console.log(`   - POST /api/queue_post`);
    console.log(`   - POST /api/queue_media_post`);
    console.log(`   - POST /api/prepare_dark_script`);
    console.log(`   - POST /api/inspect_content`);
    console.log(`   - GET  /api/list_recent`);
    console.log(`🤖 MCP JSON-RPC 2.0: POST /mcp\n`);
  });
  return server;
}

// Read Stdio lines or run HTTP server based on CLI arguments
if (require.main === module) {
  const isHttp = process.argv.includes('--http') || process.env.OMNIPRESS_MODE === 'http';

  if (isHttp) {
    const httpIdx = process.argv.indexOf('--http');
    let port = 3333;
    if (httpIdx !== -1 && process.argv[httpIdx + 1] && !process.argv[httpIdx + 1].startsWith('-')) {
      port = parseInt(process.argv[httpIdx + 1], 10) || 3333;
    } else if (process.env.PORT) {
      port = parseInt(process.env.PORT, 10) || 3333;
    }
    startHttpServer(port);
  } else {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false
    });

    rl.on('line', async (line) => {
      const trimmed = line.trim();
      if (!trimmed) return;
      try {
        const parsed = JSON.parse(trimmed);
        const response = await handleRpcRequest(parsed);
        if (response) {
          process.stdout.write(JSON.stringify(response) + '\n');
        }
      } catch (err) {
        // Malformed JSON
        process.stdout.write(JSON.stringify({
          jsonrpc: '2.0',
          id: null,
          error: { code: -32700, message: 'Parse error' }
        }) + '\n');
      }
    });
  }
}

// Export functions for unit testing and programmatic embedding
module.exports = {
  inspectSensitiveData,
  sanitizeText,
  slugify,
  saveArticle,
  queuePost,
  formatInstagramCaption,
  segmentTwitterThread,
  stageYouTubeVideo,
  prepareDarkScript,
  brainstormChannel,
  generateSpeech,
  renderDarkVideo,
  queueMediaPost,
  handleRpcRequest,
  TOOLS_DEFINITIONS,
  MCP_TOOL_ANNOTATIONS,
  createHttpServer,
  startHttpServer
};
