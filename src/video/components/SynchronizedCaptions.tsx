import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ActData, ActTimeline } from "../types";

export interface SynchronizedCaptionsProps {
  introDurationFrames?: number;
  isVertical?: boolean;
  captionsData?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
}

/**
 * SynchronizedCaptions — Renderizador de Legendas Dinâmicas Sincronizadas Palavra por Palavra.
 * Alimentado pelo modelo Whisper com timestamps milimétricos dos áudios originais.
 * Cumpre a Regra 08 de Contraste e Legibilidade Visual (Backdrop escuro protetor e stroke de segurança).
 */
export const SynchronizedCaptions: React.FC<SynchronizedCaptionsProps> = ({
  introDurationFrames = 120,
  isVertical = false,
  captionsData,
  actTimelines = [],
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  // Se não houver dados de legenda ou timeline fornecidos, renderiza null com segurança
  if (!captionsData || !actTimelines || actTimelines.length === 0) {
    return null;
  }

  // Tempo global em segundos após a vinheta
  const currentGlobalSec = (frame - introDurationFrames) / fps;

  // Encontra o ato ativo
  const activeAct = useMemo(() => {
    return actTimelines.find(
      (act) => currentGlobalSec >= act.globalStart && currentGlobalSec < act.globalEnd
    );
  }, [currentGlobalSec, actTimelines]);

  if (!activeAct) return null;

  const actInfo = captionsData[activeAct.id];
  if (!actInfo || !actInfo.chunks) return null;


  const timeInAct = currentGlobalSec - activeAct.globalStart;

  // Encontra o bloco de legenda (chunk) ativo
  // Permitimos 0.35s de persistência pós-fala para leitura confortável
  const activeChunk = actInfo.chunks.find(
    (chunk) => timeInAct >= (chunk.start - 0.08) && timeInAct <= (chunk.end + 0.35)
  );

  if (!activeChunk) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: isVertical ? 380 : 100,
        left: "50%",
        transform: "translateX(-50%)",
        width: "90%",
        maxWidth: isVertical ? 920 : 1350,
        zIndex: 50,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(8, 10, 14, 0.90)",
          backdropFilter: "blur(14px)",
          border: "1.5px solid rgba(212, 175, 55, 0.45)",
          boxShadow: "0 12px 36px rgba(0, 0, 0, 0.9), 0 0 20px rgba(212, 175, 55, 0.15)",
          borderRadius: isVertical ? 16 : 14,
          padding: isVertical ? "16px 24px" : "16px 36px",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: isVertical ? "8px 12px" : "10px 16px",
          textAlign: "center",
        }}
      >
        {activeChunk.words.map((w, idx) => {
          const isActive = timeInAct >= w.start && timeInAct <= w.end;
          const isPast = timeInAct > w.end;

          return (
            <span
              key={idx}
              style={{
                fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                fontSize: isVertical ? 36 : 34,
                fontWeight: isActive ? 900 : isPast ? 700 : 500,
                color: isActive
                  ? "#FFD700"
                  : isPast
                  ? "#FFFFFF"
                  : "rgba(225, 230, 238, 0.40)",
                backgroundColor: isActive
                  ? "rgba(212, 175, 55, 0.28)"
                  : "transparent",
                borderBottom: isActive ? "3px solid #FFD700" : "3px solid transparent",
                borderRadius: 4,
                padding: "2px 8px",
                letterSpacing: isVertical ? "0.4px" : "0.5px",
                textShadow: isActive
                  ? "0 0 16px rgba(255, 215, 0, 0.8), 0 2px 4px rgba(0,0,0,0.95)"
                  : "0 2px 4px rgba(0, 0, 0, 0.85)",
                transform: isActive ? "scale(1.08)" : "scale(1.0)",
                transition: "color 0.05s ease, transform 0.05s ease",
                WebkitTextStroke: "1px rgba(0, 0, 0, 0.7)",
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
