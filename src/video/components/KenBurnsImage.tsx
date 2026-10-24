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
import { DustParticles } from "./DustParticles";

/**
 * KenBurnsImage — Renderizador Cinematográfico de Imagens de Arquivo.
 * Cumpre as regras do usuário:
 * 1. Começa SEMPRE com escala 1.0 (sem zoom forte inicial) e faz movimentação sutil.
 * 2. Não coloca caixas grandes de texto na parte superior que tampem rostos de retratos.
 * 3. Utiliza camada de fundo com desfoque ambiente + imagem principal preservada.
 * 4. Elimina textos duplicados (delega legendas exclusivamente para o SynchronizedCaptions).
 */
export const KenBurnsImage: React.FC<KenBurnsSceneProps> = ({
  imageSrc,
  direction = "zoom-in",
  badge,
  showFilmGrain = true,
  showDust = true,
  brightness = 1.0,
  contrast = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  const isVertical = height > width;

  // 1. Movimentação Cinematográfica Suave (Começa SEMPRE em 1.0, sem zoom forte)
  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;

  if (direction === "zoom-in") {
    // Zoom suave de 1.0 para 1.045
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.045], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "zoom-out") {
    // Zoom suave de 1.045 para 1.0
    scale = interpolate(frame, [0, durationInFrames], [1.045, 1.0], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-left") {
    scale = 1.025;
    translateX = interpolate(frame, [0, durationInFrames], [14, -14], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-right") {
    scale = 1.025;
    translateX = interpolate(frame, [0, durationInFrames], [-14, 14], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "tilt-down") {
    scale = 1.03;
    translateY = interpolate(frame, [0, durationInFrames], [-12, 12], {
      extrapolateRight: "clamp",
    });
  } else {
    // Fallback padrão: zoom-in sutil
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.04], {
      extrapolateRight: "clamp",
    });
  }

  // 2. Transição luminosa suave nos primeiros 3 frames (shutter flash cinematográfico)
  const flashOpacity = interpolate(frame, [0, 1, 3], [0.25, 0.12, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06080C",
        overflow: "hidden",
      }}
    >
      {/* 1. Camada de Fundo Ambiente com Desfoque (Garante preenchimento 16:9 sem cortar retratos) */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={imageSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "blur(28px) brightness(0.32)",
            transform: "scale(1.15)",
          }}
        />
      </AbsoluteFill>

      {/* 2. Imagem Principal Nítida em Movimento Sutil (Começa em scale 1.0) */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: "center center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Img
          src={imageSrc}
          style={{
            maxWidth: "100%",
            maxHeight: "100%",
            objectFit: "contain",
            filter: `brightness(${brightness}) contrast(${contrast})`,
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85)",
          }}
        />
      </AbsoluteFill>

      {/* 3. Flash Óptico Suave de Entrada */}
      {flashOpacity > 0.01 && (
        <AbsoluteFill
          style={{
            backgroundColor: "rgba(255, 248, 230, 0.8)",
            mixBlendMode: "screen",
            opacity: flashOpacity,
            pointerEvents: "none",
          }}
        />
      )}

      {/* 4. Vinheta Protetora Suave nas Bordas */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at center, transparent 75%, rgba(6, 8, 12, 0.35) 92%, rgba(4, 5, 8, 0.65) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* 5. Partículas de Poeira Luminosa Flutuante */}
      {showDust && <DustParticles count={isVertical ? 8 : 12} />}

      {/* 6. Granulação de Película de Época */}
      {showFilmGrain && <FilmGrain opacity={0.032} />}

      {/* 7. Tag Minimalista no Topo Esquerdo (Discreta, sem cobrir rostos) */}
      {badge && (
        <div
          style={{
            position: "absolute",
            top: isVertical ? 32 : 28,
            left: isVertical ? 28 : 36,
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            backgroundColor: "rgba(8, 10, 14, 0.82)",
            border: "1px solid rgba(212, 175, 55, 0.45)",
            borderLeft: "3.5px solid #D4AF37",
            borderRadius: 6,
            padding: "6px 14px",
            backdropFilter: "blur(10px)",
            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.7)",
            zIndex: 30,
          }}
        >
          <span
            style={{
              color: "#E2E8F0",
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: isVertical ? 13 : 13,
              fontWeight: 800,
              letterSpacing: 2,
              textTransform: "uppercase",
            }}
          >
            {badge}
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};
