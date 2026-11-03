import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  Track,
  useVideoConfig,
} from "remotion";
import { resolveMediaSrc } from "../media";
import { themeVars, type VideoTheme } from "../theme";
import {
  ActTimeline,
  ActData,
  VoiceoverTrack,
} from "../types";
import { SynchronizedCaptions } from "./SynchronizedCaptions";

export interface EpisodeShellProps {
  theme?: Partial<VideoTheme>;
  backgroundMusicSrc?: string;
  backgroundMusicVolume?: number;
  outroMusicSrc?: string;
  outroMusicStartSec?: number;
  voiceovers?: VoiceoverTrack[];
  captions?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
  captionsIntroDurationFrames?: number;
  introDurationFrames?: number;
  children?: React.ReactNode;
}

/**
 * Shared shell for generated editable episodes.
 *
 * Audio stays locked to the speech alignment (Rule 10): voiceover and captions
 * are derived from the master timeline, while the scene Track is the editable
 * surface in the Remotion Studio.
 */
export const EpisodeShell: React.FC<EpisodeShellProps> = ({
  theme,
  backgroundMusicSrc,
  backgroundMusicVolume = 0.16,
  outroMusicSrc,
  outroMusicStartSec = 0,
  voiceovers = [],
  captions,
  actTimelines,
  captionsIntroDurationFrames = 0,
  introDurationFrames = 0,
  children,
}) => {
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const isVertical = height > width;

  const getMusicVolume = (frame: number): number => {
    if (frame < introDurationFrames) {
      return 0.28;
    }
    const currentSec = (frame - introDurationFrames) / fps;
    const isSpeaking = voiceovers.some((vox) => {
      return (
        currentSec >= vox.startInSeconds &&
        currentSec <= vox.startInSeconds + vox.durationInSeconds
      );
    });
    return isSpeaking ? Math.min(0.18, backgroundMusicVolume) : 0.28;
  };

  return (
    <AbsoluteFill
      style={{
        ...themeVars({
          primaryColor: theme?.primary,
          accentColor: theme?.accent,
          highlightColor: theme?.highlight,
          backgroundColor: theme?.background,
          textColor: theme?.text,
          secondaryTextColor: theme?.secondaryText,
          successColor: theme?.success,
          dangerColor: theme?.danger,
        }),
        backgroundColor: "var(--omni-background, #0B1220)",
      }}
    >
      {backgroundMusicSrc ? (
        <Track name="Trilha Sonora">
          <Sequence
            name="Trilha principal"
            from={0}
            durationInFrames={durationInFrames}
          >
            <Audio
              src={resolveMediaSrc(backgroundMusicSrc)}
              volume={(frame) => {
                const duck = getMusicVolume(frame);
                const fadeFrames = 5 * fps;
                if (frame > durationInFrames - fadeFrames) {
                  const progress =
                    (durationInFrames - frame) / fadeFrames;
                  return duck * Math.max(0, Math.min(1, progress));
                }
                return duck;
              }}
            />
          </Sequence>
        </Track>
      ) : null}

      {outroMusicSrc ? (
        <Track name="Música de Encerramento">
          <Sequence
            name="Música de encerramento"
            from={Math.round(outroMusicStartSec * fps)}
          >
            <Audio
              src={resolveMediaSrc(outroMusicSrc)}
              volume={(frame) => {
                const globalFrame =
                  Math.round(outroMusicStartSec * fps) + frame;
                const duck = getMusicVolume(globalFrame);
                const fadeInFrames = 5 * fps;
                let volume = duck;
                if (frame < fadeInFrames) {
                  volume = duck * (frame / fadeInFrames);
                }
                const distanceFromEnd = durationInFrames - globalFrame;
                if (distanceFromEnd < 5 * fps && distanceFromEnd > 0) {
                  volume *= distanceFromEnd / (5 * fps);
                } else if (distanceFromEnd <= 0) {
                  volume = 0;
                }
                return volume;
              }}
            />
          </Sequence>
        </Track>
      ) : null}

      {voiceovers.length > 0
        ? voiceovers.map((voiceover, index) => (
            <Track key={voiceover.id} name={`Locução ${index + 1}`}>
              <Sequence
                name={`Locução ${voiceover.id}`}
                from={Math.round(voiceover.startInSeconds * fps)}
                durationInFrames={Math.max(
                  1,
                  Math.round(voiceover.durationInSeconds * fps)
                )}
              >
                <Audio
                  src={resolveMediaSrc(voiceover.src)}
                  volume={voiceover.volume ?? 1.0}
                />
              </Sequence>
            </Track>
          ))
        : null}

      {children}

      {captions && actTimelines ? (
        <SynchronizedCaptions
          introDurationFrames={captionsIntroDurationFrames}
          isVertical={isVertical}
          captionsData={captions}
          actTimelines={actTimelines}
        />
      ) : null}
    </AbsoluteFill>
  );
};
