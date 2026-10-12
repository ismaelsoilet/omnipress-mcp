import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

export const FilmGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.08 }) => {
  const frame = useCurrentFrame();
  const seed = (frame % 10) * 13;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "overlay",
        opacity,
      }}
    >
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <filter id="grainFilter">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.80"
            numOctaves="3"
            stitchTiles="stitch"
            seed={seed}
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grainFilter)" fill="#FFFFFF" />
      </svg>
    </AbsoluteFill>
  );
};
