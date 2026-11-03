import React from "react";
import {
  Interactive,
  useVideoConfig,
  type InteractivitySchema,
} from "remotion";
import { ChannelOutro } from "../ChannelOutro";

export interface SceneOutroProps {
  channelName?: string;
  primaryColor?: string;
  tagline?: string;
  avatarSrc?: string;
  bannerSrc?: string;
  title?: string;
  subtitle?: string;
  stampText?: string;
  playlistTitle?: string;
  debateQuestion?: string;
}

const sceneOutroSchema = {
  channelName: {
    type: "string",
    default: "",
    description: "Nome do canal",
  },
  primaryColor: {
    type: "color",
    default: "#3B82F6",
    description: "Cor primária",
  },
  tagline: {
    type: "string",
    default: "",
    description: "Tagline",
  },
  title: {
    type: "string",
    default: "",
    description: "Título",
  },
  subtitle: {
    type: "string",
    default: "",
    description: "Subtítulo",
  },
  stampText: {
    type: "string",
    default: "",
    description: "Selo",
  },
  playlistTitle: {
    type: "string",
    default: "",
    description: "Playlist",
  },
  debateQuestion: {
    type: "string",
    default: "",
    description: "Pergunta de debate",
  },
  avatarSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Avatar",
  },
  bannerSrc: {
    type: "asset",
    assetType: "image",
    default: "",
    description: "Banner",
  },
} as const satisfies InteractivitySchema;

const SceneOutroInner: React.FC<SceneOutroProps> = ({
  channelName,
  primaryColor,
  tagline,
  avatarSrc,
  bannerSrc,
  title,
  subtitle,
  stampText,
  playlistTitle,
  debateQuestion,
}) => {
  const { durationInFrames } = useVideoConfig();

  return (
    <ChannelOutro
      durationInFrames={durationInFrames}
      channelName={channelName}
      primaryColor={primaryColor}
      tagline={tagline}
      avatarSrc={avatarSrc}
      bannerSrc={bannerSrc}
      title={title}
      subtitle={subtitle}
      stampText={stampText}
      playlistTitle={playlistTitle}
      debateQuestion={debateQuestion}
    />
  );
};

/**
 * Editable channel outro. Keeps the YouTube end-screen zones intact while
 * allowing the copy, colors and images to be edited in the Studio.
 */
export const SceneOutro = Interactive.create({
  Component: SceneOutroInner,
  componentName: "SceneOutro",
  layout: "absolute-fill",
  schema: sceneOutroSchema,
});
