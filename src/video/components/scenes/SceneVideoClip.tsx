import React from "react";
import {
  AbsoluteFill,
  Interactive,
  OffthreadVideo,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { FilmGrain } from "../FilmGrain";
import { resolveMediaSrc } from "../../media";

export interface SceneVideoClipProps {
  videoSrc?: string;
  headline?: string;
  badge?: string;
  overlayText?: string;
  muted?: boolean;
}

const sceneVideoClipSchema = {
  videoSrc: {
    type: "asset",
    assetType: "video",
    default: "",
    description: "Clipe de vídeo",
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
  overlayText: {
    type: "string",
    default: "",
    description: "Texto de apoio",
  },
  muted: {
    type: "boolean",
    default: true,
    description: "Silenciar clipe",
  },
} as const satisfies InteractivitySchema;

const SceneVideoClipInner: React.FC<SceneVideoClipProps> = ({
  videoSrc,
  headline,
  badge,
  overlayText,
  muted = true,
}) => {
  const { width, height } = useVideoConfig();
  const isVertical = height > width;

  return (
    <AbsoluteFill style={{ backgroundColor: "#04060A", overflow: "hidden" }}>
      {videoSrc ? (
        <OffthreadVideo
          src={resolveMediaSrc(videoSrc)}
          muted={muted}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      ) : null}

      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(4,6,10,0.05) 0%, rgba(4,6,10,0.18) 55%, rgba(4,6,10,0.94) 100%)",
        }}
      />
      <FilmGrain opacity={0.06} />

      <Interactive.Div
        name="Video clip text card"
        style={{
          position: "absolute",
          left: isVertical ? 42 : 84,
          right: isVertical ? 42 : "auto",
          bottom: isVertical ? 140 : 80,
          maxWidth: isVertical ? 900 : 900,
          padding: isVertical ? "22px 26px" : "26px 34px",
          borderRadius: 14,
          backgroundColor: "rgba(8, 10, 14, 0.82)",
          border: "1.5px solid rgba(var(--omni-accent-rgb, 59, 130, 246), 0.55)",
          boxShadow: "0 18px 50px rgba(0,0,0,0.8)",
        }}
      >
        <Interactive.Div
          name="Video clip badge"
          style={{
            color: "var(--omni-accent, #3B82F6)",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 16 : 18,
            fontWeight: 800,
            letterSpacing: 3,
            marginBottom: 12,
          }}
        >
          {badge || "CLIPE // ARQUIVO"}
        </Interactive.Div>
        <Interactive.Div
          name="Video clip headline"
          style={{
            color: "#FFFFFF",
            fontFamily: "'Cinzel', Georgia, serif",
            fontSize: isVertical ? 34 : 44,
            fontWeight: 900,
            lineHeight: 1.2,
            marginBottom: overlayText ? 12 : 0,
          }}
        >
          {headline || ""}
        </Interactive.Div>
        {overlayText ? (
          <Interactive.Div
            name="Video clip overlay text"
            style={{
              color: "#CBD5E1",
              fontFamily: "system-ui, sans-serif",
              fontSize: isVertical ? 18 : 22,
              lineHeight: 1.35,
            }}
          >
            {overlayText}
          </Interactive.Div>
        ) : null}
      </Interactive.Div>
    </AbsoluteFill>
  );
};

/** Editable archival video clip scene. */
export const SceneVideoClip = Interactive.create({
  Component: SceneVideoClipInner,
  componentName: "SceneVideoClip",
  layout: "absolute-fill",
  schema: sceneVideoClipSchema,
});
