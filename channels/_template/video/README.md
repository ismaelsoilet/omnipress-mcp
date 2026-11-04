# `video/` — Episódios editáveis no Remotion Studio

Esta pasta é opcional e existe para o **fluxo de edição humana** do OmniPress.

Cada episódio gerado por `omnipress video --scaffold-editable` cria sua própria pasta:

```
video/
└── episodes/
    └── <episode-slug>-16x9/
        ├── index.ts                    # registerRoot + composição do episódio
        ├── Episode.tsx                 # um nó JSX por cena (fonte de verdade após o scaffold)
        ├── meta.json                   # hashes, composição, entry point e public_dir
        ├── media.json                  # manifesto de staging (versionado no repo privado do canal)
        ├── data/
        │   ├── captions.ts             # legendas tipadas
        │   └── theme.ts                # cores/fontes resolvidas do channel.json
        ├── video_recipe.editable.json  # recipe para renderizar o episódio editado
        └── public/                     # staging gerado (ignorado pelo git)
```

## Fluxo

1. Gere o `episode_config.json` com `omnipress documentary --recipe ...`.
2. Gere o episódio editável:
   ```bash
   omnipress video --recipe <episode_config.json> --channel <slug> --scaffold-editable
   ```
3. Abra o Studio:
   ```bash
   omnipress studio --channel <slug> --episode <slug>
   ```
4. Edite cenas, textos, cores, keyframes e timing visual.
5. Renderize:
   ```bash
   omnipress video --recipe channels/<slug>/video/episodes/<slug>-16x9/video_recipe.editable.json
   ```

## Cenas suportadas

O motor gera componentes interativos dedicados para:

- `ken-burns`
- `document-reveal`
- `heraldic-surgery` / `image-morph`
- `channel-outro`
- `tactical-map` (`SceneTacticalMap`)
- `stat-counter` (`SceneStatCounter`)
- `video-clip` (`SceneVideoClip`)

Tipos desconhecidos caem em `SceneKenBurns` com aviso.

## Regras

- **Não** edite `media.json` manualmente; ele é regenerado e contém caminhos relativos à raiz do projeto (portátil entre clones).
- Edições manuais em `Episode.tsx`, `index.ts` e `data/*` são protegidas por hash. Reexecutar o scaffold sem `--force` falha; com `--force`, cria backup.
- O `video_recipe.editable.json` não fixa `duration_frames`; a duração da composição em `index.ts` é a autoridade após edições de timing.
- `prune_media` usa o índice `.staging-index.json` para remover somente assets gerados em execuções anteriores; arquivos do usuário e `.gitkeep` são preservados. Episódios antigos sem índice não são podados automaticamente.
- Retiming de `from`/`durationInFrames` pode dessincronizar locução e legendas. Para mudanças narrativas, regenere a partir do JSON e re-alinhe o áudio.
- O áudio permanece travado ao alinhamento da fala (Regra 10).
- `public/` é staging: não versione binários; `media.json` reconstrói tudo.

## Git e backup

`channels/*` é ignorado pelo Git neste repositório; apenas `channels/_template/` é versionado. Portanto, `Episode.tsx`, `index.ts`, `data/*` e `media.json` do seu episódio **não sobem para este repo** — mantenha um repositório privado ou backup separado do canal. O `public/` gerado não precisa ser versionado.
