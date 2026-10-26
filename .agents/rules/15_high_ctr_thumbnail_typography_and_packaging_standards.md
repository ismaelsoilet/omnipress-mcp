# Regra 15 — Padrão de Tipografia Titânica e Embalagem de Thumbnails de Alto CTR (YouTube Documentaries)

> **Status Normativo**: Mandatório para todos os agentes de IA, designers programáticos e editores de vídeo no ecossistema **OmniPress MCP**.
> **Alvo Primário**: Miniaturas (Thumbnails 16:9) de episódios longos (8 a 30+ min), documentários investigativos, históricos e técnicos no YouTube.
> **Meta Operacional**: Elevação estrutural do CTR (Click-Through Rate) da faixa deficitária (**0,90% a 1,5%**) para a faixa de alta performance (**5,0% a 10,0%+**).

---

## 1. Diagnóstico do Problema & Por Que 0,90% a 1,5% é Crítico

Nos primeiros testes analíticos, identificou-se que as imagens de fundo e montagens geradas possuem excelente qualidade visual, porém o CTR permanece baixo (**0,90% a 1,5%**). No algoritmo do YouTube:
- **< 2,0% de CTR**: O algoritmo classifica a embalagem como desinteressante e interrompe a distribuição em *Browse Features* (Home) e *Suggested Videos*.
- **3,5% a 5,0% de CTR**: Desempenho mediano/baseline.
- **5,5% a 8,5% de CTR**: Alto desempenho; o YouTube acelera impressões para novos públicos.
- **9,0% a 14%+ de CTR**: Conteúdo viral de tração exponencial.

### As 4 Falhas Fatais Identificadas nas Miniaturas Anteriores:
1. **Micro-Tipografia / Efeito "Bula de Remédio"**:
   Fontes entre 20px e 32px no master 1920x1080. Em celulares (onde ocorrem **>75% das visualizações**), a miniatura é exibida com apenas **320px a 380px** de largura no feed e **120px a 160px** no feed de recomendações. Uma fonte de 22px encolhe para **~3,6 pixels** — torna-se uma mancha cinza ilegível.
2. **Sobrecarga Cognitiva (Mural de Textos)**:
   Miniaturas continham até 7 elementos textuais dispersos: badge superior, título linha 1, título linha 2, subtítulo, callout pill, card de metadados com 2 tópicos/bullets e marca d'água. O cérebro humano escaneia feeds em **400 a 700 milissegundos**; diante de um texto longo, o usuário desiste e rola a tela.
3. **Colisão com o Badge de Duração do YouTube (Zona da Morte Inferior Direita)**:
   Elementos cruciais (como chamadas, setas ou detalhes) foram posicionados no canto inferior direito. O YouTube sobrepõe nesse local a etiqueta preta opaca com o tempo do vídeo (ex.: `28:45` ou `1:14:02`), decepando o conteúdo.
4. **Falta de Contraste Periférico Agressivo**:
   Textos sem contorno grosso (stroke) ou colocados sobre fundos claros/ruidosos se perdem na visão periférica do usuário enquanto ele rola o feed rapidamente.

---

## 2. As 8 Leis da Embalagem de Alto CTR (The 8 Laws of High-CTR Packaging)

### Lei 1: O Limite Estrito de 3 a 4 Palavras (The 3-Word Rule)
- A miniatura inteira DEVE conter no máximo **3 a 4 palavras de altíssimo impacto emocional**.
- **PROIBIDO**: Subtítulos explicativos, parágrafos, listas de tópicos com marcadores (bullets), setas com frases longas e cards de metadados técnicos.
- A miniatura **NUNCA** deve explicar a história inteira; ela deve apenas criar um **Choque, Anomalia ou Curiosidade Irresistível**.
- *Exemplos de Ouro*:
  - *"A MAIOR FARSA"* (3 palavras)
  - *"18 ANDARES NO SUBSOLO"* (4 palavras)
  - *"CÓPIA VETADA"* (2 palavras)
  - *"O PACTO SECRETO"* (3 palavras)
  - *"ERA TUDO FALSO!"* (3 palavras)
  - *"NUNCA EXISTIU"* (2 palavras)

---

### Lei 2: Escala Tipográfica Titânica (Titanic Typography Scale)
No canvas master de **1920x1080** (16:9):

