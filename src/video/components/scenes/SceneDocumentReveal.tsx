import React from "react";
import {
  AbsoluteFill,
  Interactive,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { ClassifiedStamp } from "../ClassifiedStamp";
import { FilmGrain } from "../FilmGrain";
import { ScrambledText } from "../ScrambledText";
import { TacticalGrid } from "../TacticalGrid";

export interface SceneDocumentRevealProps {
  headline?: string;
  subheadline?: string;
  badge?: string;
  accentColor?: string;
  dangerColor?: string;
}

const sceneDocumentRevealSchema = {
  headline: {
    type: "string",
    default: "",
    description: "Headline",
  },
  subheadline: {
    type: "string",
    default: "",
    description: "Subheadline",
  },
  badge: {
    type: "string",
    default: "",
    description: "Badge",
  },
  accentColor: {
    type: "color",
    default: "#3B82F6",
    description: "Cor de destaque",
  },
  dangerColor: {
    type: "color",
    default: "#EF4444",
    description: "Cor de alerta",
  },
} as const satisfies InteractivitySchema;

const SceneDocumentRevealInner: React.FC<SceneDocumentRevealProps> = ({
  headline,
  subheadline,
  badge,
  accentColor = "#3B82F6",
  dangerColor = "#EF4444",
}) => {
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#080A0E",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 40,
      }}
    >
      <TacticalGrid />
      <FilmGrain opacity={0.08} />

      <div
        style={{
          textAlign: "center",
          maxWidth: isVertical ? 900 : 1200,
          zIndex: 10,
        }}
      >
        <Interactive.Div
          name="Document badge"
          style={{
            display: "inline-block",
            marginBottom: 20,
            color: accentColor,
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 16 : 20,
            letterSpacing: 4,
            fontWeight: 800,
          }}
        >
          {badge || ""}
        </Interactive.Div>

        <Interactive.H1
          name="Document headline"
          style={{
            color: "#F5F6F8",
            fontFamily: "'Cinzel', Georgia, serif",
            fontSize: isVertical ? 38 : 52,
            fontWeight: 900,
            letterSpacing: 3,
            margin: "0 0 24px 0",
            lineHeight: 1.25,
            textTransform: "uppercase",
          }}
        >
          <ScrambledText text={headline || ""} durationInFrames={35} />
        </Interactive.H1>

        {subheadline ? (
          <Interactive.P
            name="Document subheadline"
            style={{
              color: "#9EA8B6",
              fontFamily: "system-ui, sans-serif",
              fontSize: isVertical ? 20 : 24,
              letterSpacing: 1,
              margin: 0,
            }}
          >
            {subheadline}
          </Interactive.P>
        ) : null}

        <div style={{ marginTop: 35 }}>
          <ClassifiedStamp
            text={badge || ""}
            startFrame={15}
            color={dangerColor}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * Editable document-reveal scene. Keeps the Rule 08 protective backdrop and
 * allows text, badge and accent colors to be edited from the Studio.
 */
export const SceneDocumentReveal = Interactive.create({
  Component: SceneDocumentRevealInner,
  componentName: "SceneDocumentReveal",
  layout: "absolute-fill",
  schema: sceneDocumentRevealSchema,
});
