# Template de Campanha / Postagem — Perfil Pessoal & Social-First

> **Arquétipo**: `personal_brand` / `social_persona`  
> **Objetivo**: Publicações de alto impacto para **LinkedIn**, **X (Twitter)**, **Instagram** e artigos long-form (**Dev.to, Substack, Medium, Ghost**), sem dependência de produção pesada de vídeo.

---

## 🎯 Estrutura da Campanha
Cada pasta de campanha representa um tema, artigo ou insight central desdobrado nos formatos sociais:

- `artigo.md`: Artigo técnico, caso de uso ou análise profunda em Markdown com YAML frontmatter.
- `carousel_recipe.json`: Receita declarativa para compilar carrossel visual 3:4 ou 4:5 via `omnipress carousel`.
- `posts/`: Textos específicos adaptados ao algoritmo e público de cada rede:
  - `linkedin_post.md`: Gancho forte, insights em bullet points, pergunta para debate e hashtags.
  - `x_thread.md`: Sequência conectada de 3 a 5 micro-posts (280 chars cada).
  - `instagram_copy.md`: Legenda persuasiva com quebras de linha e chamada para salvar.
- `midias/`: Diagramas de arquitetura, capturas de tela, fotos de acervo ou ilustrações.

---

## 🚀 Como Publicar

### 1. Gerar o Carrossel Visual (Opcional):
```bash
omnipress carousel --recipe channels/<seu-perfil>/campanhas/<nome-da-campanha>/carousel_recipe.json --all
```

### 2. Publicar Artigo Long-Form no Dev.to ou Ghost:
```bash
omnipress publish-article --file channels/<seu-perfil>/campanhas/<nome-da-campanha>/artigo.md --target devto
```

### 3. Disparar / Agendar no LinkedIn, X e Instagram:
Via receita JSON ou direto no Buffer MCP:
```bash
omnipress publish --recipe channels/<seu-perfil>/campanhas/<nome-da-campanha>/post_recipe.json
```
