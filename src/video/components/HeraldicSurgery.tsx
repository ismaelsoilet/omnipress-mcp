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

export interface HeraldicSurgeryProps {
  durationInFrames: number;
  imperialFlagSrc?: string;
  republicFlagSrc?: string;
  badge?: string;
}

/**
 * HeraldicSurgery — Animação Dinâmica da "Cirurgia Heráldica de 1889".
 * Executa a substituição em tempo real do Brasão Imperial pela Esfera Celeste Positivista:
 * 1. Frame 0 a 140 (~4.6s): Exibe a Bandeira Imperial de 1822 com sutil Ken Burns.
 * 2. Frame 140 a 220 (~4.6s a 7.3s): Fade-out cirúrgico do brasão/coroa imperial e fade-in
 *    perfeitamente alinhado da Esfera Azul com 'Ordem e Progresso' e as estrelas de 1889.
 * 3. Frame 220 a fim: A Bandeira Republicana consolidada em movimento cinematográfico.
 */
export const HeraldicSurgery: React.FC<HeraldicSurgeryProps> = ({
  durationInFrames,
  imperialFlagSrc = "dossie/ep03b/midias/bandeira_imperial_1822.png",
  republicFlagSrc = "dossie/ep03b/midias/bandeira_republica_1889.png",
  badge = "ATO 5 // CIRURGIA HERÁLDICA",
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  // Escala contínua e suave para dinamismo cinematográfico
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.10], {
    extrapolateRight: "clamp",
  });

  // Janela de transição cirúrgica: frame 130 a 210
  const transStart = Math.round(durationInFrames * 0.35); // ~frame 135
  const transEnd = Math.round(durationInFrames * 0.58);   // ~frame 225

  // Opacidades
  const imperialOpacity = interpolate(
    frame,
    [transStart, transEnd],
    [1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const republicOpacity = interpolate(
    frame,
    [transStart, transEnd],
    [0.0, 1.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Flash óptico de transição no clímax do corte
  const flashMid = (transStart + transEnd) / 2;
  const flashOpacity = interpolate(
    frame,
    [flashMid - 15, flashMid, flashMid + 20],
    [0.0, 0.40, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Badge dinâmico que evolui durante a transformação
  const isAfterSurgery = frame >= flashMid;
  const activeBadge = isAfterSurgery
    ? "ATO 5 // CIRURGIA HERÁLDICA: A ESFERA REPUBLICANA (1889)"
    : "ATO 5 // CIRURGIA HERÁLDICA: O BRASÃO IMPERIAL (1822)";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06080C",
        overflow: "hidden",
      }}
    >
      {/* 1. Camada de Fundo Ambiente com Desfoque */}
      <AbsoluteFill style={{ overflow: "hidden", contain: "paint" }}>
        <Img
          src={staticFile(isAfterSurgery ? republicFlagSrc : imperialFlagSrc)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "blur(14px) brightness(0.32)",
            transform: "scale(1.15)",
          }}
        />
      </AbsoluteFill>

      {/* 2. Bandeira Imperial com Fade-out */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          transformOrigin: "center center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: imperialOpacity,
        }}
      >
        <Img
          src={staticFile(imperialFlagSrc)}
          style={{
            maxWidth: "92%",
            maxHeight: "92%",
            objectFit: "contain",
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85)",
          }}
        />
      </AbsoluteFill>

      {/* 3. Bandeira Republicana com Fade-in */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          transformOrigin: "center center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: republicOpacity,
        }}
      >
        <Img
          src={staticFile(republicFlagSrc)}
          style={{
            maxWidth: "92%",
            maxHeight: "92%",
            objectFit: "contain",
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85)",
          }}
        />
      </AbsoluteFill>

      {/* 4. Flash Óptico Suave na Substituição do Brasão */}
      {flashOpacity > 0.01 && (
        <AbsoluteFill
          style={{
            backgroundColor: "rgba(255, 235, 170, 0.75)",
            mixBlendMode: "screen",
            opacity: flashOpacity,
            pointerEvents: "none",
          }}
        />
      )}

      {/* 5. Vinheta Protetora Suave nas Bordas */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at center, transparent 75%, rgba(6, 8, 12, 0.35) 92%, rgba(4, 5, 8, 0.65) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* 6. Partículas de Poeira Luminosa Flutuante */}
      <DustParticles count={isVertical ? 8 : 12} />

      {/* 7. Granulação de Película de Época */}
      <FilmGrain opacity={0.032} />

      {/* 8. Badge Superior Dinâmico */}
      <div
        style={{
          position: "absolute",
          top: isVertical ? 38 : 34,
          left: isVertical ? 32 : 40,
          display: "inline-flex",
          alignItems: "center",
          gap: 10,
          backgroundColor: "rgba(8, 10, 14, 0.90)",
          border: `1.2px solid ${isAfterSurgery ? "rgba(0, 180, 95, 0.6)" : "rgba(212, 175, 55, 0.6)"}`,
          borderLeft: `5px solid ${isAfterSurgery ? "#00B45F" : "#D4AF37"}`,
          borderRadius: 8,
          padding: isVertical ? "10px 22px" : "8px 18px",
          boxShadow: "0 6px 20px rgba(0, 0, 0, 0.8)",
          zIndex: 30,
        }}
      >
        <span
          style={{
            color: "#F1F5F9",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 24 : 20,
            fontWeight: 800,
            letterSpacing: 2.2,
            textTransform: "uppercase",
          }}
        >
          {activeBadge}
        </span>
      </div>
    </AbsoluteFill>
  );
};
