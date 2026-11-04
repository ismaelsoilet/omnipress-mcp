import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  Track,
  useVideoConfig,
} from "remotion";
import { ChannelIntro } from "./ChannelIntro";
import { SceneDocumentReveal } from "../components/scenes/SceneDocumentReveal";
import { SceneHeraldic } from "../components/scenes/SceneHeraldic";
import { SceneKenBurns } from "../components/scenes/SceneKenBurns";
import { SceneOutro } from "../components/scenes/SceneOutro";
import { SceneStatCounter } from "../components/scenes/SceneStatCounter";
import { SceneTacticalMap } from "../components/scenes/SceneTacticalMap";
import { SceneVideoClip } from "../components/scenes/SceneVideoClip";
import { SynchronizedCaptions } from "../components/SynchronizedCaptions";
import { resolveMediaSrc } from "../media";
import { DocumentaryScene, EpisodeConfig, KenBurnsSceneProps } from "../types";
import { themeVars } from "../theme";

export const getCameraPreset = (
  index: number,
  _headline?: string,
  _badge?: string
): NonNullable<KenBurnsSceneProps["direction"]> => {
  const presets: NonNullable<KenBurnsSceneProps["direction"]>[] = [
    "zoom-in",
    "pan-left",
    "zoom-out",
    "snap-zoom",
    "pan-right",
    "dramatic-push",
    "tilt-down",
  ];
  return presets[index % presets.length];
};

export interface DocumentaryEpisodeProps extends Record<string, unknown> {
  config: EpisodeConfig;
  introDurationFrames?: number;
  enableIntro?: boolean;
}

