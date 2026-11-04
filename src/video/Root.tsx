import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import {
  DocumentaryEpisode,
  DocumentaryEpisodeProps,
} from "./compositions/DocumentaryEpisode";
import { DocumentaryScene } from "./types";
import { DocumentaryShort } from "./compositions/DocumentaryShort";
import { ThumbnailEpisode } from "./compositions/ThumbnailEpisode";
import {
  SceneDocumentReveal,
  SceneHeraldic,
  SceneKenBurns,
  SceneOutro,
  SceneStatCounter,
  SceneTacticalMap,
  SceneVideoClip,
} from "./components/scenes";
import { sampleShortCaptions, sampleEpisodeCaptions } from "./fixtures/sampleCaptions";

/**
 * Universal Remotion compositions for OmniPress MCP.
 *
 * Keep defaultProps inline on each <Composition> so the Remotion Studio props
 * editor can write visual edits back to this file. Channel-specific content and
 * generated editable episodes live in channels/<slug>/video/.
 */
export const CoreCompositions: React.FC = () => {
  return (
    <>
      {/* 1. Vinheta 16:9 — Português (YouTube Principal) */}
      <Composition
        id="ChannelIntro-16x9"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "pt",
          channelName: "CHANNEL NAME",
          badgeText: "FEATURED // OFFICIAL",
          subText: "STORIES & INVESTIGATIONS",
          classifiedCode: "REF // DEMO-PT",
          primaryColor: "#3B82F6",
          backgroundColor: "#0B1220",
        }}
      />

      {/* 2. Vinheta 9:16 — Português (YouTube Shorts / Reels / TikTok) */}
      <Composition
        id="ChannelIntro-9x16"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "pt",
          channelName: "CHANNEL NAME",
          badgeText: "FEATURED // VERTICAL",
          subText: "REAL STORIES • OFFICIAL CONTENT",
          classifiedCode: "REF // DEMO-SHORTS",
          primaryColor: "#3B82F6",
          backgroundColor: "#0B1220",
        }}
      />

      {/* 3. Vinheta 16:9 — Inglês (Canal Internacional) */}
      <Composition
        id="ChannelIntro-16x9-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "en",
          channelName: "CHANNEL NAME",
          badgeText: "OFFICIAL RELEASE // LVL 1",
          subText: "EXPLORING THE UNKNOWN",
          classifiedCode: "REF // DEMO-EN",
          primaryColor: "#3B82F6",
          backgroundColor: "#0B1220",
        }}
      />

      {/* 4. Vinheta 9:16 — Inglês (Shorts Internacional) */}
      <Composition
        id="ChannelIntro-9x16-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "en",
          channelName: "CHANNEL NAME",
          badgeText: "FEATURED STORY",
          subText: "REAL STORIES • GLOBAL ARCHIVES",
          classifiedCode: "REF // DEMO-SHORTS-EN",
          primaryColor: "#3B82F6",
          backgroundColor: "#0B1220",
        }}
      />

      {/* 5. Episódio Documental Universal 16:9 (YouTube Widescreen) */}
      <Composition<any, DocumentaryEpisodeProps>
        id="DocumentaryEpisode-16x9"
        component={DocumentaryEpisode}
        durationInFrames={25083}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={({ props }) => {
          const introFrames = props.enableIntro
            ? props.introDurationFrames ?? 120
            : 0;
          const scenesFrames = (props.config?.scenes || []).reduce(
            (acc: number, scene: DocumentaryScene) =>
              acc + Math.round((scene.durationInSeconds || 0) * 30),
            0
          );
          const totalFrames =
            scenesFrames > 0
              ? introFrames + scenesFrames
              : props.config?.voiceovers?.[0]
                ? Math.round(
                    (props.config.voiceovers[0].durationInSeconds || 0) * 30
                  ) + introFrames
                : 25083;
          return {
            durationInFrames: totalFrames,
            props,
          };
        }}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120,
          config: {
            id: "ep-sample-16x9",
            title: "Documentary Episode Title",
            channelSlug: "template-channel",
            language: "pt",
            introProps: {
              channelName: "CHANNEL NAME",
              primaryColor: "#3B82F6",
            },
            scenes: [],
            captions: sampleEpisodeCaptions,
          },
        }}
      />

      {/* 6. Episódio Documental Universal 9:16 (Shorts / Reels / TikTok) */}
      <Composition
        id="DocumentaryEpisode-9x16"
        component={DocumentaryEpisode}
        durationInFrames={1950}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120,
          config: {
            id: "ep-sample-9x16",
            title: "Vertical Short Title",
            channelSlug: "template-channel",
            language: "pt",
            introProps: {
              channelName: "CHANNEL NAME",
              primaryColor: "#3B82F6",
            },
            scenes: [],
            captions: sampleEpisodeCaptions,
          },
        }}
      />

      {/* 7. Short Universal 9:16 (65s Padrão Monetização Vertical) */}
      <Composition
        id="DocumentaryShort-9x16"
        component={DocumentaryShort}
        durationInFrames={1950}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Vertical Short Title",
          badge: "FEATURED // SHORTS",
          captionsData: sampleShortCaptions,
          actTimelines: [
            {
              id: "short_01",
              globalStart: 0,
              globalEnd: 65.0,
            },
          ],
          scenes: [],
        }}
      />

      {/* 8. Thumbnail Oficial YouTube 16:9 — Alto Impacto */}
      <Composition
        id="Thumbnail-16x9"
        component={ThumbnailEpisode}
        durationInFrames={30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          titleLine1: "MAIN HEADLINE",
          titleLine2: "SECOND LINE",
          tagText: "CATEGORY // INVESTIGATION",
          calloutText: "IMPACT CALLOUT!",
          depthTag: "TAG 1",
          peopleTag: "TAG 2",
          doorTag: "TAG 3",
          showClassifiedStamp: false,
        }}
      />
      {/* 9. Connected scene previews for interactive template design */}
      <Composition
        id="SceneKenBurns-Preview"
        component={SceneKenBurns}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          imageSrc: "https://remotion.media/image.jpeg",
          badge: "PREVIEW // KEN BURNS",
          direction: "zoom-in",
        }}
      />

      <Composition
        id="SceneDocumentReveal-Preview"
        component={SceneDocumentReveal}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          headline: "DOCUMENT HEADLINE",
          subheadline: "Supporting archival line",
          badge: "CONFIDENCIAL",
          accentColor: "#3B82F6",
          dangerColor: "#EF4444",
        }}
      />

      <Composition
        id="SceneHeraldic-Preview"
        component={SceneHeraldic}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          beforeSrc: "https://remotion.media/image.jpeg",
          afterSrc: "https://remotion.media/image.jpeg",
          badge: "METAMORFOSE VISUAL",
        }}
      />

      <Composition
        id="SceneOutro-Preview"
        component={SceneOutro}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          channelName: "CHANNEL NAME",
          primaryColor: "#3B82F6",
          tagline: "STORIES & INVESTIGATIONS",
        }}
      />

      <Composition
        id="SceneTacticalMap-Preview"
        component={SceneTacticalMap}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          imageSrc: "https://remotion.media/image.jpeg",
          headline: "THE ROUTE OF THE ARCHIVE",
          badge: "MAPA TÁTICO",
          coordinates: "23°33′S 46°38′W",
          accentColor: "#3B82F6",
        }}
      />

      <Composition
        id="SceneStatCounter-Preview"
        component={SceneStatCounter}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          value: 1889,
          prefix: "",
          suffix: "",
          label: "Documentos analisados",
          headline: "O número que mudou a investigação",
          accentColor: "#FACC15",
        }}
      />

      <Composition
        id="SceneVideoClip-Preview"
        component={SceneVideoClip}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          videoSrc: "https://remotion.media/video.mp4",
          headline: "ARQUIVO EM MOVIMENTO",
          badge: "CLIPE // ARQUIVO",
          overlayText: "Registro original restaurado",
          muted: true,
        }}
      />
    </>
  );
};

/**
 * Default Remotion root. Generated channel episodes compose their own root via
 * createEpisodeRoot(), which includes CoreCompositions plus the episode.
 */
export const Root: React.FC = () => {
  return <CoreCompositions />;
};
