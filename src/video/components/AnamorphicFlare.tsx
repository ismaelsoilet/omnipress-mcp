import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

export interface AnamorphicFlareProps {
  color?: string;
  startFrame?: number;
  duration?: number;
}

export const AnamorphicFlare: React.FC<AnamorphicFlareProps> = ({
  color = "#FFE082",
  startFrame = 22,
  duration = 30,
}) => {
  const frame = useCurrentFrame();
  const activeFrame = frame - startFrame;

  if (activeFrame < 0 || activeFrame > duration) {
    return null;
  }

  // Abertura e fechamento suaves do feixe
  const opacity = interpolate(
    activeFrame,
    [0, duration * 0.3, duration * 0.7, duration],
    [0, 0.85, 0.75, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const scaleX = interpolate(activeFrame, [0, duration], [0.1, 1.8], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        opacity,
        mixBlendMode: "screen",
      }}
    >
      {/* Feixe Horizontal Anamórfico Principal */}
      <div
        style={{
          width: "120%",
          height: 3,
          background: `linear-gradient(90deg, transparent 0%, rgba(var(--omni-accent-rgb, 59, 130, 246), 0.2) 20%, ${color} 50%, rgba(var(--omni-accent-rgb, 59, 130, 246), 0.2) 80%, transparent 100%)`,
          transform: `scaleX(${scaleX})`,
          boxShadow: `0 0 25px 4px ${color}, 0 0 60px 8px rgba(var(--omni-accent-rgb, 59, 130, 246), 0.6)`,
        }}
      />

      {/* Brilho Central Circular (Core Glow) */}
      <div
        style={{
          position: "absolute",
          width: 140,
          height: 140,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${color} 0%, rgba(var(--omni-accent-rgb, 59, 130, 246), 0.4) 40%, transparent 75%)`,
          filter: "blur(6px)",
          transform: `scale(${scaleX * 0.8})`,
        }}
      />
    </AbsoluteFill>
  );
};
