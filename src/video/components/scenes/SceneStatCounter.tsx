import React from "react";
import {
  AbsoluteFill,
  Img,
  Interactive,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { FilmGrain } from "../FilmGrain";
import { resolveMediaSrc } from "../../media";

export interface SceneStatCounterProps {
  value?: number;
  prefix?: string;
  suffix?: string;
  label?: string;
  headline?: string;
  accentColor?: string;
  backgroundSrc?: string;
}

const sceneStatCounterSchema = {
  value: {
    type: "number",
    min: 0,
    step: 1,
    default: 0,
    description: "Valor final",
    hiddenFromList: false,
  },
  prefix: {
    type: "string",
    default: "",
    description: "Prefixo",
  },
  suffix: {
    type: "string",
    default: "",
    description: "Sufixo",
  },
  label: {
    type: "string",
    default: "",
    description: "Rótulo do número",
  },
  headline: {
    type: "string",
    default: "",
    description: "Headline",
  },
  accentColor: {
    type: "color",
    default: "#FACC15",
    description: "Cor do número",
  },
  backgroundSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Imagem de fundo",
  },
} as const satisfies InteractivitySchema;

const SceneStatCounterInner: React.FC<SceneStatCounterProps> = ({
  value = 0,
  prefix = "",
  suffix = "",
  label = "",
  headline = "",
  accentColor = "#FACC15",
  backgroundSrc = "",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const isVertical = height > width;
  const numericValue = Number.isFinite(value) ? Math.max(0, value) : 0;

  const progress = spring({
    frame,
    fps,
    durationInFrames: Math.min(45, Math.max(1, durationInFrames)),
    config: { damping: 18, mass: 0.8, stiffness: 80 },
  });
  const current = Math.round(
    interpolate(progress, [0, 1], [0, numericValue], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const formatted = new Intl.NumberFormat("pt-BR").format(current);

  return (
    <AbsoluteFill style={{ backgroundColor: "#04060A", overflow: "hidden" }}>
      {backgroundSrc ? (
        <AbsoluteFill style={{ overflow: "hidden" }}>
          <Img
            src={resolveMediaSrc(backgroundSrc)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              opacity: 0.28,
              filter: "grayscale(0.4) brightness(0.7)",
            }}
          />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 45%, rgba(15,23,42,0.15) 0%, rgba(4,6,10,0.86) 68%, #04060A 100%)",
        }}
      />
      <FilmGrain opacity={0.08} />

      <Interactive.Div
        name="Stat counter card"
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: isVertical ? "88%" : "72%",
          padding: isVertical ? "32px 26px" : "40px 54px",
          borderRadius: 18,
          backgroundColor: "rgba(8, 10, 14, 0.88)",
          border: `1.5px solid ${accentColor}`,
          boxShadow: "0 24px 70px rgba(0,0,0,0.9)",
          textAlign: "center",
        }}
      >
        <Interactive.Div
          name="Stat counter value"
          style={{
            color: accentColor,
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 92 : 132,
            fontWeight: 900,
            lineHeight: 0.95,
            letterSpacing: -2,
            textShadow: "0 8px 30px rgba(0,0,0,0.9)",
          }}
        >
          {`${prefix}${formatted}${suffix}`}
        </Interactive.Div>
        {label ? (
          <Interactive.Div
            name="Stat counter label"
            style={{
              marginTop: 14,
              color: "#E2E8F0",
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: isVertical ? 20 : 24,
              fontWeight: 700,
              letterSpacing: 3,
              textTransform: "uppercase",
            }}
          >
            {label}
          </Interactive.Div>
        ) : null}
        {headline ? (
          <Interactive.Div
            name="Stat counter headline"
            style={{
              marginTop: 20,
              color: "#9EA8B6",
              fontFamily: "'Cinzel', Georgia, serif",
              fontSize: isVertical ? 26 : 32,
              fontWeight: 700,
              lineHeight: 1.25,
            }}
          >
            {headline}
          </Interactive.Div>
        ) : null}
      </Interactive.Div>
    </AbsoluteFill>
  );
};

/** Editable animated statistic counter scene. */
export const SceneStatCounter = Interactive.create({
  Component: SceneStatCounterInner,
  componentName: "SceneStatCounter",
  layout: "absolute-fill",
  schema: sceneStatCounterSchema,
});
