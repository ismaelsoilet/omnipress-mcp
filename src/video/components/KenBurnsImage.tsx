import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { KenBurnsSceneProps } from "../types";
import { FilmGrain } from "./FilmGrain";
import { KineticCaption } from "./KineticCaption";

export const KenBurnsImage: React.FC<KenBurnsSceneProps> = ({
  imageSrc,
  direction = "zoom-in",
  headline,
  caption,
  badge,
  showFilmGrain = true,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  // Cálculo das interpolações de câmera (Ken Burns suave)
  const isVertical = height > width;

  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;

  if (direction === "zoom-in") {
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.15], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "zoom-out") {
    scale = interpolate(frame, [0, durationInFrames], [1.15, 1.0], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-left") {
    scale = 1.12;
    translateX = interpolate(frame, [0, durationInFrames], [20, -20], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-right") {
    scale = 1.12;
    translateX = interpolate(frame, [0, durationInFrames], [-20, 20], {
      extrapolateRight: "clamp",
    });
  }

  // Fade in sutil nos primeiros 10 frames
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0C10", overflow: "hidden", opacity: fadeIn }}>
      {/* 1. Imagem com Movimento Contínuo de Câmera */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: "center center",
        }}
      >
        <Img
          src={imageSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "brightness(0.72) contrast(1.05)",
          }}
        />
      </AbsoluteFill>

      {/* 2. Vinheta e Gradiente Radial Escuro Protetor */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at center, transparent 35%, rgba(6, 8, 12, 0.75) 85%, rgba(4, 5, 8, 0.95) 100%)",
        }}
      />

      {/* 3. Granulação de Película de Época */}
      {showFilmGrain && <FilmGrain opacity={0.07} />}

      {/* 4. Caixa Protetora Tática de Metadados do Arquivo (Topo Superior Esquerdo — Regra 08) */}
      {(headline || badge) && (
        <div
          style={{
            position: "absolute",
            top: isVertical ? 150 : 48,
            left: isVertical ? 40 : 64,
            maxWidth: isVertical ? "88%" : "55%",
            backgroundColor: "rgba(8, 10, 14, 0.88)",
            border: "1.5px solid rgba(212, 175, 55, 0.45)",
            borderLeft: "6px solid #D4AF37",
            borderRadius: isVertical ? 14 : 10,
            padding: isVertical ? "18px 26px" : "18px 28px",
            backdropFilter: "blur(12px)",
            boxShadow: "0 8px 28px rgba(0, 0, 0, 0.75)",
            zIndex: 30,
          }}
        >
          {badge && (
            <div
              style={{
                color: "#D4AF37",
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: isVertical ? 18 : 18,
                fontWeight: 800,
                letterSpacing: isVertical ? 2.5 : 3,
                textTransform: "uppercase",
                marginBottom: isVertical ? 6 : 6,
              }}
            >
              {badge}
            </div>
          )}

          {headline && (
            <h2
              style={{
                margin: 0,
                color: "#FFFFFF",
                fontSize: isVertical ? 36 : 34,
                fontWeight: 900,
                fontFamily: "'Cinzel', Georgia, serif",
                letterSpacing: 2,
                textTransform: "uppercase",
                textShadow: "0 3px 8px rgba(0,0,0,0.95)",
                lineHeight: 1.22,
              }}
            >
              {headline}
            </h2>
          )}
        </div>
      )}
    </AbsoluteFill>
  );
};