| Elemento | Tamanho Mínimo | Tamanho Recomendado | Proporção / Ocupação |
|---|---|---|---|
| **Headline Principal (Linha 1)** | **160px** | **175px – 195px** | Ocupa largura substancial da metade esquerda |
| **Palavra-Chave de Choque (Linha 2)** | **175px** | **190px – 220px** | Destaque máximo em amarelo/vermelho |
| **Badge Único de Contexto (Se houver)** | **50px** | **55px – 65px** | Badge tático com borda e fundo escuro |
| **Micro-Fontes (< 50px)** | **PROIBIDAS** | **PROIBIDAS** | **Tamanho mínimo absoluto no canvas é 50px** |

> [!CAUTION]
> **Tolerância Zero para Fontes Abaixo de 50px**:
> Nenhum caractere com tamanho inferior a 50px pode ser renderizado em uma miniatura de YouTube 16:9. Se um texto precisa ter menos de 50px para caber na tela, ele **NÃO DEVE EXISTIR** na miniatura.

---

### Lei 3: Tipografia Ultra-Pesada e Contorno de Proteção (Safety Heavy Stroke)
- **Famílias Tipográficas Homologadas**:
  - `Anton` (Regular condensado pesado) — Padrão Ouro.
  - `Impact` — Alternativa clássica universal.
  - `Montserrat` (Black 900) — Para badges e selos geométricos.
- **Contorno Obrigatório (Stroke)**:
  - Todas as palavras gigantes devem receber um contorno protetor escuro (`stroke_fill=(0, 0, 0, 255)`) com espessura entre **10px e 16px** (`stroke_width >= 11`).
  - Drop shadow cinematográfico: `0 12px 28px rgba(0, 0, 0, 0.98)` para descolar o texto do fundo tridimensionalmente.

---

### Lei 4: Psicologia Cromática de Visão Periférica (High-CTR Colors)
O olho humano possui maior densidade de bastonetes na visão periférica, altamente sensíveis a contrastes de alta luminância:
1. **Amarelo Alerta / Ouro Chamativo (`#FFE500` / `#FFD700`)**:
   - Cor #1 de conversão de cliques em documentários e investigações.
   - Usar na palavra mais dramática do título (ex.: *"FARSA"*, *"SUBSOLO"*, *"VETADA"*, *"SEGREDO"*).
2. **Branco Puro (`#FFFFFF`)**:
   - Clareza absoluta para a primeira linha do gancho.
3. **Vermelho Alerta / Censura (`#FF2222` / `#E50914`)**:
   - Para termos de proibição, risco, segredo de estado ou choque.
4. **Paleta Bi-Tonal de Choque**:
   - Linha 1: **BRANCO** (`#FFFFFF`)
   - Linha 2: **AMARELO VIBRANTE** (`#FFE500`) ou **VERMELHO** (`#FF2222`)

---

### Lei 5: Isolamento de Fundo por Chiaroscuro (Dark Gradient Shield)
- O texto NUNCA deve ser jogado diretamente sobre detalhes fotográficos, folhagens, multidões ou céu claro.
- A composição DEVE conter um **Gradiente Escuro Tático Chiaroscuro** no lado do texto:
  - Da borda esquerda (X = 0) até X = 450px: **Opacidade quase sólida (alpha 245 a 252)** em tom profundo de preto/azul tático (`rgba(4, 6, 10, 0.96)`).
  - De X = 450px até X = 1100px: Transição suave com curva exponencial atenuando até transparente.
  - Isso garante que a imagem à direita apareça com total nitidez e dramaticidade, enquanto o texto à esquerda tem 100% de contraste garantido.

---

### Lei 6: Escudo de Segurança do YouTube (Anti-Timestamp Shield)
```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  [ BADGE ] (55-65px)                                         │
│                                                              │
│  MANCHETE GIGANTE          [ SUJEITO PRINCIPAL / ]           │
│  (180px - BRANCO)          [ DOCUMENTO SECRETO / ]           │
│                            [ MONTAGEM DRAMÁTICA  ]           │
│  PALAVRA DE CHOQUE!                                          │
│  (200px - AMARELO)                                           │
│                                                              │
│                                              ┌─────────────┐ │
│  ✅ ÁREA TOTALMENTE SEGURA                   │ ⏱ TIMESTAMP │ │
│                                              │   YOUTUBE   │ │
│                                              │(ZONA MORTA) │ │
└──────────────────────────────────────────────┴─────────────┴─┘
```
- **Zona Proibida da Morte**: Canto inferior direito medindo **320px de largura por 140px de altura** (X > 1600, Y > 940).
- Nenhum texto, badge, carimbo, logotipo ou detalhe facial relevante pode ocupar essa área.
- A ancoragem da tipografia titânica deve residir estritamente nos **50% a 55% esquerdos da tela** (X: 80px a 950px, Y: 100px a 920px).

