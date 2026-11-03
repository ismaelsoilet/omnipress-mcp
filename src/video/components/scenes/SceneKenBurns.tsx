import React from "react";
import {
  Interactive,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { KenBurnsImage } from "../KenBurnsImage";
import { resolveMediaSrc } from "../../media";
import type { KenBurnsSceneProps } from "../../types";

export interface SceneKenBurnsProps {
  imageSrc?: string;
  badge?: string;
  direction?: NonNullable<KenBurnsSceneProps["direction"]>;
  headline?: string;
  caption?: string;
}

const sceneKenBurnsSchema = {
  imageSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Imagem de arquivo",
  },
  badge: {
    type: "string",
    default: "",
    description: "Badge",
  },
  headline: {
    type: "string",
    default: "",
    description: "Headline",
  },
  caption: {
    type: "string",
    default: "",
    description: "Legenda da cena",
  },
  direction: {
    type: "enum",
    default: "zoom-in",
    description: "Movimento de câmera",
    variants: {
      "zoom-in": {},
      "zoom-out": {},
      "pan-left": {},
      "pan-right": {},
      "snap-zoom": {},
      "dramatic-push": {},
      "tilt-down": {},
      "subtle-zoom": {},
    },
  },
} as const satisfies InteractivitySchema;

const SceneKenBurnsInner: React.FC<SceneKenBurnsProps> = ({
  imageSrc,
  badge,
  direction = "zoom-in",
  headline,
  caption,
}) => {
  const { durationInFrames } = useVideoConfig();

  return (
    <KenBurnsImage
      imageSrc={resolveMediaSrc(imageSrc)}
      durationInFrames={durationInFrames}
      direction={direction}
      badge={badge}
      headline={headline}
      caption={caption}
    />
  );
};

/**
 * Editable archival scene. The Studio writes timing, image, badge and camera
 * direction back to the generated episode TSX. durationInFrames is read from
 * the enclosing sequence so trimming the clip updates the animation.
 */
export const SceneKenBurns = Interactive.create({
  Component: SceneKenBurnsInner,
  componentName: "SceneKenBurns",
  layout: "absolute-fill",
  schema: sceneKenBurnsSchema,
});
