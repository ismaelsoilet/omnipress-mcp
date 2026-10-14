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
import { ClassifiedStamp } from "../components/ClassifiedStamp";
import { ScrambledText } from "../components/ScrambledText";
import { TacticalGrid } from "../components/TacticalGrid";
import { FilmGrain } from "../components/FilmGrain";
import { SynchronizedCaptions } from "../components/SynchronizedCaptions";
import { EpisodeConfig } from "../types";

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
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;

  const episodeTitle = config?.title || "EPISÓDIO DOCUMENTAL";
  const scenes = config?.scenes || [];

  // Função de Ducking Dinâmico da Trilha Sonora
  // Mantém a música envolvente em ~-16dB (volume 0.16) durante a fala do narrador
  // e eleva para ~-7dB (volume 0.45) nas transições e cartelas de impacto
  const getMusicVolume = (frame: number): number => {
    if (frame < introDurationFrames) {
      return 0.25;
    }
    const currentSec = (frame - introDurationFrames) / fps;
    const isSpeaking = config?.voiceovers?.some((vox) => {
      return currentSec >= vox.startInSeconds && currentSec <= (vox.startInSeconds + vox.durationInSeconds);
    });
    return isSpeaking ? 0.16 : 0.45;
  };

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0C10" }}>
      {/* 1. Trilha Sonora Master com Ducking Dinâmico Automático */}
      {config?.backgroundMusicSrc && (
        <Audio
          src={staticFile(config.backgroundMusicSrc)}
          volume={getMusicVolume}
        />
      )}

      {/* 2. Vinheta Oficial de Abertura (0 a 4s) */}
      {enableIntro && (
        <Sequence from={0} durationInFrames={introDurationFrames}>
          <ChannelIntro
            channelName={config?.introProps?.channelName || "DOCUMENTÁRIO"}
            badgeText={config?.introProps?.badgeText || "ARQUIVO ESPECIAL"}
            subText={config?.introProps?.subText || "PRODUÇÃO ORIGINAL"}
            classifiedCode={config?.introProps?.classifiedCode || "REF // OFICIAL"}
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

      {/* 4. Sequência de Cenas e Dossiês */}
      {scenes.map((scene, index) => {
        // Calcula o offset acumulado dos frames das cenas anteriores
        let startFrame = enableIntro ? introDurationFrames : 0;
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
            {/* Fallback de áudio de cena individual se especificado */}
            {scene.voiceoverAudioSrc && (
              <Audio src={staticFile(scene.voiceoverAudioSrc)} volume={1.0} />
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
                      color: "#D4AF37",
                      fontFamily: "'Courier New', Courier, monospace",
                      fontSize: isVertical ? 16 : 20,
                      letterSpacing: 4,
                      fontWeight: 800,
                    }}
                  >
                    {scene.badge || "DOSSIÊ OFICIAL // TRANSIÇÃO"}
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
                      text="CONFIDENCIAL"
                      startFrame={15}
                      color="#B3261E"
                    />
                  </div>
                </div>
              </AbsoluteFill>
            ) : (
              // Imagem Documental em Movimento Suave (Ken Burns)
              <KenBurnsImage
                imageSrc={staticFile(scene.mediaSrc)}
                durationInFrames={sceneDurationFrames}
                direction={index % 2 === 0 ? "zoom-in" : "zoom-out"}
                headline={scene.headline}
                caption={scene.notes}
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