---

### Lei 7: A Regra dos 3 Elementos Focais (The 3-Element Rule)
A miniatura inteira é composta por apenas 3 componentes visuais:
1. **Elemento 1 (O Gancho Visual / Sujeito)**:
   O rosto expressivo, a pintura histórica dramática, o documento antigo vazado, o corte transversal ou a montagem cinematográfica (posicionado na direita ou centro-direita, ocupando 45% a 60% da tela).
2. **Elemento 2 (A Tipografia Titânica)**:
   As 2 a 3 palavras gigantes em fonte Anton de 180px-210px em amarelo/branco com stroke pesado.
3. **Elemento 3 (O Selo ou Ponto de Tensão)**:
   Um único badge de caso real (`● CASO REAL` em 55-65px) OU um carimbo inclinado (`CONFIDENCIAL` / `VETADO`), OU uma seta de alto contraste apontando para uma evidência.

---

### Lei 8: O Teste Mandatório dos 120px no Celular (The 120px Squint Test)
- Antes de qualquer miniatura ser aprovada ou enviada para publicação:
  1. O arquivo deve ser redimensionado para uma versão de visualização mobile em **120px a 320px de largura**.
  2. O operador ou agente deve inspecionar a imagem em escala 100% de 120px.
  3. **Critério de Aprovação**: A mensagem textual principal deve ser lida instantaneamente, sem esforço, em menos de 1 segundo. Se exigir zoom, squint ou esforço mental, a miniatura é **REPROVADA AUTOMATICAMENTE**.

---

## 3. Matriz de Sinergia: Título vs. Miniatura (Zero Redundância)

A miniatura e o título trabalham como um diálogo em duas partes (efeito gangorra):

| Título do Vídeo (Informativo / Pesquisável) | Texto na Thumbnail (Emocional / Choque) | O que NÃO Fazer na Thumbnail |
|---|---|---|
| *"Como o Exército Fantasma Enganou Hitler na 2ª Guerra"* | **ERA TUDO FALSO!** *(Amarelo 200px)* | *"O Exército Fantasma de Hitler"* (Redundante) |
| *"A Cidade Subterrânea de 18 Andares Que Ninguém Explica"* | **18 ANDARES NO SUBSOLO** *(Amarelo/Branco)* | *"Derinkuyu: 1.100 artistas salvaram..."* (Pequeno e chato) |
| *"Por Que a Bandeira do Brasil Não Tem Nada a Ver com as Matas"* | **A MAIOR FARSA!** *(Amarelo 200px)* | *"As Cores da Bandeira Nacional Decreto"* (Bula de remédio) |
| *"A Bandeira do Brasil Inspirada nos EUA Que Durou 4 Dias"* | **CÓPIA VETADA!** *(Vermelho/Branco)* | *"Deodoro vetou a bandeira provisória"* (Sem impacto) |
| *"O Mistério da Praga da Dança de 1518 em Estrasburgo"* | **ELES NÃO PARAVAM!** *(Branco/Vermelho)* | *"Caso 02: Coreomania na Idade Média"* (Acadêmico demais) |

---

## 4. Checklist de Aprovação Pré-Publicação de Thumbnails

- [ ] **Contagem de Palavras**: A miniatura contém no máximo 3 ou 4 palavras no total?
- [ ] **Tamanho da Fonte Principal**: A headline principal possui tamanho igual ou superior a **160px** (Anton/Impact)?
- [ ] **Tamanho Mínimo de Qualquer Texto**: Todos os textos na tela (inclusive badges) possuem no mínimo **50px**?
- [ ] **Contorno de Segurança**: Todo o texto possui contorno escuro espesso (**>= 10px**)?
- [ ] **Cores de Alta Luminância**: O texto principal utiliza a combinação Branco Puro + Amarelo Alerta (`#FFE500`) ou Vermelho Alerta?
- [ ] **Fundo Chiaroscuro**: Existe um gradiente escuro de isolamento por trás do texto garantindo contraste total?
- [ ] **Escudo do YouTube**: O canto inferior direito (320x140px) está 100% livre de textos e badges?
- [ ] **Regra dos 3 Elementos**: Há no máximo 3 elementos focais no quadro (Sujeito + Tipografia Titânica + Selo)?
- [ ] **Teste dos 120px**: A miniatura foi gerada em preview de 120px e é legível de imediato em tela de celular?
- [ ] **Zero Redundância**: O texto da thumbnail complementa o título do YouTube sem repeti-lo?
