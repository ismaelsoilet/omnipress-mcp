import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ActData, ActTimeline, WordTiming } from "../types";

export interface CaptionChunkItem {
  text: string;
  startInSeconds?: number;
  durationInSeconds?: number;
  start?: number;
  end?: number;
  words?: WordTiming[];
}

export interface SynchronizedCaptionsProps {
  introDurationFrames?: number;
  isVertical?: boolean;
  captionsData?: Record<string, ActData> | CaptionChunkItem[];
  actTimelines?: ActTimeline[];
}

/**
 * SynchronizedCaptions — Renderizador de Legendas Dinâmicas Sincronizadas Palavra por Palavra.
 * Posicionamento limpo na parte inferior (bottom: 54px), sem atrasos, sem renderização dupla,
 * iluminando cada palavra pronunciada no exato momento da fala.
 */
export const SynchronizedCaptions: React.FC<SynchronizedCaptionsProps> = ({
  introDurationFrames = 120,
  isVertical = false,
  captionsData,
  actTimelines = [],
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!captionsData) {
    return null;
  }

  // Tempo global em segundos após a vinheta (Regra 10: sincronizado ao áudio master)
  const currentGlobalSec = (frame - introDurationFrames) / fps;

  // Não exibe legendas durante a vinheta inicial
  if (currentGlobalSec < 0) {
    return null;
  }

  // CASO 1: captionsData é um array direto de chunks (formato padrão do Whisper)
  if (Array.isArray(captionsData)) {
    const activeChunk = captionsData.find((chunk) => {
      const start = chunk.startInSeconds ?? chunk.start ?? 0;
      const duration =
        chunk.durationInSeconds ??
        (chunk.end !== undefined ? chunk.end - start : 1.5);
      const end = start + duration;
      return currentGlobalSec >= start && currentGlobalSec < end + 0.04;
    });

    if (!activeChunk) return null;

    const words =
      activeChunk.words && activeChunk.words.length > 0
        ? activeChunk.words
        : activeChunk.text.split(" ").map((w) => ({
            word: w,
            start: activeChunk.startInSeconds ?? activeChunk.start ?? 0,
            end:
              (activeChunk.startInSeconds ?? activeChunk.start ?? 0) +
              (activeChunk.durationInSeconds ?? 1.5),
          }));

    return (
      <div
        style={{
          position: "absolute",
          bottom: isVertical ? 360 : 54,
          left: "50%",
          transform: "translateX(-50%)",
          width: "90%",
          maxWidth: isVertical ? 920 : 1280,
          zIndex: 50,
          display: "flex",
          justifyContent: "center",
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(8, 10, 14, 0.92)",
            border: "1.2px solid rgba(212, 175, 55, 0.40)",
            boxShadow:
              "0 8px 24px rgba(0, 0, 0, 0.85), 0 0 16px rgba(212, 175, 55, 0.12)",
            borderRadius: isVertical ? 14 : 12,
            padding: isVertical ? "12px 20px" : "10px 26px",
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            alignItems: "center",
            gap: isVertical ? "5px 8px" : "4px 8px",
            textAlign: "center",
          }}
        >
          {words.map((w, idx) => {
            const isActive =
              currentGlobalSec >= w.start && currentGlobalSec <= w.end;
            const isPast = currentGlobalSec > w.end;

            return (
              <span
                key={idx}
                style={{
                  fontFamily:
                    "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                  fontSize: isVertical ? 32 : 27,
                  fontWeight: isActive ? 900 : isPast ? 700 : 500,
                  color: isActive
                    ? "#FFD700"
                    : isPast
                    ? "#FFFFFF"
                    : "rgba(225, 230, 238, 0.65)",
                  backgroundColor: isActive
                    ? "rgba(212, 175, 55, 0.28)"
                    : "transparent",
                  borderBottom: isActive
                    ? "2.5px solid #FFD700"
                    : "2.5px solid transparent",
                  borderRadius: 4,
                  padding: "1px 5px",
                  letterSpacing: "0.2px",
                  textShadow: isActive
                    ? "0 0 14px rgba(255, 215, 0, 0.8), 0 2px 4px rgba(0,0,0,0.95)"
                    : "0 2px 4px rgba(0, 0, 0, 0.85)",
                  transform: isActive ? "scale(1.06)" : "scale(1.0)",
                  transition: "color 0.04s ease, transform 0.04s ease",
                  WebkitTextStroke: "1px rgba(0, 0, 0, 0.65)",
                }}
              >
                {w.word}
              </span>
            );
          })}
        </div>
      </div>
    );
  }

  // CASO 2: captionsData agrupado por Atos
  if (!actTimelines || actTimelines.length === 0) {
    return null;
  }

  const activeAct = actTimelines.find(
    (act) =>
      currentGlobalSec >= act.globalStart && currentGlobalSec < act.globalEnd
  );

  if (!activeAct) return null;

  const actInfo = (captionsData as Record<string, ActData>)[activeAct.id];
  if (!actInfo || !actInfo.chunks) return null;

  const timeInAct = currentGlobalSec - activeAct.globalStart;

  const activeChunk = actInfo.chunks.find(
    (chunk) =>
      timeInAct >= chunk.start && timeInAct <= chunk.end + 0.04
  );

  if (!activeChunk) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: isVertical ? 360 : 54,
        left: "50%",
        transform: "translateX(-50%)",
        width: "90%",
        maxWidth: isVertical ? 920 : 1280,
        zIndex: 50,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(8, 10, 14, 0.90)",
          backdropFilter: "blur(12px)",
          border: "1.2px solid rgba(212, 175, 55, 0.40)",
          boxShadow:
            "0 8px 24px rgba(0, 0, 0, 0.85), 0 0 16px rgba(212, 175, 55, 0.12)",
          borderRadius: isVertical ? 14 : 12,
          padding: isVertical ? "12px 20px" : "10px 26px",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: isVertical ? "5px 8px" : "4px 8px",
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
                fontFamily:
                  "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                fontSize: isVertical ? 32 : 27,
                fontWeight: isActive ? 900 : isPast ? 700 : 500,
                color: isActive
                  ? "#FFD700"
                  : isPast
                  ? "#FFFFFF"
                  : "rgba(225, 230, 238, 0.65)",
                backgroundColor: isActive
                  ? "rgba(212, 175, 55, 0.28)"
                  : "transparent",
                borderBottom: isActive
                  ? "2.5px solid #FFD700"
                  : "2.5px solid transparent",
                borderRadius: 4,
                padding: "1px 5px",
                letterSpacing: "0.2px",
                textShadow: isActive
                  ? "0 0 14px rgba(255, 215, 0, 0.8), 0 2px 4px rgba(0,0,0,0.95)"
                  : "0 2px 4px rgba(0, 0, 0, 0.85)",
                transform: isActive ? "scale(1.06)" : "scale(1.0)",
                transition: "color 0.04s ease, transform 0.04s ease",
                WebkitTextStroke: "1px rgba(0, 0, 0, 0.65)",
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
