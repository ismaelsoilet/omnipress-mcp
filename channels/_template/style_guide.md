# 🎨 Guia de Estilo & Identidade Visual do Canal (Style Guide)

Este documento define as diretrizes estéticas, visuais e de redação para a produção de conteúdo deste canal no **OmniPress MCP**. Todos os criadores e agentes de IA devem seguir estas definições para garantir consistência visual em carrosséis, posts, vídeos e artigos.

---

## 🏛️ 1. Identidade & Conceito da Persona

- **Nome do Canal / Perfil**: Nome Oficial ou Marca
- **Handle Canônico**: `@seuperfil`
- **Arquétipo**: `personal_brand` (Perfil Pessoal de Liderança Técnica) | `media_channel` (Canal de Mídia / Produtora)
- **Tom de Voz**: Analítico, direto, embasado em dados e fatos, sem jargões vazios de autoajuda.
- **Público-Alvo**: Profissionais, tomadores de decisão, engenheiros, advogados ou entusiastas de investigações aprofundadas.

---

## 🎨 2. Paleta de Cores (Design Tokens)

As cores podem ser configuradas no [`channel.json`](channel.json) sob `visual_identity.palette`:

| Token | Código Hex | Descrição de Uso |
|---|---|---|
| `primary` | `#3B82F6` (ou `#D4AF37`) | Cor de destaque da marca, botões, selos e bordas ativas. |
| `background` | `#FFFFFF` (claro) / `#0A0C10` (escuro) | Fundo da lâmina ou do slide. |
| `card_background` | `#F8FAFC` (claro) / `#0F172A` (escuro) | Fundo do card protetor de texto ou container de conteúdo. |
| `text` | `#0F172A` (escuro) / `#FFFFFF` (claro) | Cor principal das headlines e textos de leitura. |
| `secondary_text` | `#64748B` (claro) / `#E2E8F0` (escuro) | Subtítulos, handles, datas e rodapés. |
| `accent` | `#F59E0B` | Cor para ênfases, termos-chave, datas e marcadores de tópicos (■). |
| `border` | `#E2E8F0` / `#1E293B` | Contornos sutis de imagens, cards e inputs de busca. |

---

## ✍️ 3. Tipografia & Famílias de Fontes

O OmniPress suporta nativamente 3 famílias tipográficas com segurança multiplataforma:

1. **Sans-Serif (`sans`)**: Moderna, limpa e altamente legível em telas mobile (ex: DejaVu Sans, Helvetica, Arial). Padrão para perfis tech e social-proof (`tweet_card`).
2. **Serif (`serif`)**: Sofisticada, editorial, clássica e de alto valor percebido (ex: DejaVu Serif, Georgia, Times). Ideal para tutoriais minimalistas (`minimal_dark`), artigos de opinião e história.
3. **Monospace (`mono`)**: Técnica, precisa e focada em engenharia (ex: DejaVu Sans Mono). Utilizada para linhas de comando, snippets de código e parâmetros.

---

## 📐 4. Presets Visuais & Parametrização por Canal

