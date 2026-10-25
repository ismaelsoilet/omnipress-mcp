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

  // 1. Movimentação Cinematográfica Dinâmica e Fluida
  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;

  if (direction === "zoom-in") {
    // Zoom suave e elegante de 1.0 para 1.12
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.12], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "zoom-out") {
    // Zoom out suave de 1.12 para 1.0
    scale = interpolate(frame, [0, durationInFrames], [1.12, 1.0], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-left") {
    scale = 1.08;
    translateX = interpolate(frame, [0, durationInFrames], [45, -45], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "pan-right") {
    scale = 1.08;
    translateX = interpolate(frame, [0, durationInFrames], [-45, 45], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "tilt-down") {
    scale = 1.08;
    translateY = interpolate(frame, [0, durationInFrames], [-28, 28], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "snap-zoom") {
    // Snap zoom pericial com amortecimento cúbico nos primeiros 16 frames e deriva contínua
    const snap = interpolate(frame, [0, 16], [1.0, 1.11], {
      extrapolateRight: "clamp",
      easing: (t) => 1 - Math.pow(1 - t, 3),
    });
    const drift = interpolate(frame, [16, durationInFrames], [0, 0.04], {
      extrapolateRight: "clamp",
    });
    scale = snap + drift;
  } else if (direction === "subtle-zoom") {
    // Zoom sutil e discreto para enquadramentos de pinturas e retratos (1.0 para 1.03)
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.03], {
      extrapolateRight: "clamp",
    });
  } else if (direction === "dramatic-push") {
    // Avanço dramático e marcante de 1.0 para 1.16
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.16], {
      extrapolateRight: "clamp",
    });
  } else {
    scale = interpolate(frame, [0, durationInFrames], [1.0, 1.10], {
      extrapolateRight: "clamp",
    });
  }

  // 2. Transições e Revelação Suave
  // Dissolvência suave de entrada nos primeiros 6 frames
  const entryOpacity = interpolate(frame, [0, 6], [0.25, 1.0], {
    extrapolateRight: "clamp",
  });

  // Flash óptico de obturador nos primeiros 4 frames
  const flashOpacity = interpolate(frame, [0, 1, 4], [0.35, 0.15, 0.0], {
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
      <AbsoluteFill style={{ overflow: "hidden", contain: "paint" }}>
        <Img
          src={imageSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "blur(14px) brightness(0.32)",
            transform: "scale(1.15)",
          }}
        />
      </AbsoluteFill>

      {/* 2. Imagem Principal Nítida em Movimento Dinâmico e Entrada Suave */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: "center center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: entryOpacity,
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

      {/* 7. Tag / Legenda Superior das Imagens (Destaque cinematográfico proporcional e legível) */}
      {badge && (
        <div
          style={{
            position: "absolute",
            top: isVertical ? 38 : 34,
            left: isVertical ? 32 : 40,
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            backgroundColor: "rgba(8, 10, 14, 0.88)",
            border: "1.2px solid rgba(212, 175, 55, 0.50)",
            borderLeft: "4.5px solid #D4AF37",
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
            {badge}
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};
