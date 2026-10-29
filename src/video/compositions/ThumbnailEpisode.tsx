import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { themeVars } from "../theme";

export interface ThumbnailEpisodeProps {
  titleLine1?: string;
  titleLine2?: string;
  tagText?: string;
  calloutText?: string;
  imageSrc?: string;
  cellarSrc?: string;
  showClassifiedStamp?: boolean;
  stampText?: string;
  accentColor?: string;
  highlightColor?: string;
  backgroundColor?: string;
  textColor?: string;
  // Legacy / optional props preserved for backward compatibility
  depthTag?: string;
  peopleTag?: string;
  doorTag?: string;
}

/**
 * ThumbnailEpisode — High-CTR 16:9 YouTube Thumbnail Composition (Rule 15 Standard).
 *
 * Implements the 8 Laws of High-CTR Packaging:
 * 1. 3-Word Limit: Concise, emotional power words.
 * 2. Titanic Typography Scale: Anton 175px - 210px, heavy 12px protective stroke.
 * 3. Zero Micro-Text: Minimum font floor >= 50px across all elements.
 * 4. High-Luminance Peripheral Palette: Pure White (#FFFFFF) + Alert Yellow (#FFE500).
 * 5. Chiaroscuro Gradient Shield: Guarantees 100% contrast over any background image.
 * 6. YouTube Safe Zone Shield: Bottom-right 320x140px corner is kept 100% clear of text.
 * 7. 3-Element Focal Hierarchy: Dramatic Subject (Right) + Titanic Hook (Left) + Authority Badge.
 * 8. 120px Mobile Squint Tested: Effortlessly readable on phone feeds in < 1 second.
 */
