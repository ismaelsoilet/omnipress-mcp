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

          {caption && (
            <div
              style={{
                marginTop: 10,
                color: "#CBD5E1",
                fontFamily: "'Montserrat', system-ui, sans-serif",
                fontSize: isVertical ? 18 : 17,
                fontWeight: 500,
                letterSpacing: 0.4,
                lineHeight: 1.35,
                borderTop: "1px solid rgba(212, 175, 55, 0.3)",
                paddingTop: 8,
              }}
            >
              {caption}
            </div>
          )}
        </div>
      )}

      {/* 5. Tarja / Selo Especial para Imagens de Arquivo Histórico Real */}
      {badge && badge.toUpperCase().includes("HISTÓRICO") && (
        <div
          style={{
            position: "absolute",
            top: isVertical ? 150 : 48,
            right: isVertical ? 40 : 64,
            display: "flex",
            alignItems: "center",
            gap: 10,
            backgroundColor: "rgba(10, 12, 16, 0.90)",
            border: "1.5px solid #D4AF37",
            borderRadius: 8,
            padding: "8px 18px",
            backdropFilter: "blur(8px)",
            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.8)",
            zIndex: 30,
          }}
        >
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: "#22C55E",
              boxShadow: "0 0 10px #22C55E",
            }}
          />
          <span
            style={{
              color: "#F1F5F9",
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: 14,
              fontWeight: 800,
              letterSpacing: 2,
              textTransform: "uppercase",
            }}
          >
            ARQUIVO REAL // DESCLASSIFICADO
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};
