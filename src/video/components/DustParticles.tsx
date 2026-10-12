import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

interface Particle {
  x: number; // 0 to 100%
  y: number; // 0 to 100%
  size: number; // pixels
  speedY: number; // drift speed
  speedX: number;
  baseOpacity: number;
  blur: number;
  color: string;
}

export const DustParticles: React.FC<{ count?: number }> = ({ count = 32 }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  // Partículas determinísticas (geradas uma vez via useMemo com seed constante)
  const particles = useMemo<Particle[]>(() => {
    const list: Particle[] = [];
    const colors = ["#D4AF37", "#FFE699", "#C5A059", "#FFFFFF"];

    for (let i = 0; i < count; i++) {
      const pseudoRand = (seed: number) => {
        const x = Math.sin(seed) * 10000;
        return x - Math.floor(x);
      };

      const size = 2 + pseudoRand(i * 13) * 5;
      list.push({
        x: pseudoRand(i * 17 + 1) * 100,
        y: pseudoRand(i * 23 + 2) * 100,
        size,
        speedY: 0.12 + pseudoRand(i * 31 + 3) * 0.25,
        speedX: (pseudoRand(i * 37 + 4) - 0.5) * 0.08,
        baseOpacity: 0.2 + pseudoRand(i * 41 + 5) * 0.6,
        blur: size > 4.5 ? 2.5 : size > 3 ? 1 : 0,
        color: colors[i % colors.length],
      });
    }
    return list;
  }, [count]);

  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      {particles.map((p, i) => {
        // Movimento contínuo determinístico baseado em frame
        const currentY = (p.y - frame * p.speedY) % 105;
        const normalizedY = currentY < -5 ? 105 + currentY : currentY;
        const currentX = p.x + Math.sin(frame * 0.05 + i) * 2;
        const pulse = 0.7 + Math.sin(frame * 0.08 + i * 2) * 0.3;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: `${normalizedY}%`,
              left: `${currentX}%`,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              backgroundColor: p.color,
              opacity: p.baseOpacity * pulse,
              filter: p.blur > 0 ? `blur(${p.blur}px)` : "none",
              boxShadow: `0 0 ${p.size * 2}px ${p.color}`,
              pointerEvents: "none",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
