# Inventário de Scripts Legados — dossie-historico

> Scripts remanescentes que ainda não foram migrados para receitas declarativas.
> Cada linha indica a engine/comando universal que deve substituí-lo antes da remoção.

Total: **83** scripts.

## Captions

| Script | Substituto universal |
|---|---|
| `episodios/ep01_exercito_fantasma/documentario/scripts/dump_ep02_words.py` | `omnipress align-captions --verify` |
| `episodios/ep01_exercito_fantasma/documentario/scripts/generate_canonical_ep02_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep01_exercito_fantasma/shorts/short_01/scripts/align_short_02_voiceover.py` | `omnipress align-captions --verify` |
| `episodios/ep01_exercito_fantasma/shorts/short_01/scripts/generate_canonical_ep02_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/align_short_03_voiceover.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/analyze_raw_voice_ep03.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/dump_ep03_words.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/generate_canonical_short03_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/get_reels_scene_timings.py` | `omnipress align-captions --verify` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/inspect_short03_gaps.py` | `omnipress align-captions --verify` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/align_short_04_voiceover.py` | `omnipress align-captions --verify` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/generate_canonical_short04_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/setup_short04_media_and_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/documentario/scripts/check_odessa_end.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/documentario/scripts/dump_all_acts_words.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/documentario/scripts/dump_words.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/documentario/scripts/generate_canonical_episode_01_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/documentario/scripts/inspect_ep01_captions.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/shorts/short_01/scripts/align_short_01_user_audio.py` | `omnipress align-captions --verify` |
| `episodios/ep06_derinkuyu/shorts/short_01/scripts/extract_short_01_captions.py` | `omnipress align-captions --verify` |
| `recursos_globais/utilitarios/analyze_pauses.py` | `omnipress align-captions --verify` |
| `recursos_globais/utilitarios/generate_canonical_captions.py` | `omnipress align-captions --verify` |

## Cenas/Shorts

| Script | Substituto universal |
|---|---|
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/build_bandeira_slides.py` | `omnipress documentary --recipe documentary_recipe.json` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/generate_short04_visuals.py` | `omnipress documentary --recipe documentary_recipe.json` |
| `episodios/ep04_operacao_mincemeat/shorts/short_01/scripts/build_authentic_archive_slides.py` | `omnipress documentary --recipe documentary_recipe.json` |
| `episodios/ep04_operacao_mincemeat/shorts/short_01/scripts/generate_short05_visuals.py` | `omnipress documentary --recipe documentary_recipe.json` |
| `episodios/ep06_derinkuyu/documentario/scripts/build_authentic_documentary_slides.py` | `omnipress documentary --recipe documentary_recipe.json` |
| `episodios/ep06_derinkuyu/documentario/scripts/generate_episode_slides.py` | `omnipress documentary --recipe documentary_recipe.json` |

## Outros

| Script | Substituto universal |
|---|---|
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/setup_short03_assets.py` | `Avaliar manualmente` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/verify_and_distribute_reels_88s.py` | `Avaliar manualmente` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/verify_short04_render.py` | `Avaliar manualmente` |
| `episodios/ep04_operacao_mincemeat/documentario/roteiros/build_roteiro_json.py` | `Avaliar manualmente` |
| `episodios/ep06_derinkuyu/documentario/scripts/format_documentary_widescreen_16x9.py` | `Avaliar manualmente` |
| `episodios/ep06_derinkuyu/shorts/short_01/scripts/generate_short_01_voiceover.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/create_carousel_slides.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/download_and_prep_mary_celeste_bgs.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/download_historical_assets.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/fetch_real_historical_assets.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/prepare_backgrounds.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/prepare_los_angeles_backgrounds.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/prepare_mascaras_chumbo_backgrounds.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/search_historical_assets.py` | `Avaliar manualmente` |
| `recursos_globais/utilitarios/surgical_debreather.py` | `Avaliar manualmente` |

## Thumbnail

| Script | Substituto universal |
|---|---|
| `episodios/ep01_exercito_fantasma/documentario/scripts/build_thumbnail_exercito_borracha_16x9.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep01_exercito_fantasma/shorts/short_01/scripts/build_vertical_thumbnail_exercito_borracha.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/build_vertical_thumbnail_praga_danca.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/build_vertical_thumbnail_cores_bandeira.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep03b_cores_da_bandeira/documentario/scripts/generate_storyboard_guide.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep03b_cores_da_bandeira/documentario/scripts/generate_thumbnails_ep03b.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep03b_cores_da_bandeira/documentario/scripts/generate_thumbnails_ep03b_v2.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep03b_cores_da_bandeira/documentario/scripts/generate_thumbnails_ep03b_v3.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |
| `episodios/ep06_derinkuyu/shorts/short_01/scripts/build_vertical_thumbnail_derinkuyu.py` | `omnipress thumbnail --recipe thumbnail_recipe.json` |

## Utilitário

| Script | Substituto universal |
|---|---|
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/inspect_ep03_voice.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `episodios/ep03_cores_da_bandeira/shorts/short_01/scripts/inspect_flag.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/build_full_pack.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/check_1963_audio.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/check_all_durations.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/check_ff_target.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/check_narrative_markers.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/deploy_rendered_video.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/find_tools.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/inspect_audio_start.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/inspect_ghost_army_images.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/inspect_raw_images.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/inspect_temp_media.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/inspect_voiceover.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/install_ffmpeg_bin.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/test_audio_env.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/test_gap_caps.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/test_whisper_slice.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/utilitarios/verify_video_deliverable.py` | `omnipress doctor / omnipress assets / omnipress deploy` |
| `recursos_globais/vinhetas/inspect_intro_audio.py` | `omnipress doctor / omnipress assets / omnipress deploy` |

## Áudio

| Script | Substituto universal |
|---|---|
| `episodios/ep01_exercito_fantasma/documentario/scripts/copy_ep02_soundtracks.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep01_exercito_fantasma/documentario/scripts/master_ep02_audio.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep01_exercito_fantasma/documentario/scripts/mix_ep02_soundtrack.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep01_exercito_fantasma/shorts/short_01/scripts/prepare_short02_soundtrack.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/build_reels_88s_audio.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep02_praga_da_danca/shorts/short_01/scripts/master_voiceover_short03.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep06_derinkuyu/documentario/scripts/mix_episode_soundtrack.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `episodios/ep06_derinkuyu/documentario/scripts/remaster_odessa.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `recursos_globais/trilhas_sonoras/master_music_track.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `recursos_globais/trilhas_sonoras/sync_soundtracks.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
| `recursos_globais/utilitarios/clean_and_master_voiceover.py` | `omnipress master-audio --mix-bed / universal_audio.mix_soundtrack` |
