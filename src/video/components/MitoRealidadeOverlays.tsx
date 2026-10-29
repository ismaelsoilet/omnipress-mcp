import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface OverlayEvent {
  startSec: number;
  durationSec: number;
  type:
    | "stamp-mito"
    | "stamp-realidade"
    | "stamp-alert"
    | "stamp-negative"
    | "stamp-success"
    | "stamp-positive"
    | "question-card"
    | "flash-cut";
  text?: string;
  subtext?: string;
  label?: string;
  top?: number;
  color?: string;
  borderColor?: string;
  subtextColor?: string;
}

export interface MitoRealidadeOverlaysProps {
  events: OverlayEvent[];
}

/**
 * MitoRealidadeOverlays (ImpactOverlays) — Camada Universal de Choque Visual e Retenção Psicológica
 * Controla carimbos táteis de alto impacto (Negativo/Alerta vs Positivo/Sucesso),
 * caixas de perguntas táticas e micro-flashes de transição para retenção nos primeiros segundos.
 */
export const MitoRealidadeOverlays: React.FC<MitoRealidadeOverlaysProps> = ({ events }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

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

        // 2. CARIMBO DE IMPACTO NEGATIVO / ALERTA (Vermelho Neon com batida violenta)
        if (
          evt.type === "stamp-mito" ||
          evt.type === "stamp-alert" ||
          evt.type === "stamp-negative"
        ) {
          const slam = spring({
            frame: localFrame,
            fps,
            config: { damping: 9, mass: 0.4, stiffness: 210 },
          });

          const scale = interpolate(slam, [0, 1], [3.2, 1.0]);
          const opacity = interpolate(slam, [0, 0.3, 1], [0, 0.95, 1.0]);
          const themeColor = evt.color || "#FF2A55";
          const borderColor = evt.borderColor || themeColor;
          const defaultLabel = evt.type === "stamp-alert" ? "ALERTA!" : "MITO!";

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
                border: `6px solid ${borderColor}`,
                borderRadius: 16,
                padding: "20px 48px",
                boxShadow: `0 0 50px ${themeColor}A6, inset 0 0 30px ${themeColor}66`,
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
                    backgroundColor: themeColor,
                    boxShadow: `0 0 20px ${themeColor}`,
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "'Impact', 'Arial Black', sans-serif",
                    fontSize: 78,
                    fontWeight: 900,
                    color: themeColor,
                    letterSpacing: 6,
                    textTransform: "uppercase",
                    textShadow: `0 4px 20px rgba(0, 0, 0, 0.95), 0 0 30px ${themeColor}CC`,
                    lineHeight: 1,
                  }}
                >
                  {evt.text || defaultLabel}
                </span>
              </div>
              {evt.subtext && (
                <span
                  style={{
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: 22,
                    fontWeight: 800,
                    color: evt.subtextColor || "#FFFFFF",
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

        // 3. CARIMBO DE IMPACTO POSITIVO / SUCESSO (Verde Dourado / Neon)
        if (
          evt.type === "stamp-realidade" ||
          evt.type === "stamp-success" ||
          evt.type === "stamp-positive"
        ) {
          const slam = spring({
            frame: localFrame,
            fps,
            config: { damping: 9, mass: 0.4, stiffness: 210 },
          });

          const scale = interpolate(slam, [0, 1], [3.2, 1.0]);
          const opacity = interpolate(slam, [0, 0.3, 1], [0, 0.95, 1.0]);
          const themeColor = evt.color || "#00FF88";
          const borderColor = evt.borderColor || themeColor;
          const defaultLabel =
            evt.type === "stamp-success"
              ? "SUCESSO!"
              : evt.type === "stamp-positive"
              ? "FATO!"
              : "REALIDADE";

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
                border: `6px solid ${borderColor}`,
                borderRadius: 16,
                padding: "20px 48px",
                boxShadow: `0 0 50px ${themeColor}A6, inset 0 0 30px ${themeColor}66`,
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
                    backgroundColor: themeColor,
                    boxShadow: `0 0 20px ${themeColor}`,
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "'Impact', 'Arial Black', sans-serif",
                    fontSize: 74,
                    fontWeight: 900,
                    color: themeColor,
                    letterSpacing: 6,
                    textTransform: "uppercase",
                    textShadow: `0 4px 20px rgba(0, 0, 0, 0.95), 0 0 30px ${themeColor}CC`,
                    lineHeight: 1,
                  }}
                >
                  {evt.text || defaultLabel}
                </span>
              </div>
              {evt.subtext && (
                <span
                  style={{
                    fontFamily: "'Courier New', Courier, monospace",
                    fontSize: 22,
                    fontWeight: 800,
                    color: evt.subtextColor || "var(--omni-accent, #3B82F6)",
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
                {evt.label || ""}
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
