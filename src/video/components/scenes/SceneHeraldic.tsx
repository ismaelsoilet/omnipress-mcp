import React from "react";
import {
  Interactive,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { HeraldicSurgery } from "../HeraldicSurgery";

export interface SceneHeraldicProps {
  beforeSrc?: string;
  afterSrc?: string;
  badge?: string;
}

const sceneHeraldicSchema = {
  beforeSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Imagem antes",
  },
  afterSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Imagem depois",
  },
  badge: {
    type: "string",
    default: "METAMORFOSE VISUAL",
    description: "Badge",
  },
} as const satisfies InteractivitySchema;

const SceneHeraldicInner: React.FC<SceneHeraldicProps> = ({
  beforeSrc,
  afterSrc,
  badge = "METAMORFOSE VISUAL",
}) => {
  const { durationInFrames } = useVideoConfig();

  return (
    <HeraldicSurgery
      durationInFrames={durationInFrames}
      beforeSrc={beforeSrc}
      afterSrc={afterSrc}
      badge={badge}
    />
  );
};

/**
 * Editable visual-metamorphosis scene (heraldic surgery / image morph).
 */
export const SceneHeraldic = Interactive.create({
  Component: SceneHeraldicInner,
  componentName: "SceneHeraldic",
  layout: "absolute-fill",
  schema: sceneHeraldicSchema,
});