export const DocumentaryEpisode: React.FC<DocumentaryEpisodeProps> = ({
  config,
  introDurationFrames = 120, // 4.0s @ 30fps
  enableIntro = true,
}) => {
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const isVertical = height > width;

  const episodeTitle = config?.title || "";
  const scenes = config?.scenes || [];

  // Dynamic soundtrack ducking (Rule 10: 0.12–0.18 ceiling under speech).
  const getMusicVolume = (frame: number): number => {
    if (frame < introDurationFrames) {
      return 0.28;
    }
    const currentSec = (frame - introDurationFrames) / fps;
    const isSpeaking = config?.voiceovers?.some((vox) => {
      return (
        currentSec >= vox.startInSeconds &&
        currentSec <= vox.startInSeconds + vox.durationInSeconds
      );
    });
    return isSpeaking ? 0.14 : 0.28;
  };

  return (
    <AbsoluteFill
      style={{
        ...themeVars({
          primaryColor: config?.introProps?.primaryColor,
          accentColor: config?.theme?.accent,
          highlightColor: config?.theme?.highlight,
          backgroundColor: config?.theme?.background,
          textColor: config?.theme?.text,
          secondaryTextColor: config?.theme?.secondaryText,
          successColor: config?.theme?.success,
          dangerColor: config?.theme?.danger,
        }),
        backgroundColor: "var(--omni-background, #0B1220)",
      }}
    >
      {/* 1. Master soundtrack with dynamic ducking under speech */}
      {config?.backgroundMusicSrc ? (
        <Track name="Trilha Sonora">
          <Sequence
            name="Trilha principal"
            from={0}
            durationInFrames={durationInFrames}
          >
            <Audio
              src={resolveMediaSrc(config.backgroundMusicSrc)}
              volume={(f) => {
                const duck = getMusicVolume(f);
                const fadeFrames = 5 * fps;
                if (f > durationInFrames - fadeFrames) {
                  const progress = (durationInFrames - f) / fadeFrames;
                  return duck * Math.max(0, Math.min(1, progress));
                }
                return duck;
              }}
            />
          </Sequence>
        </Track>
      ) : null}

      {/* 1.2 Optional outro music, kept on its own track to avoid overlap */}
      {config?.outroMusicSrc ? (
        <Track name="Música de Encerramento">
          <Sequence
            name="Música de encerramento"
            from={Math.round((config.outroMusicStartSec ?? 0) * fps)}
          >
            <Audio
              src={resolveMediaSrc(config.outroMusicSrc)}
              volume={(f) => {
                const startSec = config.outroMusicStartSec ?? 0;
                const globalFrame = Math.round(startSec * fps) + f;
                const duck = getMusicVolume(globalFrame);
                const fadeInFrames = 5 * fps;
                let vol = duck;
                if (f < fadeInFrames) {
                  vol = duck * (f / fadeInFrames);
                }
                const distFromEnd = durationInFrames - globalFrame;
                if (distFromEnd < 5 * fps && distFromEnd > 0) {
                  vol = vol * (distFromEnd / (5 * fps));
                } else if (distFromEnd <= 0) {
                  vol = 0;
                }
                return vol;
              }}
            />
          </Sequence>
        </Track>
      ) : null}

      {/* 2. Official opening bumper */}
      {enableIntro ? (
        <Track name="Vinheta">
          <Sequence
            name="Vinheta de abertura"
            from={0}
            durationInFrames={introDurationFrames}
          >
            <ChannelIntro
              channelName={config?.introProps?.channelName || ""}
              badgeText={config?.introProps?.badgeText || ""}
              subText={config?.introProps?.subText || ""}
              classifiedCode={config?.introProps?.classifiedCode || ""}
              primaryColor={config?.introProps?.primaryColor}
              backgroundColor={config?.introProps?.backgroundColor}
              language={config?.introProps?.language || config?.language || "pt"}
            />
          </Sequence>
        </Track>
      ) : null}

      {/* 3. Mastered human narration tracks (one lane per voiceover) */}
      {config?.voiceovers?.map((vox, index) => {
        const startFrame = Math.round(
          (vox.startInSeconds + (enableIntro ? introDurationFrames / fps : 0)) *
            fps
        );
        const durationFrames = Math.round(vox.durationInSeconds * fps);
        return (
          <Track key={vox.id} name={`Locução ${index + 1}`}>
            <Sequence
              name={`VO ${index + 1} — ${vox.id}`}
              from={startFrame}
              durationInFrames={durationFrames}
            >
              <Audio
                src={resolveMediaSrc(vox.src)}
                volume={vox.volume ?? 1.0}
              />
            </Sequence>
          </Track>
        );
      })}

      {/* 3.2 Per-scene narration, kept off the scene row */}
      <Track name="Áudio de Cena">
        {scenes.map((scene, index) => {
          if (!scene.voiceoverAudioSrc) {
            return null;
          }
          const sceneOffsetSec =
            (scene as DocumentaryScene).startInSeconds !== undefined
              ? (scene as DocumentaryScene).startInSeconds!
              : scenes
                  .slice(0, index)
                  .reduce((acc, item) => acc + (item.durationInSeconds || 0), 0);
          const startFrame =
            (enableIntro ? introDurationFrames : 0) +
            Math.round(sceneOffsetSec * fps);
          const sceneDurationFrames = Math.round(
            (scene.durationInSeconds || 3.0) * fps
          );

          return (
            <Sequence
              key={`vo-${scene.id || index}`}
              name={`VO de cena ${index + 1}`}
              from={startFrame}
              durationInFrames={sceneDurationFrames}
            >
              <Audio
                src={resolveMediaSrc(scene.voiceoverAudioSrc)}
                volume={1.0}
              />
            </Sequence>
          );
        })}
      </Track>

      {/* 3.3 Per-scene tactical SFX, isolated from narration */}
      <Track name="SFX de Cena">
        {scenes.map((scene, index) => {
          if (!scene.sfxSrc) {
            return null;
          }
          const sceneOffsetSec =
            (scene as DocumentaryScene).startInSeconds !== undefined
              ? (scene as DocumentaryScene).startInSeconds!
              : scenes
                  .slice(0, index)
                  .reduce((acc, item) => acc + (item.durationInSeconds || 0), 0);
          const startFrame =
            (enableIntro ? introDurationFrames : 0) +
            Math.round(sceneOffsetSec * fps);
          const sceneDurationFrames = Math.round(
            (scene.durationInSeconds || 3.0) * fps
          );

          return (
            <Sequence
              key={`sfx-${scene.id || index}`}
              name={`SFX de cena ${index + 1}`}
              from={startFrame}
              durationInFrames={Math.min(sceneDurationFrames, 120)}
            >
              <Audio
                src={resolveMediaSrc(scene.sfxSrc)}
                volume={scene.sfxVolume ?? 0.35}
              />
            </Sequence>
          );
        })}
      </Track>

      {/* 4. Scene sequence, strictly locked to speech (Rule 10) */}
      <Track name="Cenas">
        {scenes.map((scene, index) => {
          const sceneOffsetSec =
            (scene as DocumentaryScene).startInSeconds !== undefined
              ? (scene as DocumentaryScene).startInSeconds!
              : scenes
                  .slice(0, index)
                  .reduce((acc, item) => acc + (item.durationInSeconds || 0), 0);

          const startFrame =
            (enableIntro ? introDurationFrames : 0) +
            Math.round(sceneOffsetSec * fps);
          const sceneDurationFrames = Math.round(
            (scene.durationInSeconds || 3.0) * fps
          );
          const sceneName = `Cena ${String(index + 1).padStart(2, "0")} — ${
            scene.headline || scene.type
          }`;

          if (scene.type === "document-reveal") {
            return (
              <SceneDocumentReveal
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                headline={scene.headline || episodeTitle}
                subheadline={scene.subheadline || ""}
                badge={scene.badge || ""}
                accentColor={config?.theme?.accent}
                dangerColor={config?.theme?.danger}
              />
            );
          }

          if (scene.type === "channel-outro") {
            return (
              <SceneOutro
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                channelName={config?.introProps?.channelName || ""}
                primaryColor={config?.introProps?.primaryColor}
                tagline={config?.introProps?.subText || ""}
              />
            );
          }

          if (scene.type === "tactical-map") {
            return (
              <SceneTacticalMap
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                imageSrc={scene.mediaSrc}
                headline={scene.headline || episodeTitle}
                badge={scene.badge}
                coordinates={scene.coordinates}
                accentColor={config?.theme?.accent}
              />
            );
          }

          if (scene.type === "stat-counter") {
            return (
              <SceneStatCounter
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                value={scene.statValue ?? 0}
                prefix={scene.statPrefix}
                suffix={scene.statSuffix}
                label={scene.statLabel || scene.subheadline}
                headline={scene.headline || episodeTitle}
                accentColor={config?.theme?.highlight || config?.theme?.accent}
                backgroundSrc={scene.mediaSrc}
                locale={config?.language === "en" ? "en-US" : "pt-BR"}
              />
            );
          }

          if (scene.type === "video-clip") {
            return (
              <SceneVideoClip
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                videoSrc={scene.mediaSrc}
                headline={scene.headline || episodeTitle}
                badge={scene.badge}
                overlayText={scene.notes}
                muted={scene.videoMuted ?? true}
              />
            );
          }

          if (
            scene.type === "heraldic-surgery" ||
            scene.type === "image-morph"
          ) {
            return (
              <SceneHeraldic
                key={scene.id || index}
                name={sceneName}
                from={startFrame}
                durationInFrames={sceneDurationFrames}
                beforeSrc={scene.beforeSrc || scene.mediaSrc}
                afterSrc={scene.afterSrc}
                badge={scene.badge}
              />
            );
          }

          return (
            <SceneKenBurns
              key={scene.id || index}
              name={sceneName}
              from={startFrame}
              durationInFrames={sceneDurationFrames}
              imageSrc={scene.mediaSrc}
              direction={
                scene.cameraDirection ||
                getCameraPreset(index, scene.headline, scene.badge)
              }
              badge={scene.badge}
            />
          );
        })}
      </Track>

      {/* 5. Global synchronized captions (Whisper word timestamps) */}
      <SynchronizedCaptions
        introDurationFrames={enableIntro ? introDurationFrames : 0}
        isVertical={isVertical}
        captionsData={config?.captions}
        actTimelines={config?.actTimelines}
      />
    </AbsoluteFill>
  );
};
