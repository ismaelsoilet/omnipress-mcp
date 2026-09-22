#!/usr/bin/env node
/**
 * Automated Claude Desktop Setup Script for OmniPress MCP.
 * Configures Claude Desktop to recognize OmniPress MCP without manual JSON editing.
 */

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');

function getClaudeConfigPath() {
  const platform = process.platform;
  if (platform === 'win32') {
    const appData = process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming');
    return path.join(appData, 'Claude', 'claude_desktop_config.json');
  } else if (platform === 'darwin') {
    return path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else {
    return path.join(os.homedir(), '.config', 'Claude', 'claude_desktop_config.json');
  }
}

function loadLocalEnv(projectRoot) {
  const envPath = path.join(projectRoot, '.env');
  const envVars = {};
  if (fs.existsSync(envPath)) {
    const lines = fs.readFileSync(envPath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx !== -1) {
        const key = trimmed.slice(0, eqIdx).trim();
        const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
        if (val) envVars[key] = val;
      }
    }
  }
  return envVars;
}

function runSetup() {
  console.log('🤖 OmniPress MCP — Claude Desktop Configuration Utility\n');

  const projectRoot = path.resolve(__dirname, '..');
  const serverJsPath = path.join(projectRoot, 'src', 'server.js');
  const articlesDirPath = path.join(projectRoot, 'articles');
  const configPath = getClaudeConfigPath();
  const configDir = path.dirname(configPath);

  if (!fs.existsSync(serverJsPath)) {
    console.error(`❌ Error: server.js not found at ${serverJsPath}`);
    process.exit(1);
  }

  console.log(`📁 Target Claude Desktop config: ${configPath}`);

  // Ensure Claude config directory exists
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
    console.log(`Created directory: ${configDir}`);
  }

  let config = { mcpServers: {} };
  if (fs.existsSync(configPath)) {
    try {
      const raw = fs.readFileSync(configPath, 'utf8');
      config = JSON.parse(raw);
      if (!config.mcpServers) config.mcpServers = {};

      // Create backup
      const backupPath = `${configPath}.bak-${Date.now()}`;
      fs.writeFileSync(backupPath, raw, 'utf8');
      console.log(`📦 Created backup of existing config at: ${backupPath}`);
    } catch (err) {
      console.warn(`⚠️ Warning: Existing config could not be parsed (${err.message}). A new config will be generated.`);
      config = { mcpServers: {} };
    }
  }

  // Read .env if present
  const localEnv = loadLocalEnv(projectRoot);
  const serverEnv = {
    ARTICLES_DIR: localEnv.ARTICLES_DIR || articlesDirPath
  };
  if (localEnv.BUFFER_ACCESS_TOKEN) serverEnv.BUFFER_ACCESS_TOKEN = localEnv.BUFFER_ACCESS_TOKEN;
  if (localEnv.BUFFER_LINKEDIN_PROFILE_ID) serverEnv.BUFFER_LINKEDIN_PROFILE_ID = localEnv.BUFFER_LINKEDIN_PROFILE_ID;
  if (localEnv.BUFFER_X_PROFILE_ID) serverEnv.BUFFER_X_PROFILE_ID = localEnv.BUFFER_X_PROFILE_ID;
  if (localEnv.BUFFER_THREADS_PROFILE_ID) serverEnv.BUFFER_THREADS_PROFILE_ID = localEnv.BUFFER_THREADS_PROFILE_ID;
  if (localEnv.REDDIT_CLIENT_ID) serverEnv.REDDIT_CLIENT_ID = localEnv.REDDIT_CLIENT_ID;
  if (localEnv.REDDIT_CLIENT_SECRET) serverEnv.REDDIT_CLIENT_SECRET = localEnv.REDDIT_CLIENT_SECRET;
  if (localEnv.REDDIT_USERNAME) serverEnv.REDDIT_USERNAME = localEnv.REDDIT_USERNAME;
  if (localEnv.REDDIT_PASSWORD) serverEnv.REDDIT_PASSWORD = localEnv.REDDIT_PASSWORD;
  if (localEnv.REDDIT_DEFAULT_SUBREDDIT) serverEnv.REDDIT_DEFAULT_SUBREDDIT = localEnv.REDDIT_DEFAULT_SUBREDDIT;
  if (localEnv.OMNIPRESS_WEBHOOK_URL) serverEnv.OMNIPRESS_WEBHOOK_URL = localEnv.OMNIPRESS_WEBHOOK_URL;
  if (localEnv.OMNIPRESS_WEBHOOK_SECRET) serverEnv.OMNIPRESS_WEBHOOK_SECRET = localEnv.OMNIPRESS_WEBHOOK_SECRET;

  config.mcpServers.omnipress = {
    command: 'node',
    args: [serverJsPath],
    env: serverEnv
  };

  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');

  console.log('\n✅ Successfully configured OmniPress MCP in Claude Desktop!');
  console.log(`Server command: node ${serverJsPath}`);
  console.log('🔄 Please restart Claude Desktop to load the new tools:');
  console.log('   - omnipress_publish_article');
  console.log('   - omnipress_queue_post');
  console.log('   - omnipress_inspect_content');
  console.log('   - omnipress_list_recent\n');
}

if (require.main === module) {
  runSetup();
}

module.exports = { getClaudeConfigPath, runSetup };
