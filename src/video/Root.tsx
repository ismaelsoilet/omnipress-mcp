import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import { DocumentaryEpisode, DocumentaryEpisodeProps } from "./compositions/DocumentaryEpisode";
import { DocumentaryShort, DocumentaryShortProps } from "./compositions/DocumentaryShort";
import { ChannelIntroProps } from "./types";

export const Root: React.FC = () => {
  return (
    <>
      {/* 1. Vinheta 16:9 — Português (YouTube Principal) */}
      <Composition<ChannelIntroProps>
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
      <Composition<ChannelIntroProps>
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
      <Composition<ChannelIntroProps>
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
      <Composition<ChannelIntroProps>
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
      <Composition<DocumentaryEpisodeProps>
        id="Episode-Dossie-16x9"
        component={DocumentaryEpisode}
        durationInFrames={15339} // 511.3s (~8m31s @ 30fps)
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
            backgroundMusicSrc: "dossie/ep01/soundtrack.mp3",
            backgroundMusicVolume: 0.85,
            voiceovers: [
              {
                id: "vox-00-gancho",
                src: "dossie/ep01/00_gancho.mp3",
                startInSeconds: 0,
                durationInSeconds: 65.8,
                volume: 1.0,
              },
              {
                id: "vox-01-derinkuyu",
                src: "dossie/ep01/01_derinkuyu.mp3",
                startInSeconds: 69.8,
                durationInSeconds: 139.3,
                volume: 1.0,
              },
              {
                id: "vox-02-saflieni",
                src: "dossie/ep01/02_hal_saflieni.mp3",
                startInSeconds: 213.1,
                durationInSeconds: 142.1,
                volume: 1.0,
              },
              {
                id: "vox-03-odessa",
                src: "dossie/ep01/03_odessa.mp3",
                startInSeconds: 359.2,
                durationInSeconds: 94.7,
                volume: 1.0,
              },
              {
                id: "vox-04-conclusao",
                src: "dossie/ep01/04_conclusao.mp3",
                startInSeconds: 456.9,
                durationInSeconds: 46.4,
                volume: 1.0,
              },
            ],
            scenes: [
              // --- GANCHO (65.8s) ---
              {
                id: "hook-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/hook_capa.jpg",
                durationInSeconds: 33.0,
                headline: "HISTÓRIA OCULTA SOB OS NOSSOS PÉS",
                badge: "DOSSIÊ ARQUEOLÓGICO // ENIGMA",
                notes: "Civilizações que abandonaram a luz do sol para viver centenas de metros abaixo da terra.",
              },
              {
                id: "hook-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/hook_dossie.jpg",
                durationInSeconds: 32.8,
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

              // --- CASO 1: DERINKUYU (139.3s) ---
              {
                id: "derinkuyu-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide1_capa_1791756613164.jpg",
                durationInSeconds: 23.0,
                headline: "A PROVÍNCIA DE NEVŞEHIR",
                badge: "CAPADÓCIA, 1963",
                notes: "O mistério das galinhas que desapareciam por uma fresta na pedra do porão.",
              },
              {
                id: "derinkuyu-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide2_descoberta_1791756631797.jpg",
                durationInSeconds: 23.0,
                headline: "O MURO DERRUBADO",
                badge: "A DESCOBERTA ACIDENTAL",
                notes: "Uma escadaria esculpida na rocha sólida descendo para a escuridão absoluta.",
              },
              {
                id: "derinkuyu-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
                durationInSeconds: 23.0,
                headline: "18 ANDARES NO SUBSOLO",
                badge: "85 METROS DE PROFUNDIDADE",
                notes: "Abrigo completo para mais de 20.000 pessoas em isolamento absoluto.",
              },
              {
                id: "derinkuyu-slide-4",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide4_ventilacao_1791756690129.jpg",
                durationInSeconds: 23.0,
                headline: "ENGENHARIA IMPOSSÍVEL",
                badge: "15.000 DUTOS DE VENTILAÇÃO",
                notes: "Ar fresco até os níveis mais profundos, poços artesianos e capelas subterrâneas.",
              },
              {
                id: "derinkuyu-slide-5",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide5_porta_pedra_1791756724664.jpg",
                durationInSeconds: 23.3,
                headline: "PORTAS DE MEIA TONELADA",
                badge: "SISTEMA DE DEFESA BLINDADO",
                notes: "Enormes pedras circulares de 500kg que só podiam ser travadas por dentro.",
              },
              {
                id: "derinkuyu-slide-6",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/derinkuyu_slide6_construtores_1791756762060.jpg",
                durationInSeconds: 24.0,
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

              // --- CASO 2: ĦAL SAFLIENI (142.1s) ---
              {
                id: "saflieni-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide1_temple.jpg",
                durationInSeconds: 47.0,
                headline: "O HIPOGEU PRÉ-HISTÓRICO",
                badge: "CIDADE DE PAOLA, 1902",
                notes: "Três níveis esculpidos em calcário duro cinco mil anos atrás, sem ferramentas de metal.",
              },
              {
                id: "saflieni-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide2_oracle.jpg",
                durationInSeconds: 48.0,
                headline: "A CÂMARA DO ORÁCULO",
                badge: "RESSONÂNCIA EM 110 HERTZ",
                notes: "Acústica que estimula o córtex pré-frontal e induz transe emocional hipnótico.",
              },
              {
                id: "saflieni-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/saflieni_slide3_skulls.jpg",
                durationInSeconds: 47.1,
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

              // --- CASO 3: ODESSA (94.7s) ---
              {
                id: "odessa-slide-1",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide1_map.jpg",
                durationInSeconds: 31.0,
                headline: "2.500 KM DE GALERIAS",
                badge: "O LABIRINTO INFINITO",
                notes: "Distância equivalente a São Paulo até Salvador em linha reta sob a terra.",
              },
              {
                id: "odessa-slide-2",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide2_tunnels.jpg",
                durationInSeconds: 32.0,
                headline: "TRILHOS NA ESCURIDÃO",
                badge: "FORTALEZA DE GUERRILHA",
                notes: "Resistência na Segunda Guerra Mundial; mais de 60% do labirinto nunca foi mapeado.",
              },
              {
                id: "odessa-slide-3",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/odessa_slide3_danger.jpg",
                durationInSeconds: 31.7,
                headline: "DESAPARECIMENTOS CONSTANTES",
                badge: "ÁREA DE RISCO CRÍTICO",
                notes: "Silêncio absoluto e escuridão total onde exploradores desaparecem para sempre.",
              },

              // --- TRANSIÇÃO CONCLUSÃO (3.0s) ---
              {
                id: "trans-conclusao",
                type: "document-reveal",
                mediaSrc: "",
                durationInSeconds: 3.0,
                headline: "CONCLUSÃO // O MISTÉRIO DA TERRA",
                badge: "DOSSIÊ HISTÓRICO",
                subheadline: "Qual dessas três construções subterrâneas você achou mais impressionante?",
              },

              // --- CONCLUSÃO & CTA (46.4s) ---
              {
                id: "cta-slide-final",
                type: "ken-burns",
                mediaSrc: "dossie/ep01/cta_final.jpg",
                durationInSeconds: 46.4,
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
          },
        }}
      />

      {/* 6. Short Vertical 9:16 (Short 01 - Derinkuyu) */}
      <Composition<DocumentaryShortProps>
        id="Short-Derinkuyu-9x16"
        component={DocumentaryShort}
        durationInFrames={1500} // 50 segundos (1500 frames @ 30fps)
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "A Cidade Proibida de 18 Andares no Subsolo",
          badge: "DOSSIÊ // DERINKUYU 1963",
          musicSrc: "channels/dossie-historico/media/soundtrack/cuts/short_01_derinkuyu_track.mp3",
          scenes: [
            {
              id: "short-slide-1",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide1_capa_1791756613164.jpg",
              durationInSeconds: 15,
              headline: "A CIDADE NO SUBSOLO",
              badge: "TURQUIA, 1963",
              notes: "Um morador quebrou a parede e achou 18 andares escavados.",
            },
            {
              id: "short-slide-2",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide5_porta_pedra_1791756724664.jpg",
              durationInSeconds: 15,
              headline: "PORTAS DE 500 KG",
              badge: "LACRADAS POR DENTRO",
              notes: "De que ameaça 20 mil pessoas estavam se protegendo?",
            },
            {
              id: "short-slide-3",
              type: "ken-burns",
              mediaSrc: "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
              durationInSeconds: 20,
              headline: "DOSSIÊ COMPLETO NO CANAL",
              badge: "ASSISTA AGORA",
              notes: "Link fixado para o episódio completo de 8 minutos.",
            },
          ],
        }}
      />
    </>
  );
};
