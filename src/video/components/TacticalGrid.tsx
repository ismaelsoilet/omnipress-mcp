import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export interface TacticalGridProps {
  color?: string;
  code?: string;
  dateStr?: string;
  opacity?: number;
}

export const TacticalGrid: React.FC<TacticalGridProps> = ({
  color = "#D4AF37",
  code = "DOC-REF // 1963-TUR",
  dateStr = "CLASSIFIED ARCHIVE",
  opacity = 0.25,
}) => {
  const frame = useCurrentFrame();
  const scanlineY = interpolate(frame % 90, [0, 90], [0, 100]);

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        fontFamily: "'Courier New', Courier, monospace",
        color,
        opacity,
      }}
    >
      {/* 4 Corner Crosshairs */}
      <div style={{ position: "absolute", top: 40, left: 40, fontSize: 18 }}>+</div>
      <div style={{ position: "absolute", top: 40, right: 40, fontSize: 18 }}>+</div>
      <div style={{ position: "absolute", bottom: 40, left: 40, fontSize: 18 }}>+</div>
      <div style={{ position: "absolute", bottom: 40, right: 40, fontSize: 18 }}>+</div>

      {/* Top and Bottom Technical Metadata */}
      <div
        style={{
          position: "absolute",
          top: 45,
          left: 70,
          fontSize: 13,
          letterSpacing: 2,
          fontWeight: 700,
        }}
      >
        {code}
      </div>
      <div
        style={{
          position: "absolute",
          top: 45,
          right: 70,
          fontSize: 13,
          letterSpacing: 2,
          fontWeight: 700,
        }}
      >
        {dateStr}
      </div>

      {/* Subtle Scanline */}
      <div
        style={{
          position: "absolute",
          top: `${scanlineY}%`,
          left: 0,
          right: 0,
          height: "2px",
          backgroundColor: color,
          opacity: 0.15,
          boxShadow: `0 0 8px ${color}`,
        }}
      />
    </AbsoluteFill>
  );
};
