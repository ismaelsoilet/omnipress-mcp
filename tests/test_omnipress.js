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
  assert.strictEqual(toolsRes.result.tools.length, 4);
  const toolNames = toolsRes.result.tools.map(t => t.name);
  assert(toolNames.includes('omnipress_publish_article'));
  assert(toolNames.includes('omnipress_queue_post'));
  assert(toolNames.includes('omnipress_inspect_content'));
  assert(toolNames.includes('omnipress_list_recent'));
  console.log('  ✓ MCP protocol passed: initialize and tools/list resolved correctly.\n');

  // Test 5: Tool Call Execution via JSON-RPC
  console.log('Test 5: MCP Tool Call Execution (omnipress_inspect_content)...');
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
  console.log('  ✓ MCP tool call passed.\n');

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

  // Clean up test directory
  fs.rmSync(tempDir, { recursive: true, force: true });

  console.log('═══════════════════════════════════════════════════════');
  console.log('🎉 ALL 6 TEST SUITES PASSED WITH MAXIMUM RIGOR & CARE!');
  console.log('═══════════════════════════════════════════════════════');
}

runTests().catch(err => {
  console.error('❌ Test suite failed:', err);
  process.exit(1);
});
