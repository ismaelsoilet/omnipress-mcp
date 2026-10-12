import React from "react";
import { Composition } from "remotion";
import { ChannelIntro } from "./compositions/ChannelIntro";
import { ChannelIntroProps } from "./types";

export const Root: React.FC = () => {
  return (
    <>
      {/* 1. Vinheta 16:9 — Português (YouTube Principal) */}
      <Composition<ChannelIntroProps>
        id="ChannelIntro-16x9"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "pt",
          channelName: "DOSSIÊ HISTÓRICO",
          badgeText: "ARQUIVO DESCLASSIFICADO // NÍVEL 1",
          subText: "DOCUMENTOS SECRETOS • A HISTÓRIA OCULTA",
          classifiedCode: "REF // TOP-SECRET-TUR-1963",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 2. Vinheta 9:16 — Português (YouTube Shorts / Reels / TikTok) */}
      <Composition<ChannelIntroProps>
        id="ChannelIntro-9x16"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "pt",
          channelName: "DOSSIÊ HISTÓRICO",
          badgeText: "ARQUIVO DESCLASSIFICADO",
          subText: "HISTÓRIA OCULTA • FATOS REAIS",
          classifiedCode: "REF // 1963-SHORTS",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 3. Vinheta 16:9 — Inglês (Canal Internacional) */}
      <Composition<ChannelIntroProps>
        id="ChannelIntro-16x9-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          language: "en",
          channelName: "HISTORICAL DOSSIER",
          badgeText: "DECLASSIFIED ARCHIVE // LVL 1",
          subText: "OFFICIAL RECORDS • THE UNTOLD HISTORY",
          classifiedCode: "FILE REF // TOP-SECRET-GLOBAL",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />

      {/* 4. Vinheta 9:16 — Inglês (Shorts Internacional) */}
      <Composition<ChannelIntroProps>
        id="ChannelIntro-9x16-EN"
        component={ChannelIntro}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          language: "en",
          channelName: "HISTORICAL DOSSIER",
          badgeText: "DECLASSIFIED ARCHIVE",
          subText: "SECRET FILES • UNTOLD HISTORY",
          classifiedCode: "FILE // SHORTS-INTL",
          primaryColor: "#D4AF37",
          backgroundColor: "#0A0C10",
        }}
      />
    </>
  );
};
