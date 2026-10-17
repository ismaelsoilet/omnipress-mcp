import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface OverlayEvent {
  startSec: number;
  durationSec: number;
  type: "stamp-mito" | "stamp-realidade" | "question-card" | "flash-cut";
  text?: string;
  subtext?: string;
  top?: number;
}

export interface MitoRealidadeOverlaysProps {
  events: OverlayEvent[];
}

/**
 * MitoRealidadeOverlays — Camada de Choque Visual e Retenção Psicológica
 * Controla carimbos táteis (MITO vs REALIDADE), caixas de perguntas reflexivas
 * e micro-flashes de transição para reter a atenção nos primeiros segundos.
 */
export const MitoRealidadeOverlays: React.FC<MitoRealidadeOverlaysProps> = ({ events }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTimeSec = frame / fps;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 80,
      }}
    >
      {events.map((evt, idx) => {
        const startFrame = Math.round(evt.startSec * fps);
        const endFrame = Math.round((evt.startSec + evt.durationSec) * fps);

        if (frame < startFrame || frame > endFrame) {
          return null;
        }

        const localFrame = frame - startFrame;

        // 1. FLASH DE TRANSIÇÃO (2 a 4 frames)
        if (evt.type === "flash-cut") {
          const flashOpacity = interpolate(localFrame, [0, 1, 4], [0.55, 0.35, 0], {
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                backgroundColor: "#FFFFFF",
                opacity: flashOpacity,
                mixBlendMode: "overlay",
              }}
            />
          );
        }

        // 2. CARIMBO "MITO HISTÓRICO" (Vermelho Neon com batida violenta)
        if (evt.type === "stamp-mito") {
          const slam = spring({
            frame: localFrame,
            fps,
            config: { damping: 9, mass: 0.4, stiffness: 210 },
          });

          const scale = interpolate(slam, [0, 1], [3.2, 1.0]);
          const opacity = interpolate(slam, [0, 0.3, 1], [0, 0.95, 1.0]);

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                top: evt.top ?? 260,
                left: "50%",
                transform: `translateX(-50%) rotate(-12deg) scale(${scale})`,
                opacity,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                backgroundColor: "rgba(18, 4, 8, 0.92)",
                border: "6px solid #FF2A55",
                borderRadius: 16,
                padding: "20px 48px",
                boxShadow: "0 0 50px rgba(255, 42, 85, 0.65), inset 0 0 30px rgba(255, 42, 85, 0.4)",
                backdropFilter: "blur(14px)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                <span
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    backgroundColor: "#FF2A55",
                    boxShadow: "0 0 20px #FF2A55",
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "'Impact', 'Arial Black', sans-serif",
                    fontSize: 78,
                    fontWeight: 900,
                    color: "#FF2A55",
                    letterSpacing: 6,
                    textTransform: "uppercase",
                    textShadow: "0 4px 20px rgba(0, 0, 0, 0.95), 0 0 30px rgba(255, 42, 85, 0.8)",
                    lineHeight: 1,
                  }}
                >
                  {evt.text || "MITO!"}
                </span>
              </div>
              {evt.subtext && (
                <span
                  style={{
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: 22,
                    fontWeight: 800,
                    color: "#FFFFFF",
                    letterSpacing: 3,
                    textTransform: "uppercase",
                    marginTop: 8,
                  }}
                >
                  {evt.subtext}
                </span>
              )}
            </div>
          );
        }

        // 3. CARIMBO "REALIDADE HISTÓRICA" (Verde Dourado Imperial)
        if (evt.type === "stamp-realidade") {
          const slam = spring({
            frame: localFrame,
            fps,
            config: { damping: 9, mass: 0.4, stiffness: 210 },
          });

          const scale = interpolate(slam, [0, 1], [3.2, 1.0]);
          const opacity = interpolate(slam, [0, 0.3, 1], [0, 0.95, 1.0]);

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                top: evt.top ?? 260,
                left: "50%",
                transform: `translateX(-50%) rotate(8deg) scale(${scale})`,
                opacity,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                backgroundColor: "rgba(4, 18, 10, 0.92)",
                border: "6px solid #00FF88",
                borderRadius: 16,
                padding: "20px 48px",
                boxShadow: "0 0 50px rgba(0, 255, 136, 0.65), inset 0 0 30px rgba(0, 255, 136, 0.4)",
                backdropFilter: "blur(14px)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                <span
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    backgroundColor: "#00FF88",
                    boxShadow: "0 0 20px #00FF88",
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "'Impact', 'Arial Black', sans-serif",
                    fontSize: 74,
                    fontWeight: 900,
                    color: "#00FF88",
                    letterSpacing: 6,
                    textTransform: "uppercase",
                    textShadow: "0 4px 20px rgba(0, 0, 0, 0.95), 0 0 30px rgba(0, 255, 136, 0.8)",
                    lineHeight: 1,
                  }}
                >
                  {evt.text || "REALIDADE"}
                </span>
              </div>
              {evt.subtext && (
                <span
                  style={{
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: 22,
                    fontWeight: 800,
                    color: "#D4AF37",
                    letterSpacing: 3,
                    textTransform: "uppercase",
                    marginTop: 8,
                  }}
                >
                  {evt.subtext}
                </span>
              )}
            </div>
          );
        }

        // 4. CARTÃO DE PERGUNTA TÁTICA (Provocação no Topo)
        if (evt.type === "question-card") {
          const slide = spring({
            frame: localFrame,
            fps,
            config: { damping: 12, mass: 0.5, stiffness: 180 },
          });

          const translateY = interpolate(slide, [0, 1], [-80, 0]);
          const opacity = interpolate(slide, [0, 0.4, 1], [0, 0.9, 1.0]);

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                top: evt.top ?? 170,
                left: 40,
                right: 40,
                transform: `translateY(${translateY}px)`,
                opacity,
                backgroundColor: "rgba(8, 10, 16, 0.94)",
                border: "2px solid #FFE500",
                borderRadius: 18,
                padding: "16px 24px",
                backdropFilter: "blur(16px)",
                boxShadow: "0 10px 40px rgba(0, 0, 0, 0.85), 0 0 25px rgba(255, 229, 0, 0.25)",
                display: "flex",
                flexDirection: "column",
                gap: 6,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                  color: "#FFE500",
                  fontFamily: "'Courier New', Courier, monospace",
                  fontSize: 18,
                  fontWeight: 900,
                  letterSpacing: 3,
                  textTransform: "uppercase",
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: 22,
                    height: 22,
                    borderRadius: 4,
                    backgroundColor: "#FFE500",
                    color: "#000000",
                    fontSize: 14,
                    fontWeight: 900,
                  }}
                >
                  ?
                </span>
                ENIGMA DO ARQUIVO
              </div>
              <div
                style={{
                  color: "#FFFFFF",
                  fontFamily: "'Segoe UI', Roboto, sans-serif",
                  fontSize: 28,
                  fontWeight: 800,
                  lineHeight: 1.25,
                }}
              >
                {evt.text}
              </div>
            </div>
          );
        }

        return null;
      })}
    </div>
  );
};
