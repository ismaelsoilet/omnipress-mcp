import React from "react";
import {
  AbsoluteFill,
  Img,
  Interactive,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { FilmGrain } from "../FilmGrain";
import { TacticalGrid } from "../TacticalGrid";
import { resolveMediaSrc } from "../../media";

export interface SceneTacticalMapProps {
  imageSrc?: string;
  headline?: string;
  badge?: string;
  coordinates?: string;
  accentColor?: string;
}

const sceneTacticalMapSchema = {
  imageSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Mapa ou imagem de arquivo",
  },
  headline: {
    type: "string",
    default: "",
    description: "Headline",
  },
  badge: {
    type: "string",
    default: "",
    description: "Badge",
  },
  coordinates: {
    type: "string",
    default: "",
    description: "Coordenadas / referência",
  },
  accentColor: {
    type: "color",
    default: "#3B82F6",
    description: "Cor tática",
  },
} as const satisfies InteractivitySchema;

const SceneTacticalMapInner: React.FC<SceneTacticalMapProps> = ({
  imageSrc,
  headline,
  badge,
  coordinates,
  accentColor = "#3B82F6",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const isVertical = height > width;
  const scale = interpolate(
    frame,
    [0, Math.max(1, durationInFrames)],
    [1.02, 1.08],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#04060A", overflow: "hidden" }}>
      {imageSrc ? (
        <AbsoluteFill style={{ overflow: "hidden" }}>
          <Img
            src={resolveMediaSrc(imageSrc)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              opacity: 0.62,
              scale,
            }}
          />
        </AbsoluteFill>
      ) : null}

      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(4,6,10,0.96) 0%, rgba(4,6,10,0.62) 48%, rgba(4,6,10,0.18) 100%)",
        }}
      />
      <TacticalGrid
        color={accentColor}
        code={coordinates || "GRID // ARCHIVE"}
        dateStr="TACTICAL // SCAN"
        opacity={0.34}
      />
      <FilmGrain opacity={0.07} />

      <Interactive.Div
        name="Tactical map text card"
        style={{
          position: "absolute",
          left: isVertical ? 48 : 96,
          bottom: isVertical ? 150 : 96,
          maxWidth: isVertical ? 860 : 780,
          padding: isVertical ? "24px 28px" : "28px 34px",
          borderRadius: 14,
          backgroundColor: "rgba(8, 10, 14, 0.88)",
          border: `1.5px solid ${accentColor}`,
          boxShadow: "0 18px 50px rgba(0,0,0,0.85)",
        }}
      >
        <Interactive.Div
          name="Tactical map badge"
          style={{
            color: accentColor,
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 18 : 20,
            fontWeight: 800,
            letterSpacing: 3,
            marginBottom: 14,
          }}
        >
          {badge || "MAPA TÁTICO"}
        </Interactive.Div>
        <Interactive.Div
          name="Tactical map headline"
          style={{
            color: "#F5F6F8",
            fontFamily: "'Cinzel', Georgia, serif",
            fontSize: isVertical ? 34 : 46,
            fontWeight: 900,
            lineHeight: 1.2,
            letterSpacing: 1,
            marginBottom: coordinates ? 14 : 0,
          }}
        >
          {headline || ""}
        </Interactive.Div>
        {coordinates ? (
          <Interactive.Div
            name="Tactical map coordinates"
            style={{
              color: "#9EA8B6",
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: isVertical ? 16 : 18,
              letterSpacing: 2,
            }}
          >
            {coordinates}
          </Interactive.Div>
        ) : null}
      </Interactive.Div>
    </AbsoluteFill>
  );
};

/** Editable archival/tactical map scene. */
export const SceneTacticalMap = Interactive.create({
  Component: SceneTacticalMapInner,
  componentName: "SceneTacticalMap",
  layout: "absolute-fill",
  schema: sceneTacticalMapSchema,
});
