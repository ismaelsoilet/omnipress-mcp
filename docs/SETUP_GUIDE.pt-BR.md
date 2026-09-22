# ⚙️ Guia de Configuração de Contas e Uso do OmniPress

[🇺🇸 English Version](SETUP_GUIDE.md) | [🇧🇷 Versão em Português](SETUP_GUIDE.pt-BR.md)

Este documento fornece um passo a passo completo para configurar suas contas de publicação no **LinkedIn**, **X (Twitter)**, **Meta Threads**, **Reddit** e **Webhooks** no OmniPress MCP.

---

## 1. Configuração do Buffer (LinkedIn, X e Meta Threads)

O Buffer gerencia o agendamento de postagens para LinkedIn, X e Meta Threads. O OmniPress sempre envia os posts como **Rascunhos (Drafts)**, permitindo que você revise e aprove cada publicação pelo celular ou navegador antes de ir ao ar.

### Passo 1.1: Conectar suas Redes Sociais
1. Acesse [buffer.com](https://buffer.com) e crie uma conta gratuita.
2. Conecte as redes desejadas:
   - **Perfil do LinkedIn ou Página de Empresa**
   - **Perfil do X (Twitter)**
   - **Perfil do Meta Threads**

### Passo 1.2: Obter o Access Token de Desenvolvedor
1. Acesse o [Portal de Desenvolvedores do Buffer](https://buffer.com/developers/apps/create).
2. Crie uma nova aplicação:
   - **Name**: `OmniPress-MCP`
   - **Description**: `Assistente de Publicação Agêntica`
   - **Callback URL**: `http://localhost`
3. Após criar, abra as configurações da aplicação e localize o **Developer Access Token**.
4. Copie esse token.

### Passo 1.3: Descobrir os IDs dos Perfis Conectados
Para descobrir os identificadores únicos de cada rede:
1. Abra no navegador:
   `https://api.bufferapp.com/1/profiles.json?access_token=SEU_ACCESS_TOKEN` (substitua pelo seu token).
2. Localize nos objetos JSON retornados:
   - `service: "linkedin"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "twitter"` $\rightarrow$ copie o `"id"` correspondente.
   - `service: "threads"` $\rightarrow$ copie o `"id"` correspondente.

### Passo 1.4: Configurar no arquivo `.env`
```env
BUFFER_ACCESS_TOKEN=seu_token_aqui
BUFFER_LINKEDIN_PROFILE_ID=seu_id_do_linkedin
BUFFER_X_PROFILE_ID=seu_id_do_x
BUFFER_THREADS_PROFILE_ID=seu_id_do_threads
```

---

## 2. Configuração do Reddit (Publicação Direta em Subreddits)

O OmniPress conecta-se diretamente à API oficial do Reddit utilizando um aplicativo do tipo Script. Isso permite publicar postagens de texto com formatação Markdown em comunidades especializadas (ex: `r/programming`, `r/webdev`, `r/SideProject`, `r/direito`, `r/contabilidade`).

### Passo 2.1: Criar o Aplicativo de Desenvolvedor no Reddit
1. Entre na sua conta do Reddit e acesse [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
2. Role até o final da página e clique em **"are you a developer? create an app..."** (ou **"create another app..."**).
3. Preencha os campos:
   - **name**: `omnipress`
   - **Tipo**: Selecione a opção **script** (*personal use script*).
   - **description**: `Automação de Conteúdo OmniPress MCP`
   - **about url**: `https://github.com`
   - **redirect uri**: `http://localhost:8080`
4. Clique em **create app**.

### Passo 2.2: Obter as Credenciais do Reddit
- **Client ID**: A sequência de texto localizada logo abaixo de `personal use script` (cerca de 14 caracteres, ex: `a1B2c3D4e5F6g7`).
- **Client Secret**: O valor do campo `secret` exibido dentro do painel do app.
- **Username**: Seu usuário do Reddit (sem `/u/`).
- **Password**: Sua senha do Reddit.

### Passo 2.3: Configurar no arquivo `.env`
```env
REDDIT_CLIENT_ID=seu_client_id
REDDIT_CLIENT_SECRET=seu_client_secret
REDDIT_USERNAME=seu_usuario
REDDIT_PASSWORD=sua_senha
REDDIT_DEFAULT_SUBREDDIT=SideProject
```

### Passo 2.4: Como Direcionar para Subreddits Específicos
Nas conversas com o Antigravity, basta especificar a comunidade desejada:
> *"OmniPress: Publique uma análise sobre auditoria de banco de dados em perícia judicial no Reddit r/direito e r/webdev."*

O Antigravity passará `platforms: ["reddit:direito", "reddit:webdev"]` automaticamente para a ferramenta!

---

## 3. Configuração de Webhooks e n8n (Opcional)

O OmniPress despacha cargas JSON completas para pipelines no **n8n**, Make, Slack, Telegram ou endpoints HTTP personalizados.

```env
OMNIPRESS_WEBHOOK_URL=https://seu-n8n.com/webhook/omnipress
OMNIPRESS_WEBHOOK_SECRET=seu_segredo_hmac_opcional
```

Se `OMNIPRESS_WEBHOOK_SECRET` for definido, cada requisição incluirá o cabeçalho `X-OmniPress-Signature` gerado com HMAC SHA-256 para verificação criptográfica da origem.

---

## 4. Pasta de Armazenamento Local (Markdown)

Por padrão, os artigos são organizados em:
```
articles/
└── AAAA/
    └── MM/
        └── AAAA-MM-DD-titulo-do-artigo.md
```

Para armazenar em uma pasta customizada (ex: cofre do Obsidian ou pasta de blog estático):
```env
ARTICLES_DIR=C:/Users/Ismael/Documents/MeuCofre/Artigos
```

---

## 5. Testes e Validação no Antigravity

1. Execute a suíte de testes unitários:
   ```bash
   npm test
   ```
2. No chat do Antigravity, solicite uma publicação multi-canal:
   > *"OmniPress: Prepare um post anunciando nosso novo projeto open source e coloque na fila para o LinkedIn, Threads e Reddit r/SideProject."*
