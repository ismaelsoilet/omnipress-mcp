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

### 3. API Velocity & Spam Gate Handling
- Platforms like Instagram / Meta Graph API enforce automated anti-spam velocity limiters (e.g., maximum 1 post every 30–60 minutes via third-party APIs).
- When rapid publishing triggers `"Instagram flagged this post as potential spam"`:
  - **Do NOT execute circular immediate retries (`shareNow`).**
  - **Clean up the failed post immediately** using `delete_post` so no lingering error or unwanted scheduled posts remain in the Buffer queue.
  - **NEVER automatically schedule the post (`customScheduled` or `addToQueue`) without explicit user command.** The user preference is strictly immediate publishing ("postar na hora"). Scheduling identical flagged content to auto-publish later will re-trigger the spam flag.
  - **Report to the user immediately**, explaining the Instagram velocity cooldown (recommend waiting 1–2 hours) and recommending subtle caption/hashtag text variations before retrying.

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
