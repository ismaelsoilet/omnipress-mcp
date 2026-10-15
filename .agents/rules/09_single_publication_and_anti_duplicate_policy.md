# Rule 09 — Single Publication & Anti-Duplicate Policy (Política de Publicação Única e Anti-Duplicação)

> **Priority**: MANDATORY (Obrigatório para todos os agentes e adaptadores do OmniPress).

---

## 🇺🇸 English Guidelines

### 1. The Exactly-Once Publishing Contract
- Every piece of social content (Instagram carousels, LinkedIn posts, X threads) must be published or scheduled **EXACTLY ONCE**.
- Duplicating posts, sending multiple copies of the same creative, or leaving concurrent scheduled entries of the same topic in the queue is strictly prohibited.

### 2. Mandatory Pre-Publish Verification
Before calling `create_post` or any publishing tool:
1. **Query Channel Queue:** Query the channel's active queue and recent posts via `list_posts` to check if the post topic has already been marked as `sent` or `scheduled`.
2. **Handle Revisions Cleanly:** If a post is already scheduled and needs to be replaced with a revised version, **delete the prior post first** via `delete_post` before creating the new one. Never leave both active.
3. **Check Live Status:** If the post is already `sent` (live on the social network), do not publish a second copy unless the user explicitly and unmistakably commands a full overwrite/repost.

### 4. Automated Protection: The 5-Gate PublishingShield Engine
To enforce Rule 09 programmatically at runtime, OmniPress implements [`PublishingShield`](../../src/core/publishing_shield.py):
1. **Gate 1 (Dummy / Placeholder Test Interceptor)**:
   - Blocks strings like `"teste"`, `"test"`, `"testing"`, `"asdf"`, `"hello world"`, or any text under 12 characters when dispatched live with `mode="shareNow"`.
   - Prevents debug payloads or technical verification texts from accidentally broadcasting to real audience feeds.
2. **Gate 2 (Media Requirement Validator for Instagram)**:
   - Instagram strictly prohibits text-only updates. Dispatches with zero media URLs are aborted immediately before making network requests.
3. **Gate 3 (Platform Character Limit Enforcement)**:
   - **Instagram (Buffer GraphQL)**: Hard cutoff at **2,196 characters** (prevents upstream GraphQL mutation crashes).
   - **X / Twitter**: Hard cutoff at **280 characters**.
   - **Threads**: Hard cutoff at **500 characters**.
   - **LinkedIn**: Hard cutoff at **3,000 characters**.
   - The shield reports the exact character count and excess characters to prune.
4. **Gate 4 (Deterministic Idempotency Ledger)**:
   - Located at `media/staging/publishing_ledger.json`.
   - Computes a deterministic SHA-256 fingerprint:
     $$\text{Fingerprint} = \text{SHA256}(\text{channel\_id} \parallel \text{first\_30\_words} \parallel \text{sorted\_media\_urls})$$
   - Duplicate dispatches within a 24-hour window are strictly rejected unless explicit bypass (`force=True`) is passed.
5. **Gate 5 (Native API Metadata & Clean Deletion)**:
   - Instagram posts dispatched via Buffer automatically receive required `metadata.instagram.type = "post"` and `shouldShareToFeed = true`.
   - Obsolete scheduled posts are purged using native GraphQL `delete_post` to guarantee clean queue states.

---

## 🇧🇷 Diretrizes em Português

### 1. Princípio da Publicação Única (Exactly-Once)
- Todo conteúdo (carrosséis do Instagram, posts do LinkedIn, threads do X) deve ser publicado ou agendado **EXATAMENTE UMA VEZ**.
- É estritamente proibido publicar 2 ou mais vezes o mesmo post, gerar cópias duplicadas na fila ou manter agendamentos concorrentes do mesmo dossiê.

### 2. Verificação Obrigatória Antes de Publicar
Antes de invocar `create_post` ou qualquer adaptador de rede social:
1. **Consultar a Fila do Canal:** Verificar posts recentes e agendados via `list_posts` para confirmar se o tema já foi enviado (`status: sent`) ou está agendado (`status: scheduled`).
2. **Substituição Limpa de Versões:** Se uma publicação agendada precisar ser ajustada, **remova o agendamento anterior** usando `delete_post` antes de criar o novo. Nunca mantenha duas cópias na fila do Buffer.
3. **Respeito ao Conteúdo Já Publicado:** Se o post já está no ar (`sent`), não crie outra publicação para o mesmo material, a menos que o usuário dê ordem explícita para republicar.

### 3. Tratamento de Limites de Velocidade (Anti-Spam da Meta/Instagram)
- APIs sociais aplicam barreiras de velocidade quando múltiplos posts são disparados em menos de 1 hora (*"Instagram flagged this post as potential spam"*).
- Diante dessa resposta:
  - **Jamais realize retentativas circulares imediatas (`shareNow`).**
  - **Exclua o post com erro imediatamente** via `delete_post` para que a fila do Buffer permaneça 100% limpa.
  - **NUNCA agende automaticamente o post (`customScheduled` ou `addToQueue`) sem pedido explícito do usuário.** A diretriz do usuário é estritamente publicação imediata ("postar na hora"). Agendar o mesmo texto para depois causa reincidência do bloqueio de spam pelo algoritmo da Meta.
  - **Notifique o usuário imediatamente**, explicando a necessidade de respeitar a janela de cooldown da Meta (1 a 2 horas) e sugerindo pequenas variações na legenda/hashtags antes de tentar novamente.

### 4. Proteção Automatizada: Motor PublishingShield de 5 Portões
Para assegurar o cumprimento programático da Regra 09 em tempo de execução, o OmniPress implementa o [`PublishingShield`](../../src/core/publishing_shield.py):
1. **Portão 1 (Interceptor de Textos de Teste e Placeholders)**:
   - Intercepta textos como `"teste"`, `"test"`, `"asdf"`, `"hello world"` ou mensagens menores que 12 caracteres enviadas ao vivo com `mode="shareNow"`.
   - Impede que testes técnicos ou de depuração vazem no ar para contas reais.
2. **Portão 2 (Exigência Mandatória de Mídia no Instagram)**:
   - O Instagram não suporta posts sem imagem. Qualquer tentativa sem `media_urls` é abortada antes do disparo de rede.
3. **Portão 3 (Trava Rígida de Limite de Caracteres por Plataforma)**:
   - **Instagram (Buffer GraphQL)**: Teto de **2.196 caracteres** (evita falhas de mutação no GraphQL).
   - **X / Twitter**: Teto de **280 caracteres**.
   - **Threads**: Teto de **500 caracteres**.
   - **LinkedIn**: Teto de **3.000 caracteres**.
   - Retorna o número exato de caracteres em excesso a serem enxugados.
4. **Portão 4 (Livro-Razão de Idempotência Anti-Duplicação)**:
   - Armazenado em `media/staging/publishing_ledger.json`.
   - Gera um fingerprint SHA-256 único:
     $$\text{Fingerprint} = \text{SHA256}(\text{channel\_id} \parallel \text{primeiras\_30\_palavras} \parallel \text{urls\_ordenadas})$$
   - Bloqueia automaticamente disparos idênticos no mesmo canal num intervalo de 24 horas.
5. **Portão 5 (Metadados Nativos e Exclusão Limpa de Rascunhos)**:
   - Injeção obrigatória de `metadata.instagram.type = "post"` e `shouldShareToFeed = true` nos envios de carrossel.
   - Purgamento atômico de rascunhos obsoletos via mutação GraphQL `delete_post`.

