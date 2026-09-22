#!/usr/bin/env node
/**
 * OmniPress MCP Server — Pure Node.js implementation (Zero dependencies, native stdio JSON-RPC).
 * Compatible with Node.js 18+ / 20+ / 24+ without requiring `npm install`.
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const readline = require('node:readline');
const http = require('node:http');
const url = require('node:url');

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
const BUFFER_ACCESS_TOKEN = process.env.BUFFER_ACCESS_TOKEN || '';
const BUFFER_LINKEDIN_PROFILE_ID = process.env.BUFFER_LINKEDIN_PROFILE_ID || '';
const BUFFER_X_PROFILE_ID = process.env.BUFFER_X_PROFILE_ID || '';
const BUFFER_THREADS_PROFILE_ID = process.env.BUFFER_THREADS_PROFILE_ID || '';

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

  // 1. Buffer Dispatch (LinkedIn, X, Threads)
  if (BUFFER_ACCESS_TOKEN && (BUFFER_LINKEDIN_PROFILE_ID || BUFFER_X_PROFILE_ID || BUFFER_THREADS_PROFILE_ID)) {
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

    // Extract title from explicit title arg or first line of text
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

  // 3. Webhook Dispatch
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

  // 4. Fallback when no keys configured
  const hasConfiguredService = BUFFER_ACCESS_TOKEN || REDDIT_CLIENT_ID || OMNIPRESS_WEBHOOK_URL;
  if (!hasConfiguredService) {
    results.push(
      'ℹ️ No external provider configured in `.env` (BUFFER_ACCESS_TOKEN, REDDIT_CLIENT_ID, or OMNIPRESS_WEBHOOK_URL).\n' +
      'Content formatted and de-identified successfully. Ready for copy-paste:\n\n' +
      '```text\n' + processedText + '\n```'
    );
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
// MCP JSON-RPC 2.0 Protocol Handler
// ==========================================
const TOOLS_DEFINITIONS = [
  {
    name: 'omnipress_publish_article',
    description: 'Saves a complete, publication-ready long-form article to the local archive with YAML frontmatter. Runs automatic legal/PII de-identification.',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: 'Article title' },
        content_markdown: { type: 'string', description: 'Complete article in GitHub-flavored Markdown' },
        category: { type: 'string', description: 'Topic category (technology, tributario, pericia, govtech)' },
        tags: { type: 'array', items: { type: 'string' }, description: 'Array of keyword tags' },
        author: { type: 'string', description: 'Author name' },
        sanitize: { type: 'boolean', description: 'Whether to sanitize court numbers and PII (default true)' }
      },
      required: ['title', 'content_markdown']
    }
  },
  {
    name: 'omnipress_queue_post',
    description: 'Queues a post or thread to social platforms (LinkedIn, X, Threads via Buffer, or Reddit) in Draft/Review mode.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Post text or thread segment' },
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
    description: 'Scans text for sensitive judicial lawsuit numbers (CNJ), tax IDs (CPF/CNPJ), emails, or PII without publishing.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to scan for PII' }
      },
      required: ['text']
    }
  },
  {
    name: 'omnipress_list_recent',
    description: 'Lists recently saved articles in the local archive.',
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: 'Number of articles to return (default 5)' }
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
        } else if (toolName === 'omnipress_list_recent') {
          resultText = listRecentArticles(args.limit || 5);
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

      if (pathname === '/api/list_recent' && (req.method === 'GET' || req.method === 'POST')) {
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
  handleRpcRequest,
  TOOLS_DEFINITIONS,
  createHttpServer,
  startHttpServer
};
