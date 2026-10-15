import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { TacticalGrid } from "../components/TacticalGrid";
import { FilmGrain } from "../components/FilmGrain";
import { ActData, ActTimeline, DocumentaryScene } from "../types";
import { SynchronizedCaptions } from "../components/SynchronizedCaptions";

export interface DocumentaryShortProps {
  title: string;
  badge?: string;
  musicSrc?: string;
  musicVolume?: number;
  voiceoverSrc?: string;
  scenes: DocumentaryScene[];
  captionsData?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
}

export const DocumentaryShort: React.FC<DocumentaryShortProps> = ({
  title,
  badge = "CONTEÚDO OFICIAL // SHORTS",
  musicSrc,
  musicVolume = 0.35,
  voiceoverSrc,
  scenes = [],
  captionsData,
  actTimelines,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Fade out suave da música nos últimos 2.5 segundos
  const fadeOutFrames = Math.round(2.5 * fps);
  const fadeStart = Math.max(0, durationInFrames - fadeOutFrames);
  const effectiveMusicVolume =
    typeof musicVolume === "number"
      ? interpolate(frame, [fadeStart, durationInFrames], [musicVolume, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : musicVolume;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0C10" }}>
      {/* 1. Trilha Sonora do Short (com fade-out automático no encerramento) */}
      {musicSrc && (
        <Audio src={staticFile(musicSrc)} volume={effectiveMusicVolume} />
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
          backgroundColor: "rgba(8, 10, 14, 0.88)",
          border: "1.5px solid rgba(212, 175, 55, 0.5)",
          borderRadius: 14,
          padding: "16px 28px",
          backdropFilter: "blur(12px)",
          boxShadow: "0 6px 20px rgba(0, 0, 0, 0.6)",
          zIndex: 50,
        }}
      >
        <div
          style={{
            color: "#D4AF37",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: 22,
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
            fontSize: 20,
            fontWeight: 900,
            letterSpacing: 2,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span
            style={{
              width: 14,
              height: 14,
              backgroundColor: "#FF4D4D",
              borderRadius: "50%",
              display: "inline-block",
              boxShadow: "0 0 10px rgba(255, 77, 77, 0.8)",
            }}
          />
          REC
        </div>
      </div>

      {/* 5. Grade Tática Sutil & Grão de Filme */}
      <TacticalGrid opacity={0.12} />
      <FilmGrain opacity={0.06} />

      {/* 6. Legendas Dinâmicas Sincronizadas (Whisper) */}
      {captionsData && actTimelines && (
        <SynchronizedCaptions
          introDurationFrames={0}
          isVertical={true}
          captionsData={captionsData}
          actTimelines={actTimelines}
        />
      )}
    </AbsoluteFill>
  );
};
