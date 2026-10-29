# Migração — dossie-historico para receitas declarativas

Modo: escrita

> **Nota de versionamento:** `channels/*` é ignorado pelo git (apenas `_template/` é
> versionado). As receitas geradas vivem localmente no workspace do canal. Os scripts
> removidos foram substituídos pelas receitas e pelo motor universal; o conteúdo
> editorial (slides e legendas) está preservado nos JSONs.

Episódios migrados: **27**

| Episódio | Script | Slides | Assets faltando | Publish |
|---|---|---:|---:|---|
| `ep03_cores_da_bandeira` | `(migrated)` | 6 | 0 | não |
| `ep04_operacao_mincemeat` | `(migrated)` | 6 | 0 | não |
| `ep05_codex_gigas` | `(migrated)` | 6 | 0 | não |
| `ep06_derinkuyu` | `(migrated)` | 8 | 0 | não |
| `ep07_castelo_itter` | `(migrated)` | 8 | 0 | não |
| `ep08_passo_dyatlov` | `(migrated)` | 8 | 0 | não |
| `ep09_garotas_do_radio` | `(migrated)` | 8 | 0 | não |
| `ep10_mascaras_de_chumbo` | `(migrated)` | 8 | 0 | não |
| `ep11_batalha_de_los_angeles` | `(migrated)` | 8 | 0 | não |
| `ep12_mary_celeste` | `(migrated)` | 8 | 0 | não |
| `ep13_operacao_prato` | `(migrated)` | 8 | 0 | sim |
| `ep14_voo_967` | `(migrated)` | 8 | 0 | sim |
| `ep15_percy_fawcett` | `(migrated)` | 8 | 0 | sim |
| `ep16_poco_superprofundo_kola` | `(migrated)` | 8 | 0 | sim |
| `ep17_operacao_highjump` | `(migrated)` | 8 | 0 | sim |
| `ep18_projeto_mkultra` | `(migrated)` | 8 | 0 | sim |
| `ep19_farol_ilhas_flannan` | `(migrated)` | 8 | 0 | sim |
| `ep20_voo_19` | `(migrated)` | 8 | 0 | sim |
| `ep21_manuscrito_voynich` | `(migrated)` | 8 | 0 | sim |
| `ep22_principe_de_asturias` | `(migrated)` | 8 | 0 | sim |
| `ep23_ss_baychimo` | `(migrated)` | 8 | 0 | sim |
| `ep24_revolta_da_chibata` | `(migrated)` | 8 | 0 | sim |
| `ep25_camp_century` | `(migrated)` | 8 | 0 | sim |
| `ep26_ilha_da_trindade` | `(migrated)` | 8 | 0 | sim |
| `ep27_expedicao_franklin` | `(migrated)` | 8 | 0 | sim |
| `ep28_operacao_acoustic_kitty` | `(migrated)` | 8 | 0 | sim |
| `ep29_kaspar_hauser` | `(migrated)` | 8 | 0 | sim |

## Substituição por comandos universais

```bash
# Renderiza e publica cada carrossel migrado:
uv run omnipress carousel --recipe channels/dossie-historico/episodios/<ep>/carrossel/carousel_recipe.json --all
```

## Scripts legados ainda pendentes

Os scripts de áudio, captions, thumbnails, shorts e utilitários que ainda não
foram migrados estão inventariados em [`docs/LEGACY_SCRIPTS.md`](./LEGACY_SCRIPTS.md),
com o comando/engine universal que deve substituí-los antes da remoção.
