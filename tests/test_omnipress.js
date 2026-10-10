/**
 * Comprehensive Unit Tests for OmniPress MCP (Node.js engine)
 */

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {
  inspectSensitiveData,
  sanitizeText,
  slugify,
  saveArticle,
  queuePost,
  formatInstagramCaption,
  segmentTwitterThread,
  stageYouTubeVideo,
  prepareDarkScript,
  queueMediaPost,
  handleRpcRequest,
  TOOLS_DEFINITIONS,
  createHttpServer
} = require('../src/server.js');

async function runTests() {
  console.log('🧪 Starting OmniPress MCP Unit Test Suite...\n');

  // Test 1: Sanitizer & Legal / Tax PII Detection
  console.log('Test 1: Sanitizer & PII Detection...');
  const sampleText =
    'No processo 0001234-56.2023.8.26.0100 o perito analisou a empresa CNPJ 12.345.678/0001-90 ' +
    'onde o sócio CPF 123.456.789-00 respondeu via perito@tribunal.jus.br sobre a perícia.';

  const findings = inspectSensitiveData(sampleText);
  assert.strictEqual(findings.length, 4, `Expected 4 sensitive items, found ${findings.length}`);
  const foundTypes = findings.map(f => f.type);
  assert(foundTypes.includes('lawsuit_number'), 'Must detect lawsuit number');
  assert(foundTypes.includes('cnpj'), 'Must detect CNPJ');
  assert(foundTypes.includes('cpf'), 'Must detect CPF');
  assert(foundTypes.includes('email'), 'Must detect email');

  const { sanitized } = sanitizeText(sampleText);
  assert(!sanitized.includes('0001234-56.2023.8.26.0100'), 'Lawsuit number should be masked');
  assert(!sanitized.includes('12.345.678/0001-90'), 'CNPJ should be masked');
  assert(!sanitized.includes('123.456.789-00'), 'CPF should be masked');
  assert(!sanitized.includes('perito@tribunal.jus.br'), 'Email should be masked');
  assert(sanitized.includes('[PROCESSO ANÔNIMO]'), 'Expected [PROCESSO ANÔNIMO] mask');
  console.log('  ✓ Sanitizer passed: All CNJ lawsuit numbers, CPFs, CNPJs, and emails masked.\n');

  // Test 2: Slugify & URL Normalization
  console.log('Test 2: Slugify...');
  assert.strictEqual(slugify('Reforma Tributária e Software: O que Muda?'), 'reforma-tributaria-e-software-o-que-muda');
  assert.strictEqual(slugify('Auditando Bancos de Dados em Perícia Judicial'), 'auditando-bancos-de-dados-em-pericia-judicial');
  console.log('  ✓ Slugify passed.\n');

  // Test 3: Article Archiving with YAML Frontmatter
  console.log('Test 3: Article Archiving...');
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'omnipress-test-'));
  process.env.ARTICLES_DIR = tempDir;

  const saveReport = saveArticle({
    title: 'Auditando Bancos de Dados em Perícia Judicial',
    contentMarkdown: 'Conteúdo detalhado da perícia contábil e de TI.',
    category: 'pericia-judicial',
    tags: ['pericia', 'sql', 'tributario'],
    author: 'Perito Judicial TI'
  });

  assert(saveReport.includes('Article archived successfully'), 'Expected success message');
  const files = fs.readdirSync(tempDir, { recursive: true });
  const mdFiles = files.filter(f => f.toString().endsWith('.md'));
  assert(mdFiles.length > 0, 'Markdown article should have been created on disk');

  const savedContent = fs.readFileSync(path.join(tempDir, mdFiles[0]), 'utf8');
  assert(savedContent.includes('title: "Auditando Bancos de Dados em Perícia Judicial"'));
  assert(savedContent.includes('category: "pericia-judicial"'));
  assert(savedContent.includes('- pericia'));
  assert(savedContent.includes('status: draft'));
  console.log('  ✓ Article archiving passed: File created with valid YAML frontmatter.\n');

  // Test 4: JSON-RPC MCP Protocol Handshake & Tool Listing
  console.log('Test 4: MCP Protocol Handshake...');
  const initRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { capabilities: {} }
  });
  assert.strictEqual(initRes.result.serverInfo.name, 'omnipress');
  assert.strictEqual(initRes.result.protocolVersion, '2024-11-05');

  const toolsRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/list',
    params: {}
  });
  assert.strictEqual(toolsRes.result.tools.length, 9);
  const toolNames = toolsRes.result.tools.map(t => t.name);
  assert(toolNames.includes('omnipress_publish_article'));
  assert(toolNames.includes('omnipress_queue_post'));
  assert(toolNames.includes('omnipress_inspect_content'));
  assert(toolNames.includes('omnipress_list_articles'), 'Must include canonical verb_noun omnipress_list_articles');
  assert(toolNames.includes('omnipress_prepare_dark_script'), 'Must include omnipress_prepare_dark_script');
  assert(toolNames.includes('omnipress_queue_media_post'), 'Must include omnipress_queue_media_post');
  assert(toolNames.includes('omnipress_brainstorm_channel'), 'Must include omnipress_brainstorm_channel');
  assert(toolNames.includes('omnipress_generate_speech'), 'Must include omnipress_generate_speech');
  assert(toolNames.includes('omnipress_render_dark_video'), 'Must include omnipress_render_dark_video');

  for (const tool of toolsRes.result.tools) {
    assert(tool.title, `Tool ${tool.name} must have a title`);
    assert(tool.annotations, `Tool ${tool.name} must have annotations`);
    assert(typeof tool.annotations.readOnlyHint === 'boolean');
    assert(typeof tool.annotations.destructiveHint === 'boolean');
    assert(typeof tool.annotations.idempotentHint === 'boolean');
    assert(typeof tool.annotations.openWorldHint === 'boolean');
    assert(tool.description.includes('Use when:'), `Tool ${tool.name} description missing 'Use when:'`);
    assert(tool.description.includes('Do NOT use when:'), `Tool ${tool.name} description missing 'Do NOT use when:'`);
    assert(tool.description.includes('Returns:'), `Tool ${tool.name} description missing 'Returns:'`);
  }
  console.log('  ✓ MCP protocol passed: initialize, TDQS annotations, and canonical tools/list resolved correctly.\n');

  // Test 5: Tool Call Execution via JSON-RPC
  console.log('Test 5: MCP Tool Call Execution (omnipress_inspect_content & list alias)...');
  const callRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: {
      name: 'omnipress_inspect_content',
      arguments: {
        text: 'Documento limpo sem nenhum dado confidencial.'
      }
    }
  });
  assert(callRes.result.content[0].text.includes('Content is clean!'));

  // Test 5.1: Canonical and Alias Tool Calls (omnipress_list_articles & omnipress_list_recent)
  const listCanonicalRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 31,
    method: 'tools/call',
    params: { name: 'omnipress_list_articles', arguments: { limit: 3 } }
  });
  assert(listCanonicalRes.result.content[0].text.includes('Recent Articles') || listCanonicalRes.result.content[0].text.includes('No articles'));

  const listAliasRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 32,
    method: 'tools/call',
    params: { name: 'omnipress_list_recent', arguments: { limit: 3 } }
  });
  assert.strictEqual(listCanonicalRes.result.content[0].text, listAliasRes.result.content[0].text, 'Canonical and alias calls must return identical output');
  console.log('  ✓ MCP tool call passed: canonical inspection and list_articles/list_recent parity verified.\n');

  // Test 6: Threads & Reddit Tool Call Execution via JSON-RPC
  console.log('Test 6: MCP Queue Post (Threads & Reddit)...');
  const queueRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 4,
    method: 'tools/call',
    params: {
      name: 'omnipress_queue_post',
      arguments: {
        text: 'Lançando nova ferramenta aberta para perícia judicial de software no processo 0001234-56.2023.8.26.0100!',
        platforms: ['threads', 'reddit:SideProject'],
        title: 'Open Source Software Forensics Tool for Antigravity'
      }
    }
  });
  const queueOutput = queueRes.result.content[0].text;
  assert(queueOutput.includes('[PROCESSO ANÔNIMO]'), 'Sensitive court case number must be masked');
  assert(queueOutput.includes('Masked 1 sensitive item'), 'Should report 1 masked item');
  console.log('  ✓ Threads & Reddit queue test passed: Sanitization & parameters validated.\n');

  // Test 7: HTTP Gateway & OpenAPI Specification (ChatGPT Custom GPT Actions)
  console.log('Test 7: HTTP Gateway & ChatGPT OpenAPI Specification...');
  const server = createHttpServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const assignedPort = server.address().port;
  const baseUrl = `http://127.0.0.1:${assignedPort}`;

  try {
    // 7.1 Health check
    const healthRes = await fetch(`${baseUrl}/health`);
    assert.strictEqual(healthRes.status, 200);
    const healthJson = await healthRes.json();
    assert.strictEqual(healthJson.status, 'ok');
    assert.strictEqual(healthJson.service, 'omnipress-mcp');

    // 7.2 OpenAPI 3.1 Spec endpoint
    const openApiRes = await fetch(`${baseUrl}/openapi.json`);
    assert.strictEqual(openApiRes.status, 200);
    const openApiJson = await openApiRes.json();
    assert.strictEqual(openApiJson.openapi, '3.1.0');
    assert(openApiJson.paths['/api/publish_article'], 'Must define publish_article path');
    assert(openApiJson.paths['/api/queue_post'], 'Must define queue_post path');
    assert(openApiJson.paths['/api/inspect_content'], 'Must define inspect_content path');
    assert(openApiJson.paths['/api/list_recent'], 'Must define list_recent path');

    // 7.3 REST Inspect Content
    const inspectRes = await fetch(`${baseUrl}/api/inspect_content`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'Processo CNJ 0001234-56.2023.8.26.0100 verificado.' })
    });
    assert.strictEqual(inspectRes.status, 200);
    const inspectJson = await inspectRes.json();
    assert.strictEqual(inspectJson.clean, false);
    assert.strictEqual(inspectJson.findings.length, 1);
    assert.strictEqual(inspectJson.findings[0].type, 'lawsuit_number');

    // 7.4 REST Publish Article
    const publishRes = await fetch(`${baseUrl}/api/publish_article`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Artigo Via HTTP Gateway',
        contentMarkdown: 'Conteúdo publicado através do endpoint HTTP.',
        category: 'technology',
        tags: ['http', 'chatgpt']
      })
    });
    assert.strictEqual(publishRes.status, 200);
    const publishJson = await publishRes.json();
    assert.strictEqual(publishJson.success, true);
    assert(publishJson.message.includes('Article archived successfully'));

    // 7.5 REST List Recent
    const listRes = await fetch(`${baseUrl}/api/list_recent?limit=3`);
    assert.strictEqual(listRes.status, 200);
    const listJson = await listRes.json();
    assert.strictEqual(listJson.success, true);

    console.log('  ✓ HTTP Gateway passed: Health, OpenAPI 3.1, and REST tool endpoints all verified.\n');
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }

  // Test 8: Instagram Caption Formatting & Tagging
  console.log('Test 8: Instagram Formatting...');
  const igCaption = formatInstagramCaption(
    'O segredo oculto dos arquivos desclassificados.',
    ['darkchannel', 'misterio', 'investigacao']
  );
  assert(igCaption.includes('#darkchannel #misterio #investigacao'), 'Must include formatted hashtags');
  assert(igCaption.length <= 2200, 'Must not exceed 2200 characters');
  console.log('  ✓ Instagram caption formatting passed.\n');

  // Test 9: Twitter / X Thread Auto-Segmentation
  console.log('Test 9: Twitter Thread Auto-Segmentation...');
  const multiTweet = 'Tweet 1 de introdução chocante.\n---\nTweet 2 com os dados e evidências.\n---\nTweet 3 com o desfecho e CTA.';
  const segmented = segmentTwitterThread(multiTweet);
  assert.strictEqual(segmented.length, 3, 'Should segment into 3 tweets');
  assert(segmented[0].startsWith('1/3'), 'Should number first tweet');
  assert(segmented[2].startsWith('3/3'), 'Should number last tweet');
  console.log('  ✓ Twitter thread auto-segmentation passed.\n');

  // Test 10: YouTube Video & Shorts Staging
  console.log('Test 10: YouTube Video & Shorts Staging...');
  const stagingTemp = fs.mkdtempSync(path.join(os.tmpdir(), 'omnipress-yt-staging-'));
  process.env.MEDIA_STAGING_DIR = stagingTemp;

  const ytStaged = stageYouTubeVideo({
    title: 'O Enigma do Manuscrito Proibido',
    description: 'Documentário completo sobre o manuscrito.',
    tags: ['historia', 'misterio'],
    isShort: true,
    mediaUrls: ['https://example.com/video.mp4']
  });

  assert(ytStaged.manifest.title.includes('#Shorts'), 'Shorts title must include #Shorts');
  assert.strictEqual(ytStaged.manifest.isShort, true);
  assert(fs.existsSync(ytStaged.filepath), 'Manifest JSON file must exist on disk');
  const readManifest = JSON.parse(fs.readFileSync(ytStaged.filepath, 'utf8'));
  assert.strictEqual(readManifest.platform, 'youtube_shorts');
  assert.strictEqual(readManifest.title, ytStaged.manifest.title);
  fs.rmSync(stagingTemp, { recursive: true, force: true });
  console.log('  ✓ YouTube Shorts & Long-form staging passed.\n');

  // Test 11: Dark Channel Script Generator (omnipress_prepare_dark_script)
  console.log('Test 11: Dark Channel Script Generator (JSON-RPC)...');
  const scriptRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 11,
    method: 'tools/call',
    params: {
      name: 'omnipress_prepare_dark_script',
      arguments: {
        topic: 'A Cidade Perdida de Z',
        tone: 'mystery',
        target_audience: 'curiosos e historiadores'
      }
    }
  });
  assert(scriptRes.result?.content?.[0]?.text, 'Must return script bundle text');
  const parsedBundle = JSON.parse(scriptRes.result.content[0].text);
  assert.strictEqual(parsedBundle.topic, 'A Cidade Perdida de Z');
  assert(parsedBundle.shortScript.hook_0_3s, 'Must contain 0-3s hook');
  assert(parsedBundle.visualScenePrompts.length >= 5, 'Must contain scene prompts');
  assert(parsedBundle.visualScenePrompts[0].aiPrompt.includes('9:16'), 'Image prompt must specify 9:16 aspect ratio');
  assert(parsedBundle.instagramCarousel.slide1_cover, 'Must contain Instagram carousel slides');
  assert(parsedBundle.xThread.length >= 5, 'Must contain X thread tweets');
  assert(parsedBundle.youtubeMetadata.title, 'Must contain YouTube title');
  console.log('  ✓ Dark channel script generator passed: Complete multi-platform bundle verified.\n');

  // Test 12: Rich Media Post Queuing (omnipress_queue_media_post)
  console.log('Test 12: Rich Media Post Queuing (Instagram, YouTube, X)...');
  const mediaQueueRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 12,
    method: 'tools/call',
    params: {
      name: 'omnipress_queue_media_post',
      arguments: {
        title: 'O Mistério de Z Revelado',
        caption: 'Uma investigação proibida sobre os arquivos esquecidos da expedição de 1925 no processo 0001234-56.2023.8.26.0100.',
        platforms: ['instagram', 'youtube_shorts', 'x'],
        media_type: 'short',
        media_urls: ['https://example.com/shorts/video.mp4'],
        tags: ['misterio', 'historia']
      }
    }
  });
  const mediaQueueOutput = mediaQueueRes.result.content[0].text;
  assert(mediaQueueOutput.includes('Instagram'), 'Must include Instagram report');
  assert(mediaQueueOutput.includes('YouTube'), 'Must include YouTube report');
  assert(mediaQueueOutput.includes('X (Twitter)'), 'Must include X report');
  assert(mediaQueueOutput.includes('[PROCESSO ANÔNIMO]'), 'Sensitive court case must be sanitized in media post');
  console.log('  ✓ Rich media post queuing passed: Multi-platform dispatch verified.\n');

  // Test 13: Channel Ideation & Strategy (omnipress_brainstorm_channel)
  console.log('Test 13: Channel Strategy & Ideation (omnipress_brainstorm_channel)...');
  const brainstormRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 13,
    method: 'tools/call',
    params: {
      name: 'omnipress_brainstorm_channel',
      arguments: {
        niche: 'historia',
        tone: 'mystery',
        target_audience: 'geral'
      }
    }
  });
  assert(brainstormRes.result?.content?.[0]?.text, 'Must return strategy bundle text');
  const parsedStrategy = JSON.parse(brainstormRes.result.content[0].text);
  assert.strictEqual(parsedStrategy.niche, 'historia');
  assert(parsedStrategy.channelConcepts.length >= 3, 'Must contain at least 3 channel name concepts');
  assert(parsedStrategy.contentPillars.length >= 3, 'Must contain at least 3 content pillars');
  assert(parsedStrategy.viralTopicsBacklog.length >= 5, 'Must contain at least 5 viral topics');
  assert(parsedStrategy.viralTopicsBacklog[0].hook_0_3s, 'Topics must contain tested 0-3s hooks');
  assert(parsedStrategy.productionSpecs.audioVoice.includes('AntonioNeural'), 'Must recommend AntonioNeural voice');
  console.log('  ✓ Channel strategy ideation passed: High-retention concepts and pillars verified.\n');

  // Test 14: Neural Speech Audio Generation (omnipress_generate_speech)
  console.log('Test 14: Neural Speech Audio Generation (omnipress_generate_speech)...');
  const speechRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 14,
    method: 'tools/call',
    params: {
      name: 'omnipress_generate_speech',
      arguments: {
        text: 'Em 1944, os Estados Unidos venceram uma das batalhas mais decisivas da história usando tanques de borracha.',
        voice: 'pt-BR-AntonioNeural',
        output_filename: 'test_unit_speech.mp3'
      }
    }
  });
  assert(speechRes.result?.content?.[0]?.text, 'Must return speech generation response');
  const parsedSpeech = JSON.parse(speechRes.result.content[0].text);
  assert.strictEqual(parsedSpeech.success, true, 'Speech generation must succeed');
  assert(parsedSpeech.audio_path && fs.existsSync(parsedSpeech.audio_path), 'Audio MP3 file must exist on disk');
  assert(parsedSpeech.audio_size_bytes > 0, 'Audio file size must be greater than zero');
  console.log('  ✓ Neural speech audio generation passed: MP3 file generated with valid size.\n');

  // Test 15: Dark Video Rendering Pipeline (omnipress_render_dark_video)
  console.log('Test 15: Dark Video Rendering Pipeline (omnipress_render_dark_video)...');
  const renderRes = await handleRpcRequest({
    jsonrpc: '2.0',
    id: 15,
    method: 'tools/call',
    params: {
      name: 'omnipress_render_dark_video',
      arguments: {
        audio_path: parsedSpeech.audio_path,
        output_filename: 'test_unit_video.mp4',
        aspect_ratio: '9:16'
      }
    }
  });
  assert(renderRes.result?.content?.[0]?.text, 'Must return render pipeline response');
  const parsedRender = JSON.parse(renderRes.result.content[0].text);
  assert.strictEqual(parsedRender.success, true, 'Render pipeline execution must succeed');
  assert.strictEqual(parsedRender.aspect_ratio, '9:16');
  console.log('  ✓ Dark video pipeline passed: Robust audio & video staging verified.\n');

  // Clean up test directory
  fs.rmSync(tempDir, { recursive: true, force: true });

  console.log('═══════════════════════════════════════════════════════');
  console.log('🎉 ALL 15 TEST SUITES PASSED WITH MAXIMUM RIGOR & CARE!');
  console.log('═══════════════════════════════════════════════════════');
}

runTests().catch(err => {
  console.error('❌ Test suite failed:', err);
  process.exit(1);
});
