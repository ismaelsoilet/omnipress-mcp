import React, { useMemo } from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ActData, ActTimeline, WordTiming } from "../types";

export interface WordByWordCaptionsProps {
  introDurationFrames?: number;
  captionsData?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
  bottomPosition?: number;
  fontSize?: number;
  customHighlightWords?: {
    red?: string[];
    green?: string[];
    gold?: string[];
  };
}

// Channel-provided emphasis vocabulary. The core ships no language-specific words.
const DEFAULT_RED_WORDS = new Set<string>([]);

const DEFAULT_GREEN_WORDS = new Set<string>([]);

const DEFAULT_GOLD_WORDS = new Set<string>([]);

/**
 * WordByWordCaptions — Motor de Legendas de Ultra-Retenção (Palavra por Palavra)
 * Sincronização milimétrica baseada em Whisper com pop animation (escala dinâmica),
 * cores temáticas dinâmicas, contorno preto de alta densidade e zero repetições.
 */
export const WordByWordCaptions: React.FC<WordByWordCaptionsProps> = ({
  introDurationFrames = 0,
  captionsData,
  actTimelines = [],
  bottomPosition = 420,
  fontSize = 72,
  customHighlightWords,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const redWords = useMemo(() => {
    const s = new Set(DEFAULT_RED_WORDS);
    (customHighlightWords?.red || []).forEach((w) => s.add(w.toLowerCase()));
    return s;
  }, [customHighlightWords?.red]);

  const greenWords = useMemo(() => {
    const s = new Set(DEFAULT_GREEN_WORDS);
    (customHighlightWords?.green || []).forEach((w) => s.add(w.toLowerCase()));
    return s;
  }, [customHighlightWords?.green]);

  const goldWords = useMemo(() => {
    const s = new Set(DEFAULT_GOLD_WORDS);
    (customHighlightWords?.gold || []).forEach((w) => s.add(w.toLowerCase()));
    return s;
  }, [customHighlightWords?.gold]);

  if (!captionsData || !actTimelines || actTimelines.length === 0) {
    return null;
  }

  // Tempo global em segundos após a introdução
  const currentGlobalSec = (frame - introDurationFrames) / fps;

  // Encontra o ato ativo
  const activeAct = useMemo(() => {
    return actTimelines.find(
      (act) => currentGlobalSec >= act.globalStart && currentGlobalSec < act.globalEnd
    );
  }, [currentGlobalSec, actTimelines]);

  if (!activeAct) return null;

  const actInfo = captionsData[activeAct.id] || (captionsData as any);
  if (!actInfo || !actInfo.words || actInfo.words.length === 0) return null;

  const timeInAct = currentGlobalSec - activeAct.globalStart;

  // Encontra a palavra ativa com transição estrita e limpa (sem atraso e sem sobreposição)
  let activeWordIndex = -1;
  for (let i = 0; i < actInfo.words.length; i++) {
    const w = actInfo.words[i];
    const nextW = actInfo.words[i + 1];

    if (timeInAct >= w.start) {
      if (nextW) {
        if (timeInAct < nextW.start) {
          // Se houver uma pausa acústica longa (> 0.28s), mantém a palavra visível até w.end + 0.20s
          const isPause = nextW.start - w.end > 0.28;
          if (!isPause || timeInAct <= w.end + 0.20) {
            activeWordIndex = i;
            break;
          }
        }
      } else {
        // Última palavra do vídeo (limite de 0.40s pós-fala)
        if (timeInAct <= w.end + 0.40) {
          activeWordIndex = i;
          break;
        }
      }
    }
  }

  if (activeWordIndex === -1) {
    return null;
  }

  const activeWordObj = actInfo.words[activeWordIndex];
  const rawWord = activeWordObj.word.trim();

  // Limpa pontuações neutras mantendo pontuação de ênfase (? e !)
  const displayWord = rawWord.replace(/[.,:;—]/g, "").trim();
  const cleanWord = displayWord.toLowerCase().replace(/[.,!?;:"'()—]/g, "");

  // Animação de entrada rápida da palavra (Snappy Pop / Spring)
  const wordStartFrame = Math.round(activeWordObj.start * fps) + introDurationFrames;
  const frameSinceWordStart = Math.max(0, frame - wordStartFrame);

  const popProgress = spring({
    frame: frameSinceWordStart,
    fps,
    config: {
      damping: 14,
      mass: 0.28,
      stiffness: 260,
    },
  });

  const scale = interpolate(popProgress, [0, 1], [0.82, 1.0]);

  // Dimensionamento dinâmico de fonte para impedir qualquer colisão ou overflow nas bordas
  let effectiveFontSize = fontSize;
  if (displayWord.length > 12) {
    effectiveFontSize = Math.round(fontSize * 0.74);
  } else if (displayWord.length > 8) {
    effectiveFontSize = Math.round(fontSize * 0.86);
  }

  // Determina cor de destaque emocional da palavra
  let textColor = "#FFFFFF";
  let glowColor = "rgba(0, 0, 0, 0.9)";
  let isKeyword = false;

  if (redWords.has(cleanWord)) {
    textColor = "#FF2A55";
    glowColor = "rgba(255, 42, 85, 0.75)";
    isKeyword = true;
  } else if (greenWords.has(cleanWord)) {
    textColor = "#00FF88";
    glowColor = "rgba(0, 255, 136, 0.75)";
    isKeyword = true;
  } else if (goldWords.has(cleanWord)) {
    textColor = "#FFE500";
    glowColor = "rgba(255, 229, 0, 0.85)";
    isKeyword = true;
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: bottomPosition,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 90,
        pointerEvents: "none",
        padding: "0 30px",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          maxWidth: "92%",
          boxSizing: "border-box",
          backgroundColor: "rgba(6, 8, 12, 0.88)",
          border: isKeyword
            ? `2.5px solid ${textColor}`
            : "1.5px solid rgba(255, 255, 255, 0.22)",
          borderRadius: 20,
          padding: "16px 36px",
          backdropFilter: "blur(14px)",
          boxShadow: isKeyword
            ? `0 12px 35px rgba(0, 0, 0, 0.95), 0 0 32px ${glowColor}`
            : "0 10px 30px rgba(0, 0, 0, 0.9)",
        }}
      >
        <span
          style={{
            fontFamily: "'Impact', 'Arial Black', -apple-system, sans-serif",
            fontSize: isKeyword ? effectiveFontSize + 4 : effectiveFontSize,
            fontWeight: 900,
            color: textColor,
            textTransform: "uppercase",
            letterSpacing: 2.2,
            WebkitTextStroke: "6px rgba(0, 0, 0, 0.98)",
            paintOrder: "stroke fill",
            textShadow: isKeyword
              ? `0 0 22px ${glowColor}`
              : "0 4px 14px rgba(0, 0, 0, 0.95)",
            lineHeight: 1.05,
            whiteSpace: "nowrap",
          }}
        >
          {displayWord}
        </span>
      </div>
    </div>
  );
};
