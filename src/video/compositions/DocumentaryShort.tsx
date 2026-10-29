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
import { WordByWordCaptions } from "../components/WordByWordCaptions";
import { MitoRealidadeOverlays, OverlayEvent } from "../components/MitoRealidadeOverlays";
import { themeVars } from "../theme";

export interface DocumentaryShortProps {
  title?: string;
  badge?: string;
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
  highlightColor?: string;
  musicSrc?: string;
  musicVolume?: number;
  voiceoverSrc?: string;
  scenes?: DocumentaryScene[];
  captionsData?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
  captionStyle?: "word-by-word" | "chunk";
  captionsBottomPosition?: number;
  impactOverlays?: OverlayEvent[];
  showSceneMetadata?: boolean;
}

export const DocumentaryShort: React.FC<DocumentaryShortProps> = ({
  title = "",
  badge = "",
  accentColor,
  backgroundColor,
  textColor,
  highlightColor,
  musicSrc,
  musicVolume = 0.35,
  voiceoverSrc,
  scenes = [],
  captionsData,
  actTimelines,
  captionStyle = "word-by-word",
  captionsBottomPosition = 560,
  impactOverlays = [],
  showSceneMetadata = false,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Suavização acústica: Fade-in suave de 2.0s na abertura + Fade-out de 2.5s no encerramento da música
  const fadeInFrames = Math.round(2.0 * fps);
  const fadeOutFrames = Math.round(2.5 * fps);
  const fadeStart = Math.max(0, durationInFrames - fadeOutFrames);
  const effectiveMusicVolume =
    typeof musicVolume === "number"
      ? interpolate(
          frame,
          [0, fadeInFrames, fadeStart, durationInFrames],
          [0, musicVolume, musicVolume, 0],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }
        )
      : musicVolume;

  // Suavização acústica: Fade-in suave da locução nos primeiros 0.5s (15 frames)
  const voiceFadeFrames = Math.round(0.5 * fps);
  const effectiveVoiceVolume = interpolate(
    frame,
    [0, voiceFadeFrames],
    [0, 1.0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  return (
    <AbsoluteFill
      style={{
        ...themeVars({ accentColor, backgroundColor, textColor, highlightColor }),
        backgroundColor: "var(--omni-background, #0B1220)",
      }}
    >
      {/* 1. Trilha Sonora do Short (suavizada com fade-in e fade-out automático) */}
      {musicSrc && (
        <Audio src={staticFile(musicSrc)} volume={effectiveMusicVolume} />
      )}

      {/* 2. Locução Principal Suavizada */}
      {voiceoverSrc && (
        <Audio src={staticFile(voiceoverSrc)} volume={effectiveVoiceVolume} />
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
              headline={showSceneMetadata ? scene.headline : undefined}
              caption={scene.notes}
              badge={showSceneMetadata ? (scene.badge || badge) : undefined}
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
          border: "1.5px solid rgba(var(--omni-accent-rgb, 59, 130, 246), 0.5)",
          borderRadius: 14,
          padding: "16px 28px",
          backdropFilter: "blur(12px)",
          boxShadow: "0 6px 20px rgba(0, 0, 0, 0.6)",
          zIndex: 50,
        }}
      >
        <div
          style={{
            color: "var(--omni-accent, #3B82F6)",
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

      {/* 5. Overlays de Choque Visual (Carimbos MITO vs REALIDADE, Flashes & Perguntas) */}
      {impactOverlays && impactOverlays.length > 0 && (
        <MitoRealidadeOverlays events={impactOverlays} />
      )}

      {/* 7. Legendas Dinâmicas Sincronizadas (Whisper) */}
      {captionsData && actTimelines && (
        captionStyle === "word-by-word" ? (
          <WordByWordCaptions
            introDurationFrames={0}
            captionsData={captionsData}
            actTimelines={actTimelines}
            bottomPosition={captionsBottomPosition}
          />
        ) : (
          <SynchronizedCaptions
            introDurationFrames={0}
            isVertical={true}
            captionsData={captionsData}
            actTimelines={actTimelines}
          />
        )
      )}
    </AbsoluteFill>
  );
};
