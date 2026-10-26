# Regra 08 — Padrão de Contraste Visual e Segurança Tipográfica em Carrosséis
# (Visual Contrast and Carousel Legibility Standards)

> **Status:** MANDATÓRIA (Core Engine Rule)  
> **Aplica-se a:** Todos os motores de renderização (`src/engine/carousel_builder.py`), scripts de carrossel em `channels/*/scripts/` e criativos visuais do ecossistema OmniPress.

---

## 🎯 Objetivo & Problema Resolvido
Em carrosséis visuais para redes sociais (Instagram, LinkedIn, X), imagens de fundo com áreas brancas, claras ou com ruído visual intenso (ex.: recortes de jornal, documentos históricos de época, fotografias com neve, ilustrações técnicas ou fundos claros) anulam o contraste de textos renderizados em tipografia branca (`#FFFFFF`), tornando a leitura impossível ou desconfortável para o usuário.

Esta regra torna **obrigatória** a aplicação de mecanismos duplos de proteção de contraste em qualquer elemento textual sobreposto a imagens.

---

## 🛡️ Mecanismos de Segurança Mandatórios no `CarouselBuilder`

Todo slide gerado pelo motor de carrossel **deve conter sem exceção**:

### 1. Fundo Opaco/Translúcido Protetor (Card Backdrop Container)
* O bloco de texto (headline + body) deve ser envelopado em um contêiner escuro translúcido ou opaco (`fill=(8, 10, 14, 215)` ou superior, equivalente a ~85–90% de opacidade).
* O contêiner deve possuir cantos arredondados (`radius=16`), espaçamento interno (*padding*) dinâmico e borda sutil no tom primário da identidade visual do canal (`outline=(*primary_rgb, 60)`).
* O fundo protetor isola as letras de texturas, letras pré-existentes na imagem de fundo e variações brutas de luminância.

### 2. Contorno de Segurança nas Fontes (Text Stroke / Outline)
* **Headline:** Deve aplicar `stroke_width=max(2, int(w * 0.0025))` com `stroke_fill=(4, 5, 8, 255)`.
* **Corpo do Texto (Body):** Deve aplicar `stroke_width=max(1, stroke_w - 1)` com `stroke_fill=(4, 5, 8, 255)`.
* **Rodapé e Badges:** Textos de rodapé (*handle*, paginação e swipe) devem possuir `stroke_width=1` e preenchimento escuro.
* O contorno garante que, mesmo em eventual falha de renderização ou transparência residual, as bordas das letras nunca se fundam com fundos claros.

### 3. Gradiente Inferior Dinâmico (Adaptive Bottom Scrim)
* O gradiente inferior escuro não deve iniciar em uma posição estática arbitrária.
* Ele deve ser calculado dinamicamente com base no ponto inicial do texto:
  $$\text{grad\_start} = \min(h \times \text{gradient\_start\_ratio}, \text{start\_y} - 0.06h)$$
* A curva de transição deve atingir opacidade profunda ($\alpha \ge 240$) antes do início da primeira linha da headline.

### 4. Padrão Mandatório de Ícones de Ação Social (Action Icons) e Destaque Semântico
* **Ícones de Ação Vetoriais (CTA Slides):** Lâminas finais de síntese e Chamada para Ação (CTA) devem **obrigatoriamente renderizar ícones vetoriais nativos** diretamente na lâmina para cada uma das 4 ações sociais:
  - 🔖 **SALVAR (Bookmark Ribbon):** Destaque em tom dourado/âmbar (`#D97706` / `#D4AF37`).
  - 🔄/↗️ **COMPARTILHAR (Share 3-Node Graph):** Destaque em tom verde esmeralda (`#059669` / `#10B981`).
  - 💬 **COMENTAR (Speech Bubble):** Destaque em tom ciano/azul institucional (`#0A66C2` / `#0284C7`).
  - ❤️ **CURTIR (Heart):** Destaque em tom carmim/rosa vibrante (`#E11D48` / `#F43F5E`).
* **Zero Dependência de Emojis Unicode em Imagens:** Motores gráficos não devem depender de glifos unicode de emojis em texto (que frequentemente quebram ou são expurgados por fontes sem suporte a emojis coloridos). O motor deve desenhar as formas vetoriais correspondentes de forma determinística e nítida.
* **Rodapé Social Proof (Preset `tweet_card`):** Em todos os slides no preset `tweet_card`, a barra inferior de rodapé deve exibir os 4 micro-ícones sociais interativos à esquerda (Comentar, Compartilhar, Curtir, Salvar), espelhando o visual nativo das redes sociais.
* **Cores Semânticas Normativas (MITO vs. VERDADE):**
  - **MITO / ERRO / FALSO / PROBLEMA:** Aplicação **obrigatória** de cor Vermelha (`#DC2626` em fundo claro, `#EF4444` em fundo escuro) no marcador indicador e no prefixo em negrito.
  - **VERDADE / FATO / CORRETO / SOLUÇÃO:** Aplicação **obrigatória** de cor Verde (`#059669` em fundo claro, `#10B981` em fundo escuro) no marcador indicador e no prefixo em negrito.

---

## 📐 Tratamento Prévio de Imagens com Fundo Claro

Ao preparar imagens em scripts de pipeline (`prepare_backgrounds.py` ou geração de criativos):
1. **Recortes de Jornal e Documentos:** Devem passar por rebaixamento de brilho/exposição ou vinheta de escurecimento localizado na porção inferior se contiverem texto original conflitante.
2. **Imagens de Alta Luminância:** Nunca assumir que o fundo é escuro. O motor `CarouselBuilder` deve ser executado com `enable_text_card=True` por padrão.

---

## ✅ Critérios de Aceite Visual
1. O texto é perfeitamente legível com zoom de 100% em qualquer tela mobile.
2. Imagens com 100% de fundo branco (`#FFFFFF`) produzem textos com contraste WCAG AAA.
3. A identidade estética do canal (cores primárias, tipografia e badges) permanece preservada e valorizada.
4. Lâminas com MITO/VERDADE evidenciam o contraste vermelho/verde instantaneamente aos olhos do leitor.
5. Lâminas de CTA exibem os 4 ícones vetoriais de ação renderizados com nitidez cristalina.