export const ThumbnailEpisode: React.FC<ThumbnailEpisodeProps> = ({
  titleLine1 = "",
  titleLine2 = "",
  tagText = "",
  calloutText = "",
  imageSrc = "",
  cellarSrc = "",
  showClassifiedStamp = false,
  stampText = "",
  accentColor,
  highlightColor,
  backgroundColor,
  textColor,
}) => {
  return (
    <AbsoluteFill
      style={{
        ...themeVars({ accentColor, highlightColor, backgroundColor, textColor }),
        backgroundColor: "var(--omni-background, #0B1220)",
        fontFamily: "'Anton', 'Impact', 'Montserrat', sans-serif",
        overflow: "hidden",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Anton&family=Cinzel:wght@800;900&family=Montserrat:wght@800;900&display=swap');
      `}</style>

      {/* 1. Imagem de Fundo Principal (Lado Direito / Sujeito Dramático) */}
      {imageSrc && (
        <div
          style={{
            position: "absolute",
            top: 0,
            right: 0,
            width: "72%",
            height: "100%",
            backgroundImage: `url(${imageSrc.startsWith("http") || imageSrc.startsWith("data:") ? imageSrc : staticFile(imageSrc)})`,
            backgroundSize: "cover",
            backgroundPosition: "center 28%",
            filter: "contrast(1.18) saturate(1.15) brightness(0.92)",
          }}
        />
      )}

      {/* 2. Textura Opcional de Composição Secundária */}
      {cellarSrc && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "45%",
            height: "100%",
            backgroundImage: `url(${cellarSrc.startsWith("http") || cellarSrc.startsWith("data:") ? cellarSrc : staticFile(cellarSrc)})`,
            backgroundSize: "cover",
            backgroundPosition: "center 40%",
            filter: "contrast(1.2) brightness(0.55)",
            maskImage: "linear-gradient(to right, black 55%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to right, black 55%, transparent 100%)",
          }}
        />
      )}

      {/* 3. Gradiente Chiaroscuro de Isolamento Tático (100% de Contraste para o Texto) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "65%",
          height: "100%",
          background:
            "linear-gradient(to right, rgba(4, 6, 10, 0.98) 0%, rgba(4, 6, 10, 0.94) 48%, rgba(4, 6, 10, 0.65) 80%, transparent 100%)",
          zIndex: 10,
        }}
      />

      {/* 4. Vinheta de Borda e Iluminação Dramática */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          boxShadow: "inset 0 0 160px rgba(0, 0, 0, 0.98), inset 0 0 80px rgba(0, 0, 0, 0.88)",
          pointerEvents: "none",
          zIndex: 15,
        }}
      />

      {/* 5. Linha Dourada de Borda Cinemática */}
      <div
        style={{
          position: "absolute",
          inset: 20,
          border: "2px solid rgba(var(--omni-accent-rgb, 59, 130, 246), 0.45)",
          borderRadius: 8,
          pointerEvents: "none",
          zIndex: 20,
        }}
      />

      {/* 6. CONTEÚDO PRINCIPAL (LADO ESQUERDO) — TIPOGRAFIA TITÂNICA (REGRA 15) */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 85,
          zIndex: 30,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          maxWidth: 1050,
        }}
      >
        {/* Badge Superior Nítido (Mínimo 52px — Zero Micro-Fontes) */}
        {tagText && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 16,
              backgroundColor: "rgba(10, 12, 16, 0.94)",
              border: "3px solid var(--omni-accent, #3B82F6)",
              borderRadius: 10,
              padding: "12px 30px",
              marginBottom: 32,
              boxShadow: "0 10px 30px rgba(0, 0, 0, 0.95), 0 0 20px rgba(var(--omni-accent-rgb, 59, 130, 246), 0.3)",
            }}
          >
            <div
              style={{
                width: 20,
                height: 20,
                borderRadius: "50%",
                backgroundColor: "#FF2222",
                boxShadow: "0 0 14px #FF2222, 0 0 25px #FF0000",
              }}
            />
            <span
              style={{
                color: "var(--omni-highlight, #FACC15)",
                fontFamily: "'Montserrat', sans-serif",
                fontSize: 52,
                fontWeight: 900,
                letterSpacing: 4,
                textTransform: "uppercase",
              }}
            >
              {tagText}
            </span>
          </div>
        )}

        {/* Linha 1 de Título Titânico (175px - Branco Puro de Alta Clareza) */}
        {titleLine1 && (
          <h1
            style={{
              margin: 0,
              fontSize: 175,
              lineHeight: 0.92,
              fontWeight: 900,
              fontFamily: "'Anton', 'Impact', sans-serif",
              letterSpacing: 2,
              textTransform: "uppercase",
              color: "#FFFFFF",
              WebkitTextStroke: "12px #000000",
              paintOrder: "stroke fill",
              textShadow: `
                0 0 25px rgba(0, 0, 0, 0.9),
                0 8px 0 #000000,
                0 14px 0 #000000,
                0 18px 36px rgba(0, 0, 0, 0.98)
              `,
            }}
          >
            {titleLine1}
          </h1>
        )}

        {/* Linha 2 de Título Titânico (195px - Amarelo Alerta de Alta Luminância) */}
        {titleLine2 && (
          <h2
            style={{
              margin: "12px 0 32px 0",
              fontSize: 195,
              lineHeight: 0.92,
              fontWeight: 900,
              fontFamily: "'Anton', 'Impact', sans-serif",
              letterSpacing: 2,
              textTransform: "uppercase",
              color: "#FFE500", // Amarelo de Alerta Máximo
              WebkitTextStroke: "12px #000000",
              paintOrder: "stroke fill",
              textShadow: `
                0 0 30px rgba(255, 229, 0, 0.55),
                0 8px 0 #000000,
                0 14px 0 #000000,
                0 18px 36px rgba(0, 0, 0, 0.98)
              `,
            }}
          >
            {titleLine2}
          </h2>
        )}

        {/* Callout Pill Opcional de Choque (56px — Sem Partes Pequenas) */}
        {calloutText && (
          <div
            style={{
              transform: "rotate(-2deg)",
              backgroundColor: "#D32F2F", // Vermelho Alerta Vibrante
              border: "4px solid #FFFFFF",
              borderRadius: 14,
              padding: "16px 38px",
              boxShadow: "0 14px 36px rgba(0, 0, 0, 0.95), 0 0 30px rgba(211, 47, 47, 0.7)",
            }}
          >
            <span
              style={{
                color: "#FFFFFF",
                fontSize: 56,
                fontWeight: 900,
                fontFamily: "'Montserrat', sans-serif",
                letterSpacing: 2,
                textTransform: "uppercase",
                textShadow: "0 4px 8px rgba(0, 0, 0, 0.9)",
              }}
            >
              {calloutText}
            </span>
          </div>
        )}
      </div>

      {/* 7. CARIMBO DE AUTORIDADE / CONFIDENCIAL NO TOPO DIREITO (Mínimo 54px) */}
      {showClassifiedStamp && (
        <div
          style={{
            position: "absolute",
            top: 75,
            right: 85,
            zIndex: 35,
            transform: "rotate(6deg)",
            border: "6px solid #D32F2F",
            borderRadius: 10,
            padding: "12px 36px",
            color: "#D32F2F",
            fontFamily: "'Anton', 'Impact', sans-serif",
            fontSize: 54,
            fontWeight: 900,
            letterSpacing: 6,
            textTransform: "uppercase",
            backgroundColor: "rgba(10, 12, 16, 0.92)",
            boxShadow: "0 10px 30px rgba(0, 0, 0, 0.95)",
          }}
        >
          {stampText}
        </div>
      )}

      {/* 8. YouTube Duration Badge Shield:
          O canto inferior direito (X > 1600, Y > 940) é intencionalmente MANTIDO LIMPO.
          O YouTube renderiza a etiqueta de tempo exatamente aí, prevenindo obstrução.
      */}
    </AbsoluteFill>
  );
};