O motor [`CarouselBuilder`](file:///home/ismaelsoilet/omnipress-mcp/src/engine/carousel_builder.py) é 100% desacoplado e orientado a dados. Cada canal define seus parâmetros no [`channel.json`](file:///home/ismaelsoilet/omnipress-mcp/channels/_template/channel.json) via:
- `layout_parameters`: Margens (`margin_ratio`), proporções tipográficas (`headline_scale`, `body_scale`, `step_scale`, `footer_scale`), raio de borda (`border_radius`), transparência do card (`card_alpha`), e tamanho do avatar (`avatar_size_ratio`).
- `semantic_tags`: Mapeamento de tags para cores hex (ex: `"DICA": "#8B5CF6"`).
- `semantic_categories`: Mapeamento de categorias (`danger`, `success`, `warning`, `accent`) para palavras-chave personalizadas do nicho do canal.

O motor oferece 4 presets universais:

### Preset A: `tweet_card` (Social Proof & Opinião Ágil)
- **Quando Usar**: Posts de posicionamento, estudos de caso, análises políticas/estratégicas, reflexões com fotos reais ou comparativos.
- **Elementos Visuais**:
  - Cabeçalho de rede social no topo: Avatar circular do autor, nome em negrito, **selo azul de verificado**, handle `@seuperfil`.
  - Headline em fonte Sans-serif bold destacada.
  - Subtítulo / Lead com ênfases seletivas em negrito.
  - Imagem ou Comparativo abaixo: 1 foto ampla ou 2 fotos lado a lado com cantos arredondados e borda fina.

### Preset B: `minimal_dark` (Dark Editorial & Tutoriais Passo a Passo)
- **Inspiração**: Estilo Rhaj Teixeira.
- **Quando Usar**: Guias de execução prática, hacks mentais, tutoriais de ferramentas ("Passo 1.", "Passo 2."), frases de impacto.
- **Elementos Visuais**:
  - Fundo preto puro ou grafite profundo (`#08080A`).
  - Tipografia com **Serifa elegante** (`serif`) de alto contraste branco.
  - Identificador de etapa ("Passo 1.") com grande espaçamento vertical.
  - Mockup de Interface Embutido: Campo de busca estilizado (pílula escura com borda suave, termo pesquisado, ícone de lupa e botão '×' de limpar).

### Preset C: `split_editorial` (Autoridade Corporativa & GovTech)
- **Inspiração**: Estilo Portal da Reforma Tributária / Paulo Andrade.
- **Quando Usar**: Análises regulatórias, jurídicas, tributárias, relatórios econômicos e artigos institucionais.
- **Elementos Visuais**:
  - Layout Bipartido:
    - **Metade Superior (45%)**: Fotografia documental real (cenários urbanos, Brasília, tribunais, fábricas).
    - **Recorte Circular Central**: Foto de rosto (headshot) do autor sobrepondo a fronteira entre a foto e o bloco inferior.
    - **Metade Inferior (55%)**: Bloco sólido em azul marinho corporativo (`#0C2333`).
  - Badge de Opinião: Nome da instituição + `NOME DO AUTOR | OPINIÃO`.
  - Marcadores de Tópicos Quadrados: Blocos quadrados dourados/laranja (`■`) alinhados antes das linhas da manchete.
  - Marca d'água no canto inferior direito (ex: `RT` ou sigla da empresa).

### Preset D: `classic_card` (Investigativo & Dossiê Histórico)
- **Inspiração**: Estilo Dossiê Histórico / Cinema Noir.
- **Quando Usar**: Episódios investigativos, história militar, segredos de estado, geopolítica e conteúdo com fotos de arquivo.
- **Elementos Visuais**:
  - Foto de arquivo em tela cheia com vinheta escura superior e gradiente dramático inferior.
  - Selo superior em pílula (`• DOSSIÊ HISTÓRICO | @DOSSIEHISTORICO •`).
  - **Card protetor translúcido escuro** (`rgba(8, 10, 14, 215)`) com borda dourada suave e stroke escuro de segurança nas fontes (Regra 08).

---

## ⚙️ 5. Herança e Sobrescrita por Campanha ou Slide

Qualquer campanha pode adotar ou mesclar presets no [`carousel_recipe.json`](file:///home/ismaelsoilet/omnipress-mcp/channels/_template/campanhas/_template_campanha/carousel_recipe.json):

```json
{
  "channel_slug": "seuperfil",
  "post_slug": "post_estrategia",
  "aspect_ratio": "4:5",
  "preset": "tweet_card",
  "theme_override": {
    "primary": "#3B82F6",
    "background": "#FFFFFF"
  },
  "slides": [
    {
      "layout": "tweet_card",
      "headline": "Não fazer campanha foi a melhor estratégia!",
      "body": "Entenda por que construir uma base sólida supera qualquer anúncio de última hora.",
      "images": ["tarcisio.jpg", "haddad.jpg"]
    },
    {
      "layout": "minimal_dark",
      "step_number": "Passo 1.",
      "headline": "Pesquise por boring history for sleep.",
      "body": "Identifique canais com grande disparidade entre inscritos e visualizações.",
      "ui_mockup": {
        "type": "search_bar",
        "query": "boring history for sleep"
      }
    },
    {
      "layout": "split_editorial",
      "top_image": "esplanada_brasilia.jpg",
      "author_avatar": "foto_autor.jpg",
      "badge_text": "PAULO ANDRADE | OPINIÃO",
      "headline": "CBS e anterioridade\nnonagesimal.\nO Executivo dormiu\nno ponto?",
      "bullet_style": "square",
      "watermark_text": "RT"
    }
  ]
}
```

---

## 📋 6. Regras Editoriais & Redação Social

1. **LinkedIn**:
   - Gancho inicial de até 2 linhas que instigue o clique em "...ver mais".
   - 3 a 5 insights em marcadores objetivos (`•` ou `→`).
   - Pergunta de debate aberta no final para incentivar comentários.
   - 3 a 5 hashtags contextualizadas (ex: `#tecnologia #lideranca #engenharia`).
2. **X (Twitter)**:
   - Posts com no máximo 280 caracteres.
   - Tweets encadeados (threads de 3 a 5 posts) com ritmo rápido e revelações progressivas.
3. **Instagram**:
   - Legendas com quebras de linha limpas.
   - CTA para salvar o carrossel na última lâmina.
