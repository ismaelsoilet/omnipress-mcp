import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import { DocumentaryEpisode, DocumentaryEpisodeProps } from "./compositions/DocumentaryEpisode";
import { DocumentaryScene } from "./types";
import { DocumentaryShort, DocumentaryShortProps } from "./compositions/DocumentaryShort";
import { ThumbnailEpisode, ThumbnailEpisodeProps } from "./compositions/ThumbnailEpisode";
import { sampleShortCaptions, sampleEpisodeCaptions } from "./fixtures/sampleCaptions";

/**
 * Universal Remotion Root for OmniPress MCP.
 * Agnostic compositions receiving parameters dynamically via props.
 * Channel-specific content, media and scripts belong in channels/<channel_slug>/.
 */
export const Root: React.FC = () => {
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
      <Composition<any, any>
        id="DocumentaryEpisode-16x9"
        component={DocumentaryEpisode}
        durationInFrames={25083}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={({ props }) => {
          const epProps = props as DocumentaryEpisodeProps;
          const introFrames = epProps.enableIntro ? (epProps.introDurationFrames ?? 120) : 0;
          const scenesFrames = (epProps.config?.scenes || []).reduce(
            (acc: number, s: DocumentaryScene) => acc + Math.round((s.durationInSeconds || 0) * 30),
            0
          );
          const totalFrames = scenesFrames > 0
            ? introFrames + scenesFrames
            : (epProps.config?.voiceovers?.[0]
                ? Math.round((epProps.config.voiceovers[0].durationInSeconds || 0) * 30) + introFrames
                : 25083);
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
    </>
  );
};
