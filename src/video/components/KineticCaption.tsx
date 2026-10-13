import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

export interface KineticCaptionProps {
  text: string;
  durationInFrames: number;
  fontSize?: number;
  isVertical?: boolean;
}

/**
 * KineticCaption — Legendas Dinâmicas de Alta Retenção (Estilo Documentário Viral).
 * Acompanha o andamento da fala do narrador em tempo real:
 * - Palavra ativa: Brilha em ouro (#FFD700) com fundo suave e escala ampliada.
 * - Palavras anteriores: Branco nítido (#FFFFFF).
 * - Próximas palavras: Dimmer translúcido (estimula a continuar assistindo até o final da frase).
 */
export const KineticCaption: React.FC<KineticCaptionProps> = ({
  text,
  durationInFrames,
  fontSize = 20,
  isVertical = false,
}) => {
  const frame = useCurrentFrame();

  // Divide o texto em palavras individuais preservando pontuação
  const words = useMemo(() => {
    if (!text) return [];
    return text.split(/\s+/).filter(Boolean);
  }, [text]);

  if (words.length === 0) return null;

  // Calcula o progresso relativo do slide (0.0 a 1.0)
  // Deixamos um leve respiro de 5% no início e no fim para naturalidade
  const progress = Math.min(1, Math.max(0, (frame - 5) / Math.max(1, durationInFrames - 10)));
  const activeIndex = Math.min(words.length - 1, Math.floor(progress * words.length));

  return (
    <div
      style={{
        lineHeight: 1.5,
        display: "flex",
        flexWrap: "wrap",
        gap: isVertical ? "6px 8px" : "6px 10px",
        justifyContent: "flex-start",
        alignItems: "center",
      }}
    >
      {words.map((word, i) => {
        const isActive = i === activeIndex;
        const isPast = i < activeIndex;

        return (
          <span
            key={i}
            style={{
              color: isActive
                ? "#FFD700"
                : isPast
                ? "#FFFFFF"
                : "rgba(225, 230, 235, 0.42)",
              fontWeight: isActive ? 900 : isPast ? 600 : 400,
              fontSize: isActive ? fontSize * 1.08 : fontSize,
              backgroundColor: isActive ? "rgba(212, 175, 55, 0.25)" : "transparent",
              borderBottom: isActive ? "2px solid #FFD700" : "2px solid transparent",
              borderRadius: 4,
              padding: "0 4px",
              letterSpacing: isActive ? "0.5px" : "normal",
              textShadow: isActive
                ? "0 0 12px rgba(255, 215, 0, 0.7), 0 2px 4px rgba(0,0,0,0.9)"
                : "0 2px 4px rgba(0,0,0,0.8)",
              transition: "color 0.08s ease, transform 0.08s ease",
              transform: isActive ? "scale(1.05)" : "scale(1.0)",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
