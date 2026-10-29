import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import { ChannelIntro } from "./ChannelIntro";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { HeraldicSurgery } from "../components/HeraldicSurgery";
import { ChannelOutro } from "../components/ChannelOutro";
import { ClassifiedStamp } from "../components/ClassifiedStamp";
import { ScrambledText } from "../components/ScrambledText";
import { TacticalGrid } from "../components/TacticalGrid";
import { FilmGrain } from "../components/FilmGrain";
import { SynchronizedCaptions } from "../components/SynchronizedCaptions";
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

export interface DocumentaryEpisodeProps {
  config?: EpisodeConfig;
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

  // Função de Ducking Dinâmico da Trilha Sonora (Regra 10: teto de 0.12 a 0.18 sob a fala)
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

  const resolveAudioSrc = (src: string) => {
    return src.startsWith("http") || src.startsWith("data:") ? src : staticFile(src);
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
      {/* 1. Trilha Sonora Master com ducking dinâmico sob a fala */}
      {config?.backgroundMusicSrc && (
        <Sequence from={0} durationInFrames={durationInFrames}>
          <Audio
            src={resolveAudioSrc(config.backgroundMusicSrc)}
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
      )}

      {/* 1.2 Trilha Sonora Secundária / Encerramento (opcional via config) */}
      {config?.outroMusicSrc && (
        <Sequence from={Math.round((config.outroMusicStartSec ?? 0) * fps)}>
          <Audio
            src={resolveAudioSrc(config.outroMusicSrc)}
            volume={(f) => {
              const startSec = config.outroMusicStartSec ?? 0;
              const globalFrame = Math.round(startSec * fps) + f;
              const duck = getMusicVolume(globalFrame);
              // Fade-in suave de 5 segundos
              const fadeInFrames = 5 * fps;
              let vol = duck;
              if (f < fadeInFrames) {
                vol = duck * (f / fadeInFrames);
              }
              // Fade-out suave nos últimos 5 segundos do documentário
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
      )}

      {/* 2. Vinheta Oficial de Abertura (0 a 4s) */}
      {enableIntro && (
        <Sequence from={0} durationInFrames={introDurationFrames}>
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
      )}

      {/* 3. Faixas de Locução Humana Masterizadas */}
      {config?.voiceovers?.map((vox) => {
        const startFrame = Math.round(
          (vox.startInSeconds + (enableIntro ? introDurationFrames / fps : 0)) * fps
        );
        const durationFrames = Math.round(vox.durationInSeconds * fps);
        return (
          <Sequence key={vox.id} from={startFrame} durationInFrames={durationFrames}>
            <Audio src={staticFile(vox.src)} volume={vox.volume ?? 1.0} />
          </Sequence>
        );
      })}

      {/* 4. Sequência de Cenas e Dossiês (Sincronização 1:1 Estrita Fala-Frame) */}
      {scenes.map((scene, index) => {
        // Cálculo direto a partir do início da fala no áudio (Regra 10: Speech-to-Frame Lock)
        const sceneOffsetSec = (scene as DocumentaryScene).startInSeconds !== undefined
          ? (scene as DocumentaryScene).startInSeconds!
          : scenes.slice(0, index).reduce((acc, s) => acc + (s.durationInSeconds || 0), 0);
        
        const startFrame = (enableIntro ? introDurationFrames : 0) + Math.round(sceneOffsetSec * fps);
        const sceneDurationFrames = Math.round((scene.durationInSeconds || 3.0) * fps);

        return (
          <Sequence
            key={scene.id || index}
            from={startFrame}
            durationInFrames={sceneDurationFrames}
          >
            {/* Fallback de áudio de cena individual se especificado */}
            {scene.voiceoverAudioSrc && (
              <Audio src={staticFile(scene.voiceoverAudioSrc)} volume={1.0} />
            )}

            {/* Efeito Sonoro (SFX) Tátil da Cena */}
            {scene.sfxSrc && (
              <Sequence from={0} durationInFrames={Math.min(sceneDurationFrames, 120)}>
                <Audio
                  src={staticFile(scene.sfxSrc)}
                  volume={scene.sfxVolume ?? 0.35}
                />
              </Sequence>
            )}

            {scene.type === "document-reveal" ? (
              // Cartela Tática de Transição de Arquivo / Caso
              <AbsoluteFill
                style={{
                  backgroundColor: "#080A0E",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 40,
                }}
              >
                <TacticalGrid />
                <FilmGrain opacity={0.08} />

                <div
                  style={{
                    textAlign: "center",
                    maxWidth: isVertical ? 900 : 1200,
                    zIndex: 10,
                  }}
                >
                  <div
                    style={{
                      display: "inline-block",
                      marginBottom: 20,
                      color: "var(--omni-accent, #3B82F6)",
                      fontFamily: "'Courier New', Courier, monospace",
                      fontSize: isVertical ? 16 : 20,
                      letterSpacing: 4,
                      fontWeight: 800,
                    }}
                  >
                    {scene.badge || ""}
                  </div>

                  <h1
                    style={{
                      color: "#F5F6F8",
                      fontFamily: "'Cinzel', Georgia, serif",
                      fontSize: isVertical ? 38 : 52,
                      fontWeight: 900,
                      letterSpacing: 3,
                      margin: "0 0 24px 0",
                      lineHeight: 1.25,
                      textTransform: "uppercase",
                    }}
                  >
                    <ScrambledText
                      text={scene.headline || episodeTitle}
                      durationInFrames={35}
                    />
                  </h1>

                  {scene.subheadline && (
                    <p
                      style={{
                        color: "#9EA8B6",
                        fontFamily: "system-ui, sans-serif",
                        fontSize: isVertical ? 20 : 24,
                        letterSpacing: 1,
                        margin: 0,
                      }}
                    >
                      {scene.subheadline}
                    </p>
                  )}

                  <div style={{ marginTop: 35 }}>
                    <ClassifiedStamp
                      text={scene.badge || ""}
                      startFrame={15}
                      color="var(--omni-danger, #EF4444)"
                    />
                  </div>
                </div>
              </AbsoluteFill>
            ) : scene.type === "channel-outro" ? (
              // Vinheta Oficial de Encerramento e Compartilhamento com Tipografia de Alto Impacto
              <ChannelOutro
                durationInFrames={sceneDurationFrames}
                channelName={config?.introProps?.channelName || ""}
                primaryColor={config?.introProps?.primaryColor}
                tagline={config?.introProps?.subText || ""}
              />
            ) : scene.type === "heraldic-surgery" || scene.type === "image-morph" ? (
              // Animação Especial: Cirurgia Heráldica / Metamorfose Visual
              <HeraldicSurgery
                durationInFrames={sceneDurationFrames}
                badge={scene.badge}
                beforeSrc={scene.beforeSrc || scene.mediaSrc}
                afterSrc={scene.afterSrc}
              />
            ) : (
              // Imagem Documental com Movimento Dinâmico (Começa em scale 1.0, sem cobrir rostos)
              <KenBurnsImage
                imageSrc={scene.mediaSrc ? (scene.mediaSrc.startsWith("http") || scene.mediaSrc.startsWith("data:") ? scene.mediaSrc : staticFile(scene.mediaSrc)) : ""}
                durationInFrames={sceneDurationFrames}
                direction={scene.cameraDirection || getCameraPreset(index, scene.headline, scene.badge)}
                badge={scene.badge}
              />
            )}
          </Sequence>
        );
      })}

      {/* 5. Overlay Global de Legendas Dinâmicas Sincronizadas (Whisper Word Timestamps) */}
      <SynchronizedCaptions
        introDurationFrames={enableIntro ? introDurationFrames : 0}
        isVertical={isVertical}
        captionsData={config?.captions}
        actTimelines={config?.actTimelines}
      />
    </AbsoluteFill>
  );
};

