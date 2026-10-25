import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FilmGrain } from "./FilmGrain";
import { DustParticles } from "./DustParticles";

export interface ChannelOutroProps {
  durationInFrames: number;
  channelName?: string;
  avatarSrc?: string;
  bannerSrc?: string;
  primaryColor?: string;
}

/**
 * ChannelOutro — Vinheta Oficial de Encerramento e Compartilhamento.
 * 100% agnóstica e reutilizável em todos os projetos do canal Dossiê Histórico.
 *
 * Estrutura Dinâmica em 2 Fases:
 * - Fase 1 (0 a 12s / frames 0 a 360): Chamada nobre de COMPARTILHAMENTO com fontes grandes.
 * - Fase 2 (12s a 25.3s / frames 360 a 759): INSCRIÇÃO NO CANAL, branding e zonas de End Screen do YouTube.
 */
export const ChannelOutro: React.FC<ChannelOutroProps> = ({
  durationInFrames,
  channelName = "DOSSIÊ HISTÓRICO",
  avatarSrc = "dossie/ep03b/midias/cena_69_mosaico_quatro_arquitetos.jpg", // fallback seguro
  bannerSrc,
  primaryColor = "#D4AF37",
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  // Divisão das duas fases da vinheta (~12s para partilha, ~13.3s para inscrição)
  const phaseSplitFrame = Math.round(durationInFrames * 0.47); // ~frame 360

  // Animação de entrada e transição entre fases
  const phase1Opacity = interpolate(
    frame,
    [0, 15, phaseSplitFrame - 15, phaseSplitFrame],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const phase2Opacity = interpolate(
    frame,
    [phaseSplitFrame, phaseSplitFrame + 15, durationInFrames - 15, durationInFrames],
    [0.0, 1.0, 1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Escala contínua suave de câmera lenta
  const bgScale = interpolate(frame, [0, durationInFrames], [1.02, 1.10], {
    extrapolateRight: "clamp",
  });

  // Pulso do botão de inscrição na Fase 2
  const pulse = Math.sin((frame - phaseSplitFrame) * 0.12) * 0.03 + 1.0;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#070A0F",
        overflow: "hidden",
      }}
    >
      {/* 1. Fundo Cinemático com Gradiente Radial Profundo e Partículas */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at center, #101826 0%, #080C14 65%, #04060A 100%)",
          transform: `scale(${bgScale})`,
          transformOrigin: "center center",
        }}
      />

      {/* 2. Malha Tática Sutil de Fundo */}
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(212, 175, 55, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(212, 175, 55, 0.04) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          opacity: 0.7,
        }}
      />

      <DustParticles count={isVertical ? 10 : 16} />
      <FilmGrain opacity={0.035} />

      {/* ==================================================================== */}
      {/* FASE 1: O COMPARTILHAMENTO DA VERDADE HISTÓRICA (Frames 0 a 360)      */}
      {/* ==================================================================== */}
      {frame < phaseSplitFrame + 5 && (
        <AbsoluteFill
          style={{
            opacity: phase1Opacity,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "0 100px",
            textAlign: "center",
          }}
        >
          {/* Badge Superior */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 12,
              backgroundColor: "rgba(12, 18, 28, 0.85)",
              border: `1.5px solid ${primaryColor}`,
              borderLeft: `5px solid ${primaryColor}`,
              borderRadius: 6,
              padding: "10px 24px",
              marginBottom: 28,
            }}
          >
            <span
              style={{
                color: primaryColor,
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 22,
                fontWeight: 900,
                letterSpacing: 3,
                textTransform: "uppercase",
              }}
            >
              INSTRUÇÃO CONCLUÍDA // DIFUSÃO PÚBLICA
            </span>
          </div>

          {/* Título Principal de Impacto */}
          <h1
            style={{
              color: "#FFFFFF",
              fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
              fontSize: 54,
              fontWeight: 900,
              letterSpacing: 2,
              lineHeight: 1.2,
              margin: "0 0 24px 0",
              maxWidth: 1500,
              textShadow: "0 4px 20px rgba(0, 0, 0, 0.9)",
              textTransform: "uppercase",
            }}
          >
            A VERDADEIRA HISTÓRIA NÃO PODE FICAR EM SEGREDO
          </h1>

          {/* Subtítulo Dinâmico */}
          <p
            style={{
              color: "#E2E8F0",
              fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
              fontSize: 32,
              fontWeight: 500,
              lineHeight: 1.4,
              margin: "0 0 38px 0",
              maxWidth: 1300,
              textShadow: "0 2px 10px rgba(0, 0, 0, 0.8)",
            }}
          >
            Compartilhe este dossiê com professores, estudantes, historiadores e amigos que ainda acreditam no mito das matas e do ouro.
          </p>

          {/* Carimbo de Partilha Pericial */}
          <div
            style={{
              display: "inline-block",
              border: "3px solid #00B45F",
              borderRadius: 10,
              backgroundColor: "rgba(10, 32, 20, 0.88)",
              padding: "14px 40px",
              boxShadow: "0 0 30px rgba(0, 180, 95, 0.25)",
            }}
          >
            <span
              style={{
                color: "#00E676",
                fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                fontSize: 28,
                fontWeight: 800,
                letterSpacing: 3,
                textTransform: "uppercase",
              }}
            >
              ✔ DOCUMENTO PÚBLICO // COMPARTILHE A HISTÓRIA REAL
            </span>
          </div>
        </AbsoluteFill>
      )}

      {/* ==================================================================== */}
      {/* FASE 2: BRANDING DO CANAL & INSCRIÇÃO (Frames 360 a Fim)              */}
      {/* ==================================================================== */}
      {frame >= phaseSplitFrame - 5 && (
        <AbsoluteFill
          style={{
            opacity: phase2Opacity,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "50px 80px 45px 80px",
          }}
        >
          {/* Topo: Branding Imponente do Canal */}
          <div style={{ textAlign: "center" }}>
            <h1
              style={{
                color: "#FFFFFF",
                fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                fontSize: 58,
                fontWeight: 900,
                letterSpacing: 4,
                margin: "0 0 10px 0",
                textTransform: "uppercase",
                textShadow: "0 4px 24px rgba(0, 0, 0, 0.95)",
              }}
            >
              {channelName}
            </h1>
            <p
              style={{
                color: primaryColor,
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: 22,
                fontWeight: 800,
                letterSpacing: 3,
                margin: 0,
                textTransform: "uppercase",
              }}
            >
              INVESTIGAÇÃO HISTÓRICA, HERÁLDICA & ARQUIVOS SECRETOS
            </p>
          </div>

          {/* Centro: Zonas Elegantes de Vídeos Recomendados (End Screen do YouTube) */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              width: "100%",
              maxWidth: 1600,
              gap: 40,
            }}
          >
            {/* Espaço do Vídeo Recomendado (Esquerda) */}
            <div
              style={{
                flex: 1,
                height: 240,
                backgroundColor: "rgba(14, 20, 30, 0.85)",
                border: "1.5px dashed rgba(212, 175, 55, 0.45)",
                borderRadius: 12,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: 20,
                boxShadow: "0 8px 30px rgba(0, 0, 0, 0.8)",
              }}
            >
              <span
                style={{
                  color: primaryColor,
                  fontFamily: "'Courier New', Courier, monospace",
                  fontSize: 18,
                  fontWeight: 800,
                  letterSpacing: 2,
                  marginBottom: 10,
                }}
              >
                VÍDEO RECOMENDADO
              </span>
              <span
                style={{
                  color: "#FFFFFF",
                  fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                  fontSize: 22,
                  fontWeight: 700,
                  textAlign: "center",
                }}
              >
                Assista ao próximo documentário
              </span>
            </div>

            {/* Centro: Botão de Inscrição em Destaque Absoluto */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: `scale(${pulse})`,
                zIndex: 10,
              }}
            >
              <div
                style={{
                  backgroundColor: "#CC0000",
                  border: "2.5px solid #FFFFFF",
                  borderRadius: 50,
                  padding: "18px 46px",
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  boxShadow: "0 8px 35px rgba(204, 0, 0, 0.6), 0 0 20px rgba(255, 255, 255, 0.3)",
                }}
              >
                <span style={{ fontSize: 28, color: "#FFFFFF" }}>▶</span>
                <span
                  style={{
                    color: "#FFFFFF",
                    fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                    fontSize: 28,
                    fontWeight: 900,
                    letterSpacing: 2,
                    textTransform: "uppercase",
                  }}
                >
                  INSCREVA-SE
                </span>
              </div>
              <span
                style={{
                  color: "#E2E8F0",
                  fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                  fontSize: 18,
                  fontWeight: 700,
                  marginTop: 14,
                  letterSpacing: 1,
                }}
              >
                🔔 Ative o sino de notificações
              </span>
            </div>

            {/* Espaço do Próximo Episódio (Direita) */}
            <div
              style={{
                flex: 1,
                height: 240,
                backgroundColor: "rgba(14, 20, 30, 0.85)",
                border: "1.5px dashed rgba(212, 175, 55, 0.45)",
                borderRadius: 12,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: 20,
                boxShadow: "0 8px 30px rgba(0, 0, 0, 0.8)",
              }}
            >
              <span
                style={{
                  color: primaryColor,
                  fontFamily: "'Courier New', Courier, monospace",
                  fontSize: 18,
                  fontWeight: 800,
                  letterSpacing: 2,
                  marginBottom: 10,
                }}
              >
                PLAYLIST COMPLETA
              </span>
              <span
                style={{
                  color: "#FFFFFF",
                  fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                  fontSize: 22,
                  fontWeight: 700,
                  textAlign: "center",
                }}
              >
                Dossiês e Casos Arquivados
              </span>
            </div>
          </div>

          {/* Rodapé: Chamada para Comentários e Debate */}
          <div
            style={{
              backgroundColor: "rgba(10, 14, 22, 0.90)",
              border: `1.5px solid rgba(212, 175, 55, 0.40)`,
              borderRadius: 8,
              padding: "14px 40px",
              width: "100%",
              maxWidth: 1600,
              textAlign: "center",
            }}
          >
            <p
              style={{
                color: "#F8FAFC",
                fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                fontSize: 24,
                fontWeight: 600,
                margin: 0,
                letterSpacing: 1,
              }}
            >
              <strong style={{ color: primaryColor }}>PARTICIPE DO DEBATE:</strong> Você já conhecia a verdadeira história das cores? Deixe sua opinião nos comentários.
            </p>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
