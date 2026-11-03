// Golden fixture for generated editable episode shape. Typechecked in CI.
import React from "react";
import { Track } from "remotion";
import {
  EpisodeShell,
  SceneDocumentReveal,
  SceneKenBurns,
} from "../../../src/video/public";
import { captions } from "./data/captions";
import { theme } from "./data/theme";

export const Episode: React.FC = () => {
  return (
    <EpisodeShell
      theme={theme}
      backgroundMusicSrc="music/bed.mp3"
      backgroundMusicVolume={0.16}
      voiceovers={[
        {
          id: "vo_01",
          src: "audio/vo_01.mp3",
          startInSeconds: 3,
          durationInSeconds: 10,
          volume: 1,
        },
      ]}
      captions={captions}
      actTimelines={[]}
      captionsIntroDurationFrames={90}
      introDurationFrames={90}
    >
      <Track name="Cenas">
        <SceneKenBurns
          name={"Cena 01 — Abertura"}
          from={90}
          durationInFrames={150}
          imageSrc={"scenes/01_abertura.jpg"}
          direction={"zoom-in"}
          badge={"ARQUIVO"}
          headline={"Abertura"}
          caption={""}
        />
        <SceneDocumentReveal
          name={"Cena 02 — Documento"}
          from={240}
          durationInFrames={180}
          headline={"Documento"}
          subheadline={"1889"}
          badge={"CONFIDENCIAL"}
          accentColor={"#D4AF37"}
          dangerColor={"#EF4444"}
        />
      </Track>
    </EpisodeShell>
  );
};
