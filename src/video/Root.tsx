import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import { DocumentaryEpisode, DocumentaryEpisodeProps } from "./compositions/DocumentaryEpisode";
import { DocumentaryShort, DocumentaryShortProps } from "./compositions/DocumentaryShort";
import { ThumbnailEpisode, ThumbnailEpisodeProps } from "./compositions/ThumbnailEpisode";
import { sampleShortCaptions, sampleEpisodeCaptions, short02Captions, short03Captions, short03ReelsCaptions, short04Captions } from "./fixtures/sampleCaptions";
import { ep02DocumentaryConfig } from "./fixtures/ep02DocumentaryConfig";

export const Root: React.FC = () => {
  return (
    <>
      {/* 1. Vinheta 16:9 — Português (YouTube Principal) */}
      <Composition
        id="ChannelIntro-16x9"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "pt",
          channelName: "DOSSIÊ HISTÓRICO",
          badgeText: "ARQUIVO DESCLASSIFICADO // NÍVEL 1",
          subText: "DOCUMENTOS SECRETOS • A HISTÓRIA OCULTA",
          classifiedCode: "REF // TOP-SECRET-TUR-1963",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 2. Vinheta 9:16 — Português (YouTube Shorts / Reels / TikTok) */}
      <Composition
        id="ChannelIntro-9x16"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "pt",
          channelName: "DOSSIÊ HISTÓRICO",
          badgeText: "ARQUIVO DESCLASSIFICADO",
          subText: "HISTÓRIA OCULTA • FATOS REAIS",
          classifiedCode: "REF // 1963-SHORTS",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 3. Vinheta 16:9 — Inglês (Canal Internacional) */}
      <Composition
        id="ChannelIntro-16x9-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "en",
          channelName: "HISTORICAL DOSSIER",
          badgeText: "DECLASSIFIED ARCHIVE // LVL 1",
          subText: "OFFICIAL RECORDS • THE UNTOLD HISTORY",
          classifiedCode: "FILE REF // TOP-SECRET-GLOBAL",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 4. Vinheta 9:16 — Inglês (Shorts Internacional) */}
      <Composition
        id="ChannelIntro-9x16-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "en",
          channelName: "HISTORICAL DOSSIER",
          badgeText: "DECLASSIFIED ARCHIVE",
          subText: "SECRET FILES • UNTOLD HISTORY",
          classifiedCode: "FILE // SHORTS-INTL",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 5. Episódio Documental Completo 16:9 — Piloto Ep 01 Master */}
      <Composition
        id="Episode-Dossie-16x9"
        component={DocumentaryEpisode}
        durationInFrames={15368} // 512.25s (~8m32s @ 30fps) locução 100% íntegra sem cortes
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120, // 4.0s
          config: {
            id: "ep01-cidades-subterraneas",
            title: "3 Cidades Subterrâneas Que a Arqueologia Não Consegue Explicar",
            channelSlug: "dossie-historico",
            language: "pt",
            introProps: {
              channelName: "DOSSIÊ HISTÓRICO",
              badgeText: "ARQUIVO DESCLASSIFICADO // NÍVEL 1",
              subText: "DOCUMENTOS SECRETOS • A HISTÓRIA OCULTA",
              classifiedCode: "REF // TUR-MLT-UKR",
              primaryColor: "#D4AF37",
            },
            backgroundMusicSrc: "dossie/ep01/soundtrack.mp3",
            backgroundMusicVolume: 1.0, // Controlado via dynamic ducking
            voiceovers: [
              {
                id: "vox-00-gancho",
                src: "dossie/ep01/00_gancho.mp3",
                startInSeconds: 0,
                durationInSeconds: 65.78,
                volume: 1.0,
              },
              {
                id: "vox-01-derinkuyu",
                src: "dossie/ep01/01_derinkuyu.mp3",
                startInSeconds: 69.78,
                durationInSeconds: 139.34,
                volume: 1.0,
              },
              {
                id: "vox-02-saflieni",
                src: "dossie/ep01/02_hal_saflieni.mp3",
                startInSeconds: 213.12,
                durationInSeconds: 142.10,
                volume: 1.0,
              },
              {
                id: "vox-03-odessa",
                src: "dossie/ep01/03_odessa.mp3",
                startInSeconds: 359.22,
                durationInSeconds: 92.5,
                volume: 1.0,
              },
              {
                id: "vox-04-conclusao",
                src: "dossie/ep01/04_conclusao.mp3",
                startInSeconds: 457.88,
                durationInSeconds: 46.37,
                volume: 1.0,
              },
            ],
            scenes: [
              // --- GANCHO (65.78s) ---
              {
                id: "hook-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
                durationInSeconds: 32.89,
                headline: "HISTÓRIA OCULTA SOB OS NOSSOS PÉS",
                badge: "DOSSIÊ ARQUEOLÓGICO // ENIGMA",
                notes: "Civilizações que abandonaram a luz do sol para viver centenas de metros abaixo da terra.",
              },
              {
                id: "hook-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide1_capa_1791756613164.jpg",
                durationInSeconds: 32.89,
                headline: "IMPÉRIOS NO SUBMUNDO",
                badge: "DOCUMENTOS DESCLASSIFICADOS",
                notes: "Construções monumentais que a ciência convencional ainda não consegue decifrar.",
              },

              // --- TRANSIÇÃO CASO 1 (4.0s) ---
              {
                id: "trans-derinkuyu",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 4.0,
                headline: "ARQUIVO 01 // DERINKUYU",
                badge: "TURQUIA, 1963",
                subheadline: "A metrópole de 18 andares escondida atrás da parede do porão.",
              },

              // --- CASO 1: DERINKUYU (139.34s) ---
              {
                id: "derinkuyu-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide1_capa_1791756613164.jpg",
                durationInSeconds: 23.22,
                headline: "A PROVÍNCIA DE NEVŞEHIR",
                badge: "CAPADÓCIA, 1963",
                notes: "O mistério das galinhas que desapareciam por uma fresta na pedra do porão.",
              },
              {
                id: "derinkuyu-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide2_descoberta_1791756631797.jpg",
                durationInSeconds: 23.22,
                headline: "O MURO DERRUBADO",
                badge: "A DESCOBERTA ACIDENTAL",
                notes: "Uma escadaria esculpida na rocha sólida descendo para a escuridão absoluta.",
              },
              {
                id: "derinkuyu-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
                durationInSeconds: 23.22,
                headline: "18 ANDARES NO SUBSOLO",
                badge: "85 METROS DE PROFUNDIDADE",
                notes: "Abrigo completo para mais de 20.000 pessoas em isolamento absoluto.",
              },
              {
                id: "derinkuyu-slide-4",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide4_ventilacao_1791756690129.jpg",
                durationInSeconds: 23.22,
                headline: "ENGENHARIA IMPOSSÍVEL",
                badge: "15.000 DUTOS DE VENTILAÇÃO",
                notes: "Ar fresco até os níveis mais profundos, poços artesianos e capelas subterrâneas.",
              },
              {
                id: "derinkuyu-slide-5",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide5_porta_pedra_1791756724664.jpg",
                durationInSeconds: 23.23,
                headline: "PORTAS DE MEIA TONELADA",
                badge: "SISTEMA DE DEFESA BLINDADO",
                notes: "Enormes pedras circulares de 500kg que só podiam ser travadas por dentro.",
              },
              {
                id: "derinkuyu-slide-6",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide6_construtores_1791756762060.jpg",
                durationInSeconds: 23.23,
                headline: "HITITAS OU FRÍGIOS?",
                badge: "O ENIGMA DOS CONSTRUTORES",
                notes: "De que ameaça devastadora uma civilização inteira precisou se esconder?",
              },

              // --- TRANSIÇÃO CASO 2 (4.0s) ---
              {
                id: "trans-saflieni",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 4.0,
                headline: "ARQUIVO 02 // ĦAL SAFLIENI",
                badge: "ILHA DE MALTA, 3.000 A.C.",
                subheadline: "O santuário subterrâneo neolítico afinado na frequência de 110 Hertz.",
              },

              // --- CASO 2: ĦAL SAFLIENI (142.10s) ---
              {
                id: "saflieni-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide1_temple.jpg",
                durationInSeconds: 47.36,
                headline: "O HIPOGEU PRÉ-HISTÓRICO",
                badge: "CIDADE DE PAOLA, 1902",
                notes: "Três níveis esculpidos em calcário duro cinco mil anos atrás, sem ferramentas de metal.",
              },
              {
                id: "saflieni-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide2_oracle.jpg",
                durationInSeconds: 47.37,
                headline: "A CÂMARA DO ORÁCULO",
                badge: "RESSONÂNCIA EM 110 HERTZ",
                notes: "Acústica que estimula o córtex pré-frontal e induz transe emocional hipnótico.",
              },
              {
                id: "saflieni-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide3_skulls.jpg",
                durationInSeconds: 47.37,
                headline: "7.000 ESQUELETOS E CRÂNIOS ALONGADOS",
                badge: "MUSEU ARQUEOLÓGICO DE VALETA",
                notes: "Restos mortais retirados misteriosamente de exibição pública décadas depois.",
              },

              // --- TRANSIÇÃO CASO 3 (4.0s) ---
              {
                id: "trans-odessa",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 4.0,
                headline: "ARQUIVO 03 // CATACUMBAS DE ODESSA",
                badge: "UCRÂNIA, SÉCULO XIX",
                subheadline: "O labirinto infinito de 2.500 km escavado na costa do Mar Negro.",
              },

              // --- CASO 3: ODESSA (94.66s) ---
              {
                id: "odessa-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide1_map.jpg",
                durationInSeconds: 31.55,
                headline: "2.500 KM DE GALERIAS",
                badge: "O LABIRINTO INFINITO",
                notes: "Distância equivalente a São Paulo até Salvador em linha reta sob a terra.",
              },
              {
                id: "odessa-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide2_tunnels.jpg",
                durationInSeconds: 31.55,
                headline: "TRILHOS NA ESCURIDÃO",
                badge: "FORTALEZA DE GUERRILHA",
                notes: "Resistência na Segunda Guerra Mundial; mais de 60% do labirinto nunca foi mapeado.",
              },
              {
                id: "odessa-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide3_danger.jpg",
                durationInSeconds: 31.56,
                headline: "DESAPARECIMENTOS CONSTANTES",
                badge: "ÁREA DE RISCO CRÍTICO",
                notes: "Silêncio absoluto e escuridão total onde exploradores desaparecem para sempre.",
              },

              // --- TRANSIÇÃO CONCLUSÃO (4.0s) ---
              {
                id: "trans-conclusao",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 4.0,
                headline: "CONCLUSÃO // O MISTÉRIO DA TERRA",
                badge: "DOSSIÊ HISTÓRICO",
                subheadline: "Qual dessas três construções subterrâneas você achou mais impressionante?",
              },

              // --- CONCLUSÃO & CTA (46.37s) ---
              {
                id: "cta-slide-final",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/cta_final.jpg",
                durationInSeconds: 46.37,
                headline: "INSCREVA-SE NO CANAL",
                badge: "DEIXE SUA OPINIÃO NOS COMENTÁRIOS",
                notes: "Novos arquivos e investigações desclassificadas todas as semanas.",
              },

              // --- OUTRO FINAL (4.0s) ---
              {
                id: "outro-final",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 4.0,
                headline: "DOSSIÊ CONCLUÍDO",
                badge: "ARQUIVO REGISTRADO",
                subheadline: "Até o próximo dossiê.",
              },
            ],
            captions: sampleEpisodeCaptions as any,
            actTimelines: [
              {
                id: "act_00",
                globalStart: 0,
                globalEnd: 65.78,
              },
              {
                id: "act_01",
                globalStart: 69.78,
                globalEnd: 209.12,
              },
              {
                id: "act_02",
                globalStart: 213.12,
                globalEnd: 355.22,
              },
              {
                id: "act_03",
                globalStart: 359.22,
                globalEnd: 453.88,
              },
              {
                id: "act_04",
                globalStart: 457.88,
                globalEnd: 504.25,
              },
            ],
          },
        }}
      />

      {/* 6. Short Vertical 9:16 (Short 01 - Derinkuyu Pilot) — Padrão Cross-Platform 65s (TikTok Monetization > 60s) */}
      <Composition
        id="Short-Derinkuyu-9x16"
        component={DocumentaryShort as any}
        durationInFrames={1952} // 65.07s @ 30fps (Métrica exata da locução real do usuário)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "A Cidade Proibida de 18 Andares no Subsolo",
          badge: "DOSSIÊ // DERINKUYU 1963",
          musicSrc: "dossie/ep01/short_01_derinkuyu_track.mp3",
          musicVolume: 0.46,
          voiceoverSrc: "dossie/ep01/short_01_derinkuyu.mp3",
          captionsData: sampleShortCaptions,
          actTimelines: [
            {
              id: "short_01",
              globalStart: 0,
              globalEnd: 65.07,
            },
          ],
          scenes: [
            {
              id: "short-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide1_capa_1791756613164.jpg",
              durationInSeconds: 12,
              headline: "A DESCOBERTA NO PORÃO",
              badge: "TURQUIA, 1963",
              notes: "Galinhas desaparecendo por uma fresta escura na parede.",
            },
            {
              id: "short-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide2_descoberta_1791756631797.jpg",
              durationInSeconds: 13,
              headline: "ESCADARIA NA ESCURIDÃO",
              badge: "PAREDE DEMOLIDA",
              notes: "Um túnel vertical que descia para as profundezas da terra.",
            },
            {
              id: "short-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
              durationInSeconds: 15,
              headline: "METRÓPOLE DE 18 ANDARES",
              badge: "ENGENHARIA IMPOSSÍVEL",
              notes: "85 metros de profundidade abrigando 20 mil pessoas.",
            },
            {
              id: "short-slide-4",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide5_porta_pedra_1791756724664.jpg",
              durationInSeconds: 14,
              headline: "PORTAS DE MEIA TONELADA",
              badge: "LACRADAS POR DENTRO",
              notes: "De quem ou de que eles estavam se escondendo?",
            },
            {
              id: "short-slide-5",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide4_ventilacao_1791756690129.jpg",
              durationInSeconds: 11.07,
              headline: "O ENIGMA CONTINUA",
              badge: "DOSSIÊ HISTÓRICO",
              notes: "Deixe sua teoria nos comentários e siga para mais arquivos.",
            },
          ],
        }}
      />

      {/* 7. Short Vertical 9:16 (Short 02 - O Exército de Borracha) — Locução Real do Usuário (78.26s / 2348 frames @ 30fps) */}
      <Composition
        id="Short-Exercito-Borracha-9x16"
        component={DocumentaryShort as any}
        durationInFrames={2348} // 78.26s @ 30fps (Métrica exata da locução real gravada)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "O Exército de Borracha: A Maior Farsa da 2ª Guerra",
          badge: "DOSSIÊ // EXÉRCITO FANTASMA 1944",
          musicSrc: "dossie/ep02/short_02_soundtrack.mp3",
          musicVolume: 0.15, // Volume seguro: 0.12-0.18 para garantir inteligibilidade absoluta da voz em mobile
          voiceoverSrc: "dossie/ep02/short_02_exercito_borracha.mp3",
          captionsData: short02Captions,
          actTimelines: [
            {
              id: "short_02",
              globalStart: 0,
              globalEnd: 78.26,
            },
          ],
          scenes: [
            {
              id: "short2-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/ghost_army_scene.jpg",
              durationInSeconds: 9.0,
              headline: "O TANQUE DE 30 TONELADAS",
              badge: "FRANÇA, 1944",
              notes: "Quatro soldados erguendo um blindado com as próprias mãos.",
            },
            {
              id: "short2-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/scene_artistas.jpg",
              durationInSeconds: 12.0,
              headline: "ARTISTAS CONVOCADOS",
              badge: "HOLLYWOOD & NOVA YORK",
              notes: "Designers e ilustradores convocados para enganar Hitler.",
            },
            {
              id: "short2-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/scene_som.jpg",
              durationInSeconds: 15.0,
              headline: "O EXÉRCITO FANTASMA",
              badge: "ARMA SECRETA",
              notes: "Vencer divisões inteiras sem disparar uma única bala real.",
            },
            {
              id: "short2-slide-4",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/scene_tanque_floresta.jpg",
              durationInSeconds: 17.5,
              headline: "TANQUES DE 42 QUILOS",
              badge: "ALTO-FALANTES A 25 KM",
              notes: "Tanques infláveis de borracha e rugidos de 500W.",
            },
            {
              id: "short2-slide-5",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/scene_rio_reno.jpg",
              durationInSeconds: 11.0,
              headline: "A FARSA DO RIO RENO",
              badge: "30.000 VIDAS SALVAS",
              notes: "Simularam 40 mil homens e desviaram as defesas alemãs.",
            },
            {
              id: "short2-slide-6",
              type: "ken-burns",
              mediaSrc: "dossie/ep02/scene_dossie_final.jpg",
              durationInSeconds: 13.76,
              headline: "SIGILO ATÉ 1996",
              badge: "DOSSIÊ HISTÓRICO",
              notes: "Deixe seu comentário e siga o canal para mais arquivos.",
            },
          ],
        }}
      />

      {/* 8. Short Vertical 9:16 (Short 03 - A Praga da Dança de 1518) — Locução Real do Usuário (100.13s / 3004 frames @ 30fps) */}
      <Composition
        id="Short-Praga-Danca-1518-9x16"
        component={DocumentaryShort as any}
        durationInFrames={3004} // 100.13s @ 30fps (Métrica exata da locução real gravada pelo usuário)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "A Epidemia da Dança de 1518: O Surto Bizarro de Estrasburgo",
          badge: "DOSSIÊ // ESTRASBURGO 1518",
          musicSrc: "dossie/ep03/short_03_signal_to_noise_track.mp3",
          musicVolume: 0.14, // Volume seguro: 0.12-0.18 sob voz humana para garantir inteligibilidade absoluta da voz
          voiceoverSrc: "dossie/ep03/short_03_praga_danca_voiceover.mp3",
          captionsData: short03Captions,
          actTimelines: [
            {
              id: "short_03",
              globalStart: 0,
              globalEnd: 100.13,
            },
          ],
          scenes: [
            {
              id: "short3-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_01_frau_troffea.jpg",
              durationInSeconds: 16.50,
              headline: "A MULHER QUE COMEÇOU A DANÇAR",
              badge: "ESTRASBURGO, JULHO DE 1518",
              notes: "Sem música e sem motivo. Um transe físico incontrolável e assustador.",
            },
            {
              id: "short3-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_02_contagio_400.jpg",
              durationInSeconds: 15.00,
              headline: "400 PESSOAS EM TRANSE MORTAL",
              badge: "SURTO COLETIVO HISTÓRICO",
              notes: "Pés ensanguentados; dançando dia e noite até o colapso físico absoluto.",
            },
            {
              id: "short3-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_03_medicos_colapso.jpg",
              durationInSeconds: 13.00,
              headline: "ATAQUES CARDÍACOS DIÁRIOS",
              badge: "COLAPSO BIOLÓGICO",
              notes: "Autoridades desesperadas consultam médicos que dão o diagnóstico mais bizarro.",
            },
            {
              id: "short3-slide-4",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_04_orquestra_palco.jpg",
              durationInSeconds: 14.00,
              headline: "A PIOR PRESCRIÇÃO DA HISTÓRIA",
              badge: "ERRO MÉDICO CATASTRÓFICO",
              notes: "Sangue superaquecido: contrataram músicos e palcos 24 horas na praça!",
            },
            {
              id: "short3-slide-5",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_05_danca_morte.jpg",
              durationInSeconds: 15.00,
              headline: "MATADOUROS A CÉU ABERTO",
              badge: "A DANÇA DA MORTE REAL",
              notes: "Pessoas implorando por socorro enquanto os músculos pulavam contra a vontade.",
            },
            {
              id: "short3-slide-6",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_06_sapatos_vermelhos.jpg",
              durationInSeconds: 9.00,
              headline: "O RITUAL DE SÃO VITO",
              badge: "SAVERNE, MONTANHAS",
              notes: "Levados amarrados para o santuário onde calçaram sapatos vermelhos santificados.",
            },
            {
              id: "short3-slide-7",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_07_histeria_coletiva.jpg",
              durationInSeconds: 9.00,
              headline: "A EXPLICAÇÃO CIENTÍFICA",
              badge: "DOENÇA PSICOGÊNICA COLETIVA",
              notes: "Não foi veneno de centeio: histeria coletiva gerada por fome e terror místico.",
            },
            {
              id: "short3-slide-8",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_08_dossie_final.jpg",
              durationInSeconds: 8.63,
              headline: "VOCÊ TERIA RESISTIDO?",
              badge: "DOSSIÊ HISTÓRICO",
              notes: "Deixe sua opinião nos comentários e siga o canal para mais arquivos.",
            },
          ],
        }}
      />

      {/* 8B. Short Vertical 9:16 (Short 03 - A Praga da Dança de 1518 — CORTE REELS 88s / <90s) */}
      <Composition
        id="Short-Praga-Danca-1518-Reels-9x16"
        component={DocumentaryShort as any}
        durationInFrames={2640} // 88.00s @ 30fps (Adequação estrita para Instagram Reels / Meta Business Suite <90s)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "A Epidemia da Dança de 1518: O Surto Bizarro de Estrasburgo",
          badge: "DOSSIÊ // ESTRASBURGO 1518",
          musicSrc: "dossie/ep03/short_03_signal_to_noise_track.mp3",
          musicVolume: 0.14, // Volume seguro: 0.12-0.18 sob voz humana para garantir inteligibilidade absoluta da voz
          voiceoverSrc: "dossie/ep03/short_03_praga_danca_reels_88s_voiceover.mp3",
          captionsData: short03ReelsCaptions,
          actTimelines: [
            {
              id: "short_03",
              globalStart: 0,
              globalEnd: 88.00,
            },
          ],
          scenes: [
            {
              id: "short3-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_01_frau_troffea.jpg",
              durationInSeconds: 19.69,
              headline: "A MULHER QUE COMEÇOU A DANÇAR",
              badge: "ESTRASBURGO, JULHO DE 1518",
              notes: "Sem música e sem motivo. Um transe físico incontrolável e assustador.",
            },
            {
              id: "short3-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_02_contagio_400.jpg",
              durationInSeconds: 11.06,
              headline: "400 PESSOAS EM TRANSE MORTAL",
              badge: "SURTO COLETIVO HISTÓRICO",
              notes: "Pés ensanguentados; dançando dia e noite até o colapso físico absoluto.",
            },
            {
              id: "short3-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_03_medicos_colapso.jpg",
              durationInSeconds: 11.70,
              headline: "ATAQUES CARDÍACOS DIÁRIOS",
              badge: "COLAPSO BIOLÓGICO",
              notes: "Autoridades desesperadas consultam médicos que dão o diagnóstico mais bizarro.",
            },
            {
              id: "short3-slide-4",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_04_orquestra_palco.jpg",
              durationInSeconds: 12.76,
              headline: "A PIOR PRESCRIÇÃO DA HISTÓRIA",
              badge: "ERRO MÉDICO CATASTRÓFICO",
              notes: "Sangue superaquecido: contrataram músicos e palcos 24 horas na praça!",
            },
            {
              id: "short3-slide-5",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_05_danca_morte.jpg",
              durationInSeconds: 9.15,
              headline: "MATADOUROS A CÉU ABERTO",
              badge: "A DANÇA DA MORTE REAL",
              notes: "Pessoas implorando por socorro enquanto os músculos pulavam contra a vontade.",
            },
            {
              id: "short3-slide-6",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_06_sapatos_vermelhos.jpg",
              durationInSeconds: 7.90,
              headline: "O RITUAL DE SÃO VITO",
              badge: "SAVERNE, MONTANHAS",
              notes: "Levados amarrados para o santuário onde calçaram sapatos vermelhos santificados.",
            },
            {
              id: "short3-slide-7",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_07_histeria_coletiva.jpg",
              durationInSeconds: 8.05,
              headline: "A EXPLICAÇÃO CIENTÍFICA",
              badge: "DOENÇA PSICOGÊNICA COLETIVA",
              notes: "Não foi veneno de centeio: histeria coletiva gerada por fome e terror místico.",
            },
            {
              id: "short3-slide-8",
              type: "ken-burns",
              mediaSrc: "dossie/ep03/scene_08_dossie_final.jpg",
              durationInSeconds: 7.69,
              headline: "VOCÊ TERIA RESISTIDO?",
              badge: "DOSSIÊ HISTÓRICO",
              notes: "Deixe sua opinião nos comentários e siga o canal para mais arquivos.",
            },
          ],
        }}
      />

      {/* 8C. Short Vertical 9:16 (Short 04 - O Real Motivo das Cores da Bandeira do Brasil — Word-by-Word & Mito x Realidade) */}
      <Composition
        id="Short-Cores-Bandeira-9x16"
        component={DocumentaryShort as any}
        durationInFrames={2580} // 86.0s @ 30fps — Formato exato para Instagram Reels (<90s) e TikTok (>60s)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "O Real Motivo das Cores da Bandeira do Brasil (O Decreto de 1822)",
          badge: "DOSSIÊ // DECRETO DE 1822",
          voiceoverSrc: "dossie/ep04/short_04_voiceover_mastered.mp3",
          voiceoverVolume: 1.0,
          musicSrc: "dossie/ep04/short_04_hino_nacional_instrumental.mp3",
          musicVolume: 0.15, // Teto rigoroso de 0.15 sob a fala (Rule 10)
          captionStyle: "word-by-word",
          captionsBottomPosition: 420,
          showSceneMetadata: false, // Mantém o topo desobstruído evitando colisão com o HUD
          captionsData: short04Captions,
          actTimelines: [
            {
              id: "short_04",
              globalStart: 0,
              globalEnd: 86.0,
            },
          ],
          impactOverlays: [
            {
              startSec: 0.5,
              durationSec: 6.5,
              type: "question-card",
              top: 150,
              text: "O VERDE E O AMARELO SÃO MESMO PELAS FLORESTAS E PELO OURO?",
            },
            {
              startSec: 8.5,
              durationSec: 4.2,
              type: "stamp-mito",
              top: 240,
              text: "MITO CÍVICO!",
              subtext: "A VERSÃO ESCOLAR É UMA CRIAÇÃO POSTERIOR",
            },
            {
              startSec: 12.8,
              durationSec: 0.15,
              type: "flash-cut",
            },
            {
              startSec: 13.2,
              durationSec: 5.5,
              type: "question-card",
              top: 150,
              text: "QUAL É, AFINAL, A VERDADEIRA ORIGEM DESSAS CORES?",
            },
            {
              startSec: 22.8,
              durationSec: 4.5,
              type: "stamp-realidade",
              top: 990, // Posicionado com folga no peito de Dom Pedro I, sem encobrir o colarinho/rosto!
              text: "CASA DE BRAGANÇA",
              subtext: "A DINASTIA PORTUGUESA DE DOM PEDRO I",
            },
            {
              startSec: 30.5,
              durationSec: 3.5,
              type: "question-card",
              top: 150,
              text: "E O QUE REPRESENTA O LOSANGO AMARELO NO CENTRO?",
            },
            {
              startSec: 41.5,
              durationSec: 5.5,
              type: "stamp-realidade",
              top: 1040, // Posicionado no decote/vestido imperial de Leopoldina, liberando 100% do rosto e pescoço!
              text: "CASA DE HABSBURGO",
              subtext: "A DINASTIA AUSTRÍACA DA IMPERATRIZ LEOPOLDINA",
            },
            {
              startSec: 53.0,
              durationSec: 4.5,
              type: "question-card",
              top: 150,
              text: "POR QUE ESSA HISTÓRIA FOI APAGADA EM 1889?",
            },
            {
              startSec: 58.5,
              durationSec: 6.0,
              type: "stamp-mito",
              top: 980, // Posicionado na metade inferior, sem colidir com as listras centrais
              text: "BANDEIRA PROVISÓRIA VETADA",
              subtext: "REJEITADA EM 4 DIAS POR DEODORO DA FONSECA",
            },
            {
              startSec: 79.5,
              durationSec: 5.8,
              type: "question-card",
              top: 150,
              text: "VOCÊ JÁ CONHECIA O DECRETO DE 1822?",
            },
          ],
          scenes: [
            {
              id: "short4-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_01_bandeira_escola_mito.jpg",
              durationInSeconds: 7.5,
              headline: "O MITO DO VERDE E AMARELO",
              badge: "TRADIÇÃO ESCOLAR",
              notes: "Você provavelmente aprendeu que as cores representam as matas e o ouro.",
            },
            {
              id: "short4-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_02_carimbo_mito_quebra.jpg",
              durationInSeconds: 5.5,
              headline: "A VERDADE DOCUMENTADA",
              badge: "ARQUIVO DESCLASSIFICADO",
              notes: "Mas os documentos oficiais revelam que isso é apenas um mito cívico.",
            },
            {
              id: "short4-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_03_arquivo_secreto_1822.jpg",
              durationInSeconds: 9.5,
              headline: "DECRETO DE 18 DE SETEMBRO",
              badge: "LEGISLAÇÃO DE 1822",
              notes: "A resposta está no Decreto Imperial de 18 de setembro de 1822.",
            },
            {
              id: "short4-slide-4",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_04_dom_pedro_braganca.jpg",
              durationInSeconds: 4.0,
              headline: "DOM PEDRO I DE BRAGANÇA",
              badge: "A COROA PORTUGUESA",
              notes: "O verde nunca simbolizou florestas: era a cor heráldica da Casa de Bragança.",
            },
            {
              id: "short4-slide-5",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_05_brasao_verde_portugal.jpg",
              durationInSeconds: 6.0,
              headline: "O VERDE HERÁLDICO REAL",
              badge: "HERÁLDICA MONÁRQUICA",
              notes: "A dinastia real portuguesa de onde nasceu a independência do Brasil.",
            },
            {
              id: "short4-slide-6",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_06_losango_amarelo_macro.jpg",
              durationInSeconds: 4.5,
              headline: "EXPLODED VIEW DA BANDEIRA",
              badge: "ANATOMIA HERÁLDICA",
              notes: "Visão explodida em camadas 3D da bandeira imperial de 1822.",
            },
            {
              id: "short4-slide-7",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_07_debret_napoleao_losango.jpg",
              durationInSeconds: 5.0,
              headline: "INSPIRAÇÃO NAPOLEÔNICA",
              badge: "JEAN-BAPTISTE DEBRET",
              notes: "Debret se inspirou no padrão militar de losango da Itália de Napoleão.",
            },
            {
              id: "short4-slide-8",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_08_leopoldina_habsburgo.jpg",
              durationInSeconds: 5.0,
              headline: "A IMPERATRIZ LEOPOLDINA",
              badge: "CASA DE HABSBURGO",
              notes: "O amarelo-ouro era a cor secular da Casa de Habsburgo da Áustria.",
            },
            {
              id: "short4-slide-9",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_09_aguia_bicefala_austria.jpg",
              durationInSeconds: 6.0,
              headline: "A ÁUSTRIA NO BRASIL",
              badge: "ALIANÇA DINÁSTICA",
              notes: "A bandeira nasceu da aliança matrimonial entre essas duas coroas da Europa.",
            },
            {
              id: "short4-slide-10",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_10_golpe_1889_republica.jpg",
              durationInSeconds: 5.5,
              headline: "O DILEMA DE 1889",
              badge: "GOLPE REPUBLICANO",
              notes: "Com a República em 1889, os militares não podiam manter homenagem a imperadores.",
            },
            {
              id: "short4-slide-11",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_11_bandeira_americana_rejeitada.jpg",
              durationInSeconds: 6.5,
              headline: "BANDEIRA PROVISÓRIA VETADA",
              badge: "4 DIAS DE HISTÓRIA",
              notes: "Tentaram criar uma bandeira provisória estilo americana, vetada por Deodoro.",
            },
            {
              id: "short4-slide-12",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_12_olavo_bilac_propaganda.jpg",
              durationInSeconds: 7.0,
              headline: "A INVENÇÃO DAS MATAS",
              badge: "PROPAGANDA CÍVICA",
              notes: "Criaram a versão poética das matas e minerais para reescrever o símbolo cívico.",
            },
            {
              id: "short4-slide-13",
              type: "ken-burns",
              mediaSrc: "dossie/ep04/scene_13_dossie_final_debate.jpg",
              durationInSeconds: 14.0,
              headline: "O DECRETO DE 1822",
              badge: "DOSSIÊ HISTÓRICO",
              notes: "Conhecer a origem resgata a história documental de como o Brasil foi fundado.",
            },
          ],
        }}
      />

      {/* 9. Documentário Longo 16:9 — Episódio 02: O Exército de Borracha */}
      <Composition
        id="DocumentaryEpisode-02-ExercitoBorracha-16x9"
        component={DocumentaryEpisode}
        durationInFrames={15210}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          config: ep02DocumentaryConfig,
          enableIntro: true,
          introDurationFrames: 120,
        }}
      />

      {/* 9. Universal Agnostic Documentary Episode 16:9 (Render Any Channel via props) */}
      <Composition
        id="DocumentaryEpisode-16x9"
        component={DocumentaryEpisode}
        durationInFrames={15368}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120,
        }}
      />

      {/* 8. Universal Agnostic Documentary Episode 9:16 (Vertical Full Episode) */}
      <Composition
        id="DocumentaryEpisode-9x16"
        component={DocumentaryEpisode}
        durationInFrames={15368}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120,
        }}
      />

      {/* 9. Universal Agnostic Documentary Short 9:16 (Shorts / Reels / TikTok) */}
      <Composition
        id="DocumentaryShort-9x16"
        component={DocumentaryShort as any}
        durationInFrames={1500}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Título do Short",
          badge: "CONTEÚDO OFICIAL // SHORTS",
          scenes: [],
        }}
      />

      {/* 10. Thumbnail Oficial YouTube 16:9 — Alto Impacto & Altas Letras */}
      <Composition
        id="Thumbnail-Dossie-16x9"
        component={ThumbnailEpisode as any}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          titleLine1: "18 ANDARES",
          titleLine2: "NO SUBSOLO",
          tagText: "ARQUIVO SECRETO // CASO REAL",
          calloutText: "ACHOU ATRÁS DA PAREDE!",
          depthTag: "85 METROS DE PROFUNDIDADE",
          peopleTag: "ABRIGAVA 20.000 PESSOAS",
          doorTag: "PORTAS DE MEIA TONELADA",
          imageSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
          cellarSrc: "dossie/ep01/derinkuyu_slide2_descoberta_1791756631797.jpg",
          showClassifiedStamp: true,
        }}
      />
    </>
  );
};
