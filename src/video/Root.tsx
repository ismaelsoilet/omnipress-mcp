import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import { DocumentaryEpisode } from "./compositions/DocumentaryEpisode";
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
          channelName: "NOME DO CANAL",
          badgeText: "DESTAQUE // OFICIAL",
          subText: "HISTÓRIAS & INVESTIGAÇÕES",
          classifiedCode: "REF // OMNIPRESS-PT",
          primaryColor: "#3B82F6",
          backgroundColor: "#0A0C10",
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
          channelName: "NOME DO CANAL",
          badgeText: "DESTAQUE // VERTICAL",
          subText: "FATOS REAIS • CONTEÚDO OFICIAL",
          classifiedCode: "REF // OMNIPRESS-SHORTS",
          primaryColor: "#3B82F6",
          backgroundColor: "#0A0C10",
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
          classifiedCode: "REF // OMNIPRESS-EN",
          primaryColor: "#3B82F6",
          backgroundColor: "#0A0C10",
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
          classifiedCode: "REF // OMNIPRESS-SHORTS-EN",
          primaryColor: "#3B82F6",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 5. Episódio Documental Universal 16:9 (YouTube Widescreen) */}
      <Composition
        id="DocumentaryEpisode-16x9"
        component={DocumentaryEpisode}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          enableIntro: true,
          introDurationFrames: 120,
          config: {
            id: "ep-sample-16x9",
            title: "Título do Episódio Documental",
            channelSlug: "template-channel",
            language: "pt",
            introProps: {
              channelName: "NOME DO CANAL",
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
            title: "Episódio Vertical",
            channelSlug: "template-channel",
            language: "pt",
            introProps: {
              channelName: "NOME DO CANAL",
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
          title: "Título do Short Vertical",
          badge: "CONTEÚDO OFICIAL // SHORTS",
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
          titleLine1: "MANCHETE PRINCIPAL",
          titleLine2: "SEGUNDA LINHA",
          tagText: "CATEGORIA // INVESTIGAÇÃO",
          calloutText: "CHAMADA DE IMPACTO!",
          depthTag: "TAG 1",
          peopleTag: "TAG 2",
          doorTag: "TAG 3",
          showClassifiedStamp: false,
        }}
      />
    </>
  );
};
