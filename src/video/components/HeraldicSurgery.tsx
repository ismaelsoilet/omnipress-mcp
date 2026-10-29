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
  beforeSrc?: string;
  afterSrc?: string;
  imperialFlagSrc?: string; // Legacy alias
  republicFlagSrc?: string; // Legacy alias
  badge?: string;
  beforeBadge?: string;
  afterBadge?: string;
}

/**
 * HeraldicSurgery (ImageMorph) — Animação Universal de Metamorfose Visual / Transição de Documentos.
 * Executa a substituição cinematográfica em tempo real entre dois estados visuais (Antes e Depois):
 * 1. Frame 0 a ~35%: Exibe o elemento original (beforeSrc) com sutil Ken Burns.
 * 2. Frame ~35% a ~58%: Fade cruzado cirúrgico com flash óptico no ponto central.
 * 3. Frame ~58% ao fim: O novo elemento (afterSrc) consolidado em movimento cinematográfico.
 */
export const HeraldicSurgery: React.FC<HeraldicSurgeryProps> = ({
  durationInFrames,
  beforeSrc,
  afterSrc,
  imperialFlagSrc,
  republicFlagSrc,
  badge = "METAMORFOSE VISUAL",
  beforeBadge,
  afterBadge,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  const resolvedBefore = beforeSrc || imperialFlagSrc || "";
  const resolvedAfter = afterSrc || republicFlagSrc || "";

  const resolveMediaUrl = (src: string) => {
    if (!src) return "";
    return src.startsWith("http") || src.startsWith("data:") ? src : staticFile(src);
  };

  // Escala contínua e suave para dinamismo cinematográfico
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.10], {
    extrapolateRight: "clamp",
  });

  // Janela de transição cirúrgica: frame 35% a 58%
  const transStart = Math.round(durationInFrames * 0.35);
  const transEnd = Math.round(durationInFrames * 0.58);

  // Opacidades
  const beforeOpacity = interpolate(
    frame,
    [transStart, transEnd],
    [1.0, 0.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const afterOpacity = interpolate(
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
    ? (afterBadge || badge || "TRANSFORMAÇÃO CONCLUÍDA")
    : (beforeBadge || badge || "METAMORFOSE VISUAL");

  const bgSrc = isAfterSurgery ? resolvedAfter : resolvedBefore;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "var(--omni-background, #0B1220)",
        overflow: "hidden",
      }}
    >
      {/* 1. Camada de Fundo Ambiente com Desfoque */}
      {bgSrc && (
        <AbsoluteFill style={{ overflow: "hidden", contain: "paint" }}>
          <Img
            src={resolveMediaUrl(bgSrc)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              filter: "blur(14px) brightness(0.32)",
              transform: "scale(1.15)",
            }}
          />
        </AbsoluteFill>
      )}

      {/* 2. Imagem Inicial (Before) com Fade-out */}
      {resolvedBefore && (
        <AbsoluteFill
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "center center",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: beforeOpacity,
          }}
        >
          <Img
            src={resolveMediaUrl(resolvedBefore)}
            style={{
              maxWidth: "92%",
              maxHeight: "92%",
              objectFit: "contain",
              boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85)",
            }}
          />
        </AbsoluteFill>
      )}

      {/* 3. Imagem Final (After) com Fade-in */}
      {resolvedAfter && (
        <AbsoluteFill
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "center center",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: afterOpacity,
          }}
        >
          <Img
            src={resolveMediaUrl(resolvedAfter)}
            style={{
              maxWidth: "92%",
              maxHeight: "92%",
              objectFit: "contain",
              boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85)",
            }}
          />
        </AbsoluteFill>
      )}

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
          border: `1.2px solid ${isAfterSurgery ? "rgba(var(--omni-success-rgb, 16, 185, 129), 0.6)" : "rgba(var(--omni-accent-rgb, 59, 130, 246), 0.6)"}`,
          borderLeft: `5px solid ${isAfterSurgery ? "var(--omni-success, #10B981)" : "var(--omni-accent, #3B82F6)"}`,
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
