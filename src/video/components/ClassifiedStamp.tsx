import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ClassifiedStampProps {
  text?: string;
  color?: string;
  startFrame?: number;
  rotation?: number;
  scaleFactor?: number;
}

export const ClassifiedStamp: React.FC<ClassifiedStampProps> = ({
  text = "ARQUIVO DESCLASSIFICADO",
  color = "#D43F3A", // Vermelho carimbo oficial
  startFrame = 16,
  rotation = -9,
  scaleFactor = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const activeFrame = Math.max(0, frame - startFrame);

  // Animação de impacto com mola rápida (slamming onto the paper)
  const slamProgress = spring({
    frame: activeFrame,
    fps,
    config: {
      damping: 10,
      mass: 0.5,
      stiffness: 140,
    },
  });

  if (frame < startFrame) {
    return null;
  }

  const scale = interpolate(slamProgress, [0, 1], [2.2 * scaleFactor, 1.0 * scaleFactor]);
  const opacity = interpolate(slamProgress, [0, 0.4, 1], [0, 0.9, 0.95]);

  return (
    <div
      style={{
        display: "inline-block",
        transform: `rotate(${rotation}deg) scale(${scale})`,
        opacity,
        border: `3px double ${color}`,
        borderRadius: 6,
        padding: "6px 18px",
        color,
        fontFamily: "'Courier New', Courier, monospace",
        fontSize: 16,
        fontWeight: 900,
        letterSpacing: 4,
        textTransform: "uppercase",
        boxShadow: `0 0 15px rgba(212, 63, 58, 0.35)`,
        pointerEvents: "none",
        backgroundColor: "rgba(10, 12, 16, 0.85)",
        backdropFilter: "blur(4px)",
      }}
    >
      ★ {text} ★
    </div>
  );
};
