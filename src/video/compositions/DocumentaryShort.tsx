import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { TacticalGrid } from "../components/TacticalGrid";
import { FilmGrain } from "../components/FilmGrain";
import { DocumentaryScene } from "../types";

export interface DocumentaryShortProps {
  title: string;
  badge?: string;
  musicSrc?: string;
  musicVolume?: number;
  voiceoverSrc?: string;
  scenes: DocumentaryScene[];
}

export const DocumentaryShort: React.FC<DocumentaryShortProps> = ({
  title,
  badge = "DOSSIÊ HISTÓRICO // SHORTS",
  musicSrc,
  musicVolume = 0.35,
  voiceoverSrc,
  scenes = [],
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0C10" }}>
      {/* 1. Trilha Sonora do Short */}
      {musicSrc && (
        <Audio src={staticFile(musicSrc)} volume={musicVolume} />
      )}

      {/* 2. Locução Principal */}
      {voiceoverSrc && (
        <Audio src={staticFile(voiceoverSrc)} volume={1.0} />
      )}

      {/* 3. Sequência de Cenas e Imagens Rápidas */}
      {scenes.map((scene, index) => {
        let startFrame = 0;
        for (let i = 0; i < index; i++) {
          startFrame += Math.round(scenes[i].durationInSeconds * fps);
        }
        const sceneDurationFrames = Math.round(scene.durationInSeconds * fps);

        return (
          <Sequence
            key={scene.id || index}
            from={startFrame}
            durationInFrames={sceneDurationFrames}
          >
            <KenBurnsImage
              imageSrc={staticFile(scene.mediaSrc)}
              durationInFrames={sceneDurationFrames}
              direction={index % 2 === 0 ? "zoom-in" : "zoom-out"}
              headline={scene.headline}
              caption={scene.notes}
              badge={scene.badge || badge}
            />
          </Sequence>
        );
      })}

      {/* 4. Overlay de Top Badge Fixo para Shorts */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 40,
          right: 40,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          backgroundColor: "rgba(8, 10, 14, 0.85)",
          border: "1px solid rgba(212, 175, 55, 0.4)",
          borderRadius: 12,
          padding: "12px 20px",
          backdropFilter: "blur(10px)",
          zIndex: 50,
        }}
      >
        <div
          style={{
            color: "#D4AF37",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: 2,
          }}
        >
          {badge}
        </div>
        <div
          style={{
            color: "#FF4D4D",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: 12,
            fontWeight: 900,
            letterSpacing: 2,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              backgroundColor: "#FF4D4D",
              borderRadius: "50%",
              display: "inline-block",
            }}
          />
          REC
        </div>
      </div>
    </AbsoluteFill>
  );
};
