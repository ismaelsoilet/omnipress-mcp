// Golden fixture for generated editable episode shape. Typechecked in CI.
import React from "react";
import { Track } from "remotion";
import {
  EpisodeShell,
  SceneDocumentReveal,
  SceneKenBurns,
  SceneStatCounter,
  SceneTacticalMap,
  SceneVideoClip,
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
        <SceneTacticalMap
          name={"Cena 03 — Mapa"}
          from={420}
          durationInFrames={120}
          imageSrc={"scenes/03_mapa.jpg"}
          headline={"Rota do arquivo"}
          badge={"MAPA"}
          coordinates={"23°33′S 46°38′W"}
          accentColor={"#3B82F6"}
        />
        <SceneStatCounter
          name={"Cena 04 — Número"}
          from={540}
          durationInFrames={120}
          value={1889}
          label={"Documentos"}
          headline={"O número"}
          accentColor={"#FACC15"}
        />
        <SceneVideoClip
          name={"Cena 05 — Clipe"}
          from={660}
          durationInFrames={120}
          videoSrc={"scenes/05_clip.mp4"}
          headline={"Arquivo em movimento"}
          badge={"CLIPE"}
          overlayText={"Registro original"}
          muted
        />
      </Track>
    </EpisodeShell>
  );
};
