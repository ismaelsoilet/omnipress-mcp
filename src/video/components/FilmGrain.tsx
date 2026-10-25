import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

/**
 * Textura de ruído estático em SVG base64 (200x200 seamless tile).
 * Calculada uma única vez pelo Chromium e cacheada na memória bitmap,
 * evitando a reavaliação matemática de feTurbulence na CPU em cada frame (ganho massivo de render).
 */
const NOISE_DATA_URI =
  "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjAwIDIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZmlsdGVyIGlkPSJub2lzZUZpbHRlciI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuODUiIG51bU9jdGF2ZXM9IjIiIHN0aXRjaFRpbGVzPSJzdGl0Y2giLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgibm9pc2VGaWx0ZXIpIi8+PC9zdmc+";

export const FilmGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.032 }) => {
  const frame = useCurrentFrame();

  // Deslocamento analógico determinístico que jitteriza a granulação sem recalcular shaders
  const shiftX = ((frame * 37) % 64) - 32;
  const shiftY = ((frame * 59) % 64) - 32;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "overlay",
        opacity,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: -64,
          left: -64,
          right: -64,
          bottom: -64,
          backgroundImage: `url("${NOISE_DATA_URI}")`,
          backgroundRepeat: "repeat",
          transform: `translate(${shiftX}px, ${shiftY}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

