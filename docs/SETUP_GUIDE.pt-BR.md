# ⚙️ Guia de Configuração de Contas e Uso do OmniPress

[🇺🇸 English Version](SETUP_GUIDE.md) | [🇧🇷 Versão em Português](SETUP_GUIDE.pt-BR.md)

Este documento fornece um guia passo a passo completo para configurar suas contas de publicação no **Buffer** (LinkedIn, X, Threads), **Instagram Graph API**, **Reddit**, **Webhooks** e a **Arquitetura Multi-Canal** no OmniPress MCP.

---

## 1. Configuração do Buffer (LinkedIn, X e Meta Threads)

O Buffer gerencia o agendamento de postagens para LinkedIn, X (Twitter) e Meta Threads. O OmniPress sempre envia os posts como **Rascunhos (Drafts)**, permitindo que você revise e aprove cada publicação pelo celular ou navegador antes de ir ao ar.

### Passo 1.1: Conectar suas Redes Sociais
1. Acesse [buffer.com](https://buffer.com) e faça login na sua conta.
2. Conecte as redes desejadas:
   - **Perfil do LinkedIn ou Página de Empresa**
   - **Perfil do X (Twitter)**
   - **Perfil do Meta Threads**
   - **Instagram Business / Creator** (opcional, caso queira publicar via Buffer)

### Passo 1.2: Obter seu Token de API do Buffer
O OmniPress suporta tanto a API moderna GraphQL quanto a API REST legada do Buffer:
1. Acesse [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).
2. Copie sua chave de API pessoal (**Personal API Key**) ou crie uma aplicação no [Buffer Developer Portal](https://buffer.com/developers/apps/create).
3. Adicione ao seu arquivo `.env`:
   ```env
   BUFFER_API_KEY=seu_token_aqui
   BUFFER_ACCESS_TOKEN=seu_token_aqui
   ```

### Passo 1.3: Descobrir os IDs dos Perfis Conectados
Para descobrir os identificadores únicos de cada rede:
1. Abra no navegador:
   `https://api.bufferapp.com/1/profiles.json?access_token=SEU_ACCESS_TOKEN` (substitua pelo seu token).
2. Localize nos objetos JSON retornados:
   - `service: "linkedin"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "twitter"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "threads"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "instagram"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "youtube"` $\rightarrow$ copie o `"id"` correspondente.

### Passo 1.4: Configurar no arquivo `.env`
```env
BUFFER_API_KEY=seu_token_aqui
BUFFER_ACCESS_TOKEN=seu_token_aqui
BUFFER_LINKEDIN_PROFILE_ID=seu_id_do_linkedin
BUFFER_X_PROFILE_ID=seu_id_do_x
BUFFER_THREADS_PROFILE_ID=seu_id_do_threads
BUFFER_INSTAGRAM_PROFILE_ID=seu_id_do_instagram
BUFFER_YOUTUBE_PROFILE_ID=seu_id_do_youtube
```

> 💡 **Nota Multi-Canal**: Se você gerencia vários canais, pode configurar o `buffer_channel_id` diretamente no arquivo `channels/<slug>/channel.json` de cada canal (em `social.instagram` ou `social.youtube`)! O OmniPress prioriza o ID do canal antes de recorrer ao `.env`.

---

## 2. Configuração do Instagram Graph API (Publicação Direta)

Caso você deseje publicar imagens e carrosséis diretamente no Instagram sem depender do Buffer, você pode usar a API oficial do Instagram Graph:

### Passo 2.1: Pré-requisitos
- Uma conta do **Instagram Profissional** (Comercial ou Criador de Conteúdo).
- Uma **Página do Facebook** vinculada à conta do Instagram.
- Uma aplicação no portal [Meta for Developers](https://developers.facebook.com/) com as permissões:
  - `instagram_basic`
  - `instagram_content_publish`

### Passo 2.2: Adicionar ao `.env`
```env
INSTAGRAM_ACCESS_TOKEN=seu_token_de_longa_duracao_meta
INSTAGRAM_ACCOUNT_ID=seu_instagram_business_account_id
```

---

## 3. Configuração do Reddit (Publicação Direta em Subreddits)

O OmniPress conecta-se diretamente à API oficial do Reddit utilizando um aplicativo do tipo Script. Isso permite publicar postagens de texto com formatação Markdown em comunidades especializadas (ex: `r/programming`, `r/webdev`, `r/SideProject`, `r/direito`, `r/contabilidade`).

### Passo 3.1: Criar o Aplicativo de Desenvolvedor no Reddit
1. Entre na sua conta do Reddit e acesse [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
2. Role até o final da página e clique em **"are you a developer? create an app..."** (ou **"create another app..."**).
3. Preencha os campos:
   - **name**: `omnipress`
   - **Tipo**: Selecione a opção **script** (*personal use script*).
   - **description**: `Automação de Conteúdo OmniPress MCP`
   - **about url**: `https://github.com`
   - **redirect uri**: `http://localhost:8080`
4. Clique em **create app**.

### Passo 3.2: Obter as Credenciais do Reddit
- **Client ID**: A sequência de texto localizada logo abaixo de `personal use script` (cerca de 14 caracteres, ex: `a1B2c3D4e5F6g7`).
- **Client Secret**: O valor do campo `secret` exibido dentro do painel do app.
- **Username**: Seu usuário do Reddit (sem `/u/`).
- **Password**: Sua senha do Reddit.

### Passo 3.3: Configurar no arquivo `.env`
```env
REDDIT_CLIENT_ID=seu_client_id
REDDIT_CLIENT_SECRET=seu_client_secret
REDDIT_USERNAME=seu_usuario
REDDIT_PASSWORD=sua_senha
REDDIT_DEFAULT_SUBREDDIT=SideProject
```

### Passo 3.4: Como Direcionar para Subreddits Específicos
Nas conversas com o Antigravity ou Claude, basta especificar a comunidade desejada:
> *"OmniPress: Publique uma análise sobre auditoria de banco de dados em perícia judicial no Reddit r/direito e r/webdev."*

O agente passará `platforms: ["reddit:direito", "reddit:webdev"]` automaticamente para a ferramenta!

---

## 4. Arquitetura Multi-Canal e Linha de Comando (CLI)

O OmniPress isola completamente marcas e veículos através do diretório `channels/<slug>/`.

### Estrutura de Diretórios de um Canal
```
channels/dossie-historico/
  ├── channel.json             # Metadados, paleta de cores e identidades sociais
  ├── articles/                # Artigos arquivados organizados por AAAA/MM/
  ├── media/
  │   ├── raw/                 # Imagens originais de referência
  │   ├── carousels/           # Decks de carrossel 3:4 gerados
  │   ├── stories/             # Imagens em 9:16
  │   └── highlights/          # Capas de destaques
  └── scripts/                 # Pipelines de produção do canal
```

### Comandos da CLI (`src/cli.py`)
```bash
# 1. Listar todos os canais configurados
python src/cli.py list-channels

# 2. Criar um novo canal com cores e dados da marca
python src/cli.py create-channel fin-pro \
  --name "Finanças Pro" \
  --handle "@financas.pro" \
  --category "finance" \
  --color "#10B981"

# 3. Exibir os detalhes e configurações JSON de um canal
python src/cli.py info-channel fin-pro

# 4. Renderizar carrossel de imagens 3:4 para um post
python src/cli.py build-carousel \
  --channel fin-pro \
  --post juros-compostos \
  --config caminho/para/slides.json \
  --aspect-ratio 3:4
```

### Definindo o Canal Ativo Padrão
No arquivo `.env`:
```env
OMNIPRESS_ACTIVE_CHANNEL=fin-pro
```

---

## 5. Configuração de Webhooks e n8n (Opcional)

O OmniPress despacha cargas JSON completas para pipelines no **n8n**, Make, Slack, Telegram ou endpoints HTTP personalizados.

```env
OMNIPRESS_WEBHOOK_URL=https://seu-n8n.com/webhook/omnipress
OMNIPRESS_WEBHOOK_SECRET=seu_segredo_hmac_opcional
```

Se `OMNIPRESS_WEBHOOK_SECRET` for definido, cada requisição incluirá o cabeçalho `X-OmniPress-Signature` gerado com HMAC SHA-256 para verificação criptográfica da origem.

---

## 6. Configuração no Google Antigravity e Claude Desktop

### No Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "omnipress": {
      "command": "/caminho/ate/omnipress-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNIPRESS_ACTIVE_CHANNEL": "dossie-historico"
      }
    }
  }
}
```

### No Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "omnipress": {
      "command": "python",
      "args": ["/caminho/ate/omnipress-mcp/src/server.py"],
      "env": {
        "ARTICLES_DIR": "/caminho/ate/omnipress-mcp/articles"
      }
    }
  }
}
```

---

## 7. Verificação e Testes

Para garantir que todos os adaptadores e o motor de canais estão funcionando perfeitamente:

```bash
# Executar a suíte de testes em Python:
uv run pytest -v

# Executar a checagem de tipos do Remotion / TypeScript:
npm run typecheck
```
