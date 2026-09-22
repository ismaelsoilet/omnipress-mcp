# 🌐 OmniPress MCP

[🇺🇸 English](README.md) | [🇧🇷 Português](README.pt-BR.md) | [📖 GitHub Wiki](https://github.com/ismaelsoilet/omnipress-mcp/wiki)

> **O Protocolo Universal de Publicação Agêntica e Motor de Distribuição para Agentes de IA via Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Padrão MCP](https://img.shields.io/badge/MCP-1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Nativo Antigravity](https://img.shields.io/badge/Antigravity-Native-purple.svg)](https://deepmind.google/technologies/gemini/)

O **OmniPress MCP** é um protocolo aberto e agnóstico a nichos para publicação agêntica. Ele capacita agentes de IA (como Antigravity, Claude ou ChatGPT) a ingerir ideias brutas, repositórios de código, decisões judiciais/tributárias, memorandos de políticas públicas ou dados de mercado, transformando-os em artigos completos de alta autoridade e campanhas estruturadas para redes sociais.

O OmniPress é projetado para ser **verdadeiramente "Omni"**:
- **Omni-Domínio**: Motor de ingestão universal expansível através de Skills modulares por nicho.
- **Omni-Plataforma**: Distribuição nativa para LinkedIn, X (Twitter), Meta Threads, Reddit, Webhooks (n8n/Make) e arquivos Markdown locais.
- **Omni-Ambiente (Dual-Runtime)**: Motor em Node.js com **zero dependências externas** + implementação completa em Python (FastMCP).

---

## 🎯 Visão e Objetivos

Especialistas, engenheiros de software, tributaristas, pesquisadores e gestores públicos perdem horas adaptando manualmente seu conhecimento para formatos fragmentados em diferentes redes sociais.

O OmniPress resolve isso oferecendo um fluxo unificado de **Publicação Agêntica**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. INGESTÃO UNIVERSAL                          │
│   Ideias Brutas • Diffs de Git • Decisões Tributárias • Relatórios TI  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    2. RUNTIME DE SKILLS MODULARES                       │
│   Cada nicho possui uma Skill dedicada que define tom, estilo e jargão: │
│   ├── Engenharia de Software e TI     ├── Direito Tributário e Perícia  │
│   ├── Gestão Pública e GovTech        ├── Finanças, Cripto e Mercados   │
│   └── Pesquisa Científica/Acadêmica   └── Jornada de Founders / Produto │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  3. ESCUDO DE PRIVACIDADE E SEGREDOS                    │
│   Mascaramento automático de chaves de API, processos CNJ, CPFs e LGPD  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                    4. SINCRONIZAÇÃO MULTI-CANAL                         │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐│
│  │   LinkedIn    │ │  X (Twitter)  │ │  Meta Threads │ │    Reddit     ││
│  │  (Autoridade) │ │   (Threads)   │ │ (Conversas)   │ │  (Subreddits) ││
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘│
│          │                 │                 │                 │        │
│          └─────────────────┴────────┬────────┴─────────────────┘        │
│                                     ▼                                   │
│                        ┌────────────────────────┐                       │
│                        │ Artigo Long-Form .md   │                       │
│                        │ (Substack/Jusbrasil)   │                       │
│                        └────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Pilares Fundamentais

### 1. Verdadeiramente Omni-Domínio (Skills Modulares por Nicho)
O OmniPress separa o **motor de distribuição técnica** (ferramentas MCP) da **inteligência de redação** (Skills do Agente).
Você pode produzir qualquer tipo de artigo ativando ou criando uma Skill especializada em `.agents/skills/<nicho>`:
- **`tech-architecture`**: Análises profundas de arquitetura de software, trade-offs de engenharia e notas de release.
- **`tax-and-legal`**: Análises tributárias, pareceres de conformidade e perícias judiciais com proteção estrita de segredo de justiça e LGPD.
- **`govtech-civic`**: Políticas públicas, modernização municipal e transparência governamental.
- **`science-research`**: Sínteses acadêmicas, divulgação científica e análise metodológica.
- **`founder-buildinpublic`**: Construção em público, métricas de crescimento e aprendizados de produto.

### 2. Escudo Universal de Privacidade e Segredos
Antes de qualquer rascunho ser colocado na fila ou arquivado, o OmniPress executa uma varredura automática:
- **Credenciais Técnicas**: Mascara chaves de API, tokens Bearer/JWT e segredos de ambiente.
- **Identificadores Legais e Pessoais**: Mascara números de processos judiciais (padrão CNJ `0000000-00.0000.0.00.0000`), CPFs, CNPJs, e-mails e telefones.

### 3. Distribuição em 5 Formatos Sincronizados
A partir de um único conceito central, o OmniPress produz:
1. **Artigo Completo**: Arquivo Markdown com frontmatter YAML para Substack, Medium, Jusbrasil ou blogs estáticos.
2. **Post para o LinkedIn**: Gancho de retenção, tópicos de impacto, pergunta de engajamento e hashtags profissionais.
3. **Thread para o X (Twitter)**: Arco narrativo conciso em 3 a 5 tweets.
4. **Post para o Meta Threads**: Conteúdo conversacional e focado em comunidade.
5. **Postagem para o Reddit**: Publicação sem firulas de marketing direcionada para subreddits específicos (`r/webdev`, `r/programming`, `r/direito`, `r/SideProject`).

### 4. Arquitetura Dual-Runtime
- **Node.js (18+)**: **Zero dependências externas**—utiliza apenas módulos nativos (`node:fs`, `node:crypto`, `readline`, `fetch`). Não necessita de `npm install`!
- **Python (3.10+)**: Servidor FastMCP estruturado com herança de adaptadores (`BasePublisherAdapter`).

---

## ⚡ Instalação e Testes

### 1. Testes Automatizados
Execute a suíte de testes com 6 cenários de validação no Node.js:
```bash
npm test
# ou: node tests/test_omnipress.js
```

### 2. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```
*(O OmniPress funciona perfeitamente mesmo sem chaves de API externas, salvando artigos localmente e formatando as postagens para cópia manual).*

Consulte o [Guia de Configuração de Contas (docs/SETUP_GUIDE.pt-BR.md)](docs/SETUP_GUIDE.pt-BR.md) para conectar:
- **Buffer**: Fila de rascunhos para LinkedIn, X e Meta Threads.
- **Reddit**: Envio direto para subreddits via aplicativo Script oficial do Reddit.
- **Webhooks**: Disparo de eventos para n8n, Make, Slack ou Telegram.

---

## 🤖 Integração com o Antigravity

Configure o OmniPress no arquivo global `~/.gemini/config/mcp_config.json`:

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

---

## 🛠️ Ferramentas MCP Disponíveis

| Ferramenta | Finalidade |
| :--- | :--- |
| `omnipress_publish_article` | Salva o artigo completo no arquivo local organizado por `AAAA/MM/` com frontmatter YAML e filtro LGPD/Segredo de Justiça. |
| `omnipress_queue_post` | Envia postagens para a fila de rascunhos do LinkedIn, X, Threads ou Reddit. |
| `omnipress_inspect_content` | Utilitário isolado para checar texto em busca de credenciais, processos judiciais ou dados sensíveis. |
| `omnipress_list_recent` | Lista os artigos recentemente salvos e seus metadados. |

---

## 📚 Documentação e Wiki

- **[Wiki Oficial no GitHub](https://github.com/ismaelsoilet/omnipress-mcp/wiki)**: Guias de arquitetura e runbooks detalhados.
- **[Guia de Criação de Skills para Nichos](https://github.com/ismaelsoilet/omnipress-mcp/wiki/Creating-Niche-Skills)**: Como criar skills para qualquer área.
- **[Guia de Contas (docs/SETUP_GUIDE.pt-BR.md)](docs/SETUP_GUIDE.pt-BR.md)**
- **[Diretrizes para Agentes de IA (AGENTS.md)](AGENTS.md)**

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
