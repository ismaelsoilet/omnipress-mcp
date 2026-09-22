# 🚀 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md)

> **O Motor Agêntico de Publicação e Autoridade para Antigravity via Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Padrão MCP](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Nativo Antigravity](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

O **OmniPress MCP** capacita agentes de IA a transformar notas técnicas brutas, estudos de caso de perícia judicial, decisões fiscais/tributárias e arquiteturas de software em artigos completos de alta autoridade e campanhas em redes sociais com desidentificação automática (LGPD e segredo de justiça) e aprovação humana integrada.

---

## 🌟 Recursos Principais

- 🎯 **Adaptação Dinâmica de Tom**: Alterna com precisão entre **Tecnologia/Engenharia de Software**, **Direito Tributário**, **Perícia Judicial de TI/Contábil** e **Administração Pública/GovTech**.
- 🛡️ **Filtro de Privacidade e Ética (LGPD / Segredo de Justiça)**: Detecção e mascaramento automático de números de processos judiciais no formato CNJ (`0000000-00.0000.0.00.0000`), CPFs, CNPJs, e-mails e dados identificadores.
- 📐 **Fluxo Tri-Formato**: Uma única ideia é desdobrada em 3 ativos integrados:
  1. **Artigo Completo**: Arquivo Markdown com frontmatter YAML detalhado para Substack, Jusbrasil, Medium ou blogs estáticos.
  2. **Post de Alta Autoridade para o LinkedIn**: Gancho inicial persuasivo, 3 a 5 tópicos de destaque e chamada para engajamento.
  3. **Thread para o X (Twitter)**: Sequência concisa de 3 a 5 micro-posts para consumo rápido.
- 🔌 **Arquitetura Multi-Provedores Modular**:
  - **Buffer**: Envio direto para **LinkedIn**, **X (Twitter)** e **Meta Threads** em modo rascunho com aprovação por aplicativo móvel.
  - **Motor Direto do Reddit**: Publicação de postagens completas com formatação Markdown diretamente em subreddits (ex: `r/webdev`, `r/SideProject`, `r/direito`, `r/contabilidade`).
  - **Webhook Genérico**: Integração completa com pipelines no **n8n**, Make, Slack ou Telegram.
  - **Arquivo Local de Markdown**: Organização de artigos estruturada por `AAAA/MM/`.
- ⚡ **Dual-Runtime**: Execução nativa tanto em **Node.js (18+) sem dependências externas** quanto em **Python (FastMCP)**.

---

## 🏛️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                       ANTIGRAVITY                       │
│      (Redação, adaptação de tom e síntese agêntica)     │
└────────────────────────────┬────────────────────────────┘
                             │ Model Context Protocol (MCP)
┌────────────────────────────▼────────────────────────────┐
│                  Servidor OmniPress MCP                 │
│  ├── Motor de Sanitização & LGPD (Processos CNJ / PII)  │
│  └── Camada Modular de Adaptadores                      │
└──────────────┬───────────────────┬───────────────────┬──┘
               │                   │                   │
               ▼                   ▼                   ▼
      ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
      │ Adaptador Buffer│ │Adaptador Reddit │ │  Arquivo Local  │
      │  (LinkedIn, X,  │ │ (Submissão Direta││   (Markdown)    │
      │    Threads)     │ │ em Subreddits)  │ └─────────────────┘
      └─────────────────┘ └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │Adaptador Webhook│
                          │  (n8n / Make)   │
                          └─────────────────┘
```

---

## 📦 Estrutura do Projeto

```
omnipress-mcp/
├── .agents/skills/omnipress/   # Skill para Antigravity (instruções do runbook)
├── docs/                      # Guias de configuração e contas
│   ├── SETUP_GUIDE.md         # Guia em Inglês
│   └── SETUP_GUIDE.pt-BR.md   # Guia em Português
├── src/
│   ├── adapters/              # Adaptadores Buffer, Webhook e Markdown (Python)
│   ├── utils/                 # Sanitizador de dados sensíveis (Python)
│   ├── server.js              # Servidor MCP em Node.js (Zero dependências externas)
│   └── server.py              # Servidor FastMCP em Python
├── tests/
│   ├── test_omnipress.js      # Suíte de testes unitários em Node.js
│   └── test_omnipress.py      # Suíte de testes unitários em Python
├── AGENTS.md                  # Regras operacionais para agentes de IA
├── plugin.json                # Manifesto de plugin Antigravity
├── mcp_config.json            # Configuração local MCP
├── package.json               # Configuração Node.js / npm
├── pyproject.toml             # Especificação do pacote Python
└── .env.example               # Modelo de variáveis de ambiente
```

---

## ⚡ Instalação e Testes

### 1. Testes Automatizados (Node.js)
O projeto roda nativamente no Node.js sem necessidade de compilação ou pacotes externos pesados:

```bash
# Executar a suíte de testes com 5 cenários de validação
npm test
# ou: node tests/test_omnipress.js
```

### 2. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Consulte o [Guia de Configuração de Contas (docs/SETUP_GUIDE.pt-BR.md)](docs/SETUP_GUIDE.pt-BR.md) para obter o token do Buffer e os IDs do LinkedIn e X.

---

## 🤖 Integração com o Antigravity

Adicione o servidor no seu arquivo global `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "omnipress": {
      "command": "node",
      "args": ["C:/Users/Ismael/projects/omnipress-mcp/src/server.js"],
      "env": {
        "ARTICLES_DIR": "C:/Users/Ismael/projects/omnipress-mcp/articles"
      }
    }
  }
}
```

### Exemplo de Uso no Chat
Converse normalmente com o Antigravity:

> *"OmniPress: Elabore uma análise técnica sobre a tributação de software na Reforma Tributária (IBS/CBS versus ISS), focando em SaaS. Gere o artigo completo, um post persuasivo para o LinkedIn e uma thread no X. Aplique a sanitização em menções a processos judiciais."*

O Antigravity produzirá a prévia do artigo e das postagens, e ao receber sua aprovação, salvará o artigo e enviará as postagens para a fila de rascunhos!

---

## 🛠️ Ferramentas MCP Expostas

| Ferramenta | Descrição |
| :--- | :--- |
| `omnipress_publish_article` | Salva o artigo completo no arquivo local com frontmatter YAML e filtro LGPD. |
| `omnipress_queue_post` | Envia postagem para a fila de rascunhos do LinkedIn e X via Buffer ou Webhook. |
| `omnipress_inspect_content` | Varre o texto em busca de números de processo CNJ, CPFs, CNPJs ou dados confidenciais. |
| `omnipress_list_recent` | Lista os artigos recentemente arquivados e suas datas de modificação. |

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
