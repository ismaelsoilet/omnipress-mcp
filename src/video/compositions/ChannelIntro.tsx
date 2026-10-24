import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChannelIntroProps } from "../types";
import { FilmGrain } from "../components/FilmGrain";
import { TacticalGrid } from "../components/TacticalGrid";
import { DustParticles } from "../components/DustParticles";
import { AnamorphicFlare } from "../components/AnamorphicFlare";
import { ScrambledText } from "../components/ScrambledText";
import { ClassifiedStamp } from "../components/ClassifiedStamp";

export const ChannelIntro: React.FC<ChannelIntroProps> = ({
  channelName,
  badgeText,
  subText,
  classifiedCode,
  primaryColor = "#3B82F6", // Padrão agnóstico, customizável por props
  backgroundColor = "#0A0C10",
  language = "pt",
  audioSrc,
  enableAudio = true,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Textos padrão bilíngues agnósticos
  const isEn = language === "en";
  const finalTitle = channelName || (isEn ? "CHANNEL NAME" : "NOME DO CANAL");
  const finalBadge =
    badgeText || (isEn ? "FEATURED CONTENT // OFFICIAL" : "CONTEÚDO OFICIAL // DESTAQUE");
  const finalSub =
    subText ||
    (isEn
      ? "OFFICIAL RECORDS • THE UNTOLD STORY"
      : "DOCUMENTOS & INVESTIGAÇÕES");
  const finalCode =
    classifiedCode || (isEn ? "REF // OMNIPRESS-EN" : "REF // OMNIPRESS-PT");
  const stampText = isEn ? "OFFICIAL" : "OFICIAL";

  // 1. Animação de entrada com física de mola (Spring)
  const introSpring = spring({
    frame,
    fps,
    config: {
      damping: 14,
      mass: 0.8,
      stiffness: 85,
    },
  });

  // 2. Camera Shake realista no momento do impacto do carimbo (frames 18 a 28)
  const shakeDecay = interpolate(frame, [18, 28], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shakeX = Math.sin(frame * 1.8) * 5 * shakeDecay;
  const shakeY = Math.cos(frame * 2.1) * 3 * shakeDecay;

  // 3. Escala contínua lenta de câmera (Slow Push-in cinemático ao longo de 4 segundos)
  const cameraScale = interpolate(frame, [0, 120], [0.96, 1.05], {
    extrapolateRight: "clamp",
  });

  // 4. Rotação sutil do anel externo do selo
  const ringRotation = interpolate(frame, [0, 120], [-18, 35]);

  // 5. Varredura de luz dourada (Shimmer Glint) no título
  const glintProgress = interpolate(frame, [24, 65], [-100, 220], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 6. Fade out cinematográfico estendido (tempo de leitura garantido de f45 a f104)
  const fadeOut = interpolate(frame, [104, 120], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Responsividade vertical vs horizontal
  const isVertical = height > width;
  const titleFontSize = isVertical ? 60 : 78;
  const sealSize = isVertical ? 200 : 230;

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        overflow: "hidden",
        opacity: fadeOut,
        transform: `translate(${shakeX}px, ${shakeY}px)`,
      }}
    >
      {/* 1. Áudio Cinemático Multi-Camada (Soundscape Sincronizado se fornecido) */}
      {enableAudio && audioSrc && (
        <Audio
          src={audioSrc}
          volume={1.0}
        />
      )}

      {/* 2. Fundo com Gradiente Radial Profundo e Vinheta Escura */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at center, #171c26 0%, ${backgroundColor} 70%, #030406 100%)`,
        }}
      />

      {/* 2. Partículas Volumétricas de Poeira e Brasas Douradas */}
      <DustParticles count={isVertical ? 24 : 36} />

      {/* 3. Grade Tática com Mira e Linha de Varredura de Radar */}
      <TacticalGrid
        color={primaryColor}
        code={finalCode}
        dateStr={isEn ? "STATUS: UNSEALED" : "STATUS: DESCLASSIFICADO"}
        opacity={0.35}
      />

      {/* 4. Carimbo Desgastado no Canto Superior Direito (Slamming no frame 18) */}
      <div
        style={{
          position: "absolute",
          top: isVertical ? 120 : 70,
          right: isVertical ? 40 : 80,
          zIndex: 5,
        }}
      >
        <ClassifiedStamp
          text={stampText}
          color="#D43F3A"
          startFrame={18}
          rotation={isVertical ? -12 : -8}
          scaleFactor={isVertical ? 0.9 : 1.1}
        />
      </div>

      {/* 5. Granulação de Película de Cinema 35mm */}
      <FilmGrain opacity={0.11} />

      {/* 6. Feixe de Luz Anamórfica Dourada (Expande no frame 22) */}
      <AnamorphicFlare color="#FFE082" startFrame={22} duration={32} />

      {/* 7. Contêiner Central Animado com Câmera Push-In */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          transform: `scale(${cameraScale * introSpring})`,
          opacity: introSpring,
        }}
      >
        {/* Selo Circular de Arquivo com Relevo Metálico */}
        <div
          style={{
            position: "relative",
            width: sealSize,
            height: sealSize,
            marginBottom: isVertical ? 32 : 26,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {/* Anel Externo Giratório com Notches e Marcações Táticas */}
          <svg
            width={sealSize}
            height={sealSize}
            viewBox="0 0 200 200"
            style={{
              position: "absolute",
              transform: `rotate(${ringRotation}deg)`,
            }}
          >
            <circle
              cx="100"
              cy="100"
              r="92"
              stroke={primaryColor}
              strokeWidth="2.5"
              fill="none"
              strokeDasharray="8 10"
              opacity="0.65"
            />
            <circle
              cx="100"
              cy="100"
              r="82"
              stroke={primaryColor}
              strokeWidth="1.2"
              fill="none"
              opacity="0.4"
            />
            {/* Marcadores de Ângulo (0, 90, 180, 270) */}
            <line x1="100" y1="2" x2="100" y2="12" stroke={primaryColor} strokeWidth="3" />
            <line x1="100" y1="188" x2="100" y2="198" stroke={primaryColor} strokeWidth="3" />
            <line x1="2" y1="100" x2="12" y2="100" stroke={primaryColor} strokeWidth="3" />
            <line x1="188" y1="100" x2="198" y2="100" stroke={primaryColor} strokeWidth="3" />
          </svg>

          {/* Círculo Central com Sombra de Relevo Metálico */}
          <div
            style={{
              width: sealSize * 0.74,
              height: sealSize * 0.74,
              borderRadius: "50%",
              backgroundColor: "rgba(12, 15, 20, 0.95)",
              border: `2px solid ${primaryColor}`,
              boxShadow: `0 0 35px rgba(212, 175, 55, 0.35), inset 0 0 20px rgba(212, 175, 55, 0.25)`,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            {/* Ícone Heráldico de Arquivo / Escudo Tático */}
            <svg
              width="68"
              height="68"
              viewBox="0 0 24 24"
              fill="none"
              stroke={primaryColor}
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ filter: "drop-shadow(0 0 8px rgba(212, 175, 55, 0.7))" }}
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
          </div>
        </div>

        {/* Badge Superior com Decodificação Militar Cipher */}
        <div
          style={{
            backgroundColor: "rgba(212, 175, 55, 0.12)",
            border: `1px solid ${primaryColor}`,
            borderRadius: 4,
            padding: "6px 22px",
            color: primaryColor,
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 15 : 17,
            fontWeight: 800,
            letterSpacing: 4,
            textTransform: "uppercase",
            marginBottom: 16,
            boxShadow: "0 0 15px rgba(212, 175, 55, 0.2)",
          }}
        >
          <ScrambledText text={finalBadge} startFrame={6} durationInFrames={36} />
        </div>

        {/* Título Principal com Brilho Shimmer e Sombra Metálica */}
        <div style={{ position: "relative", overflow: "hidden", padding: "0 24px" }}>
          <h1
            style={{
              margin: 0,
              color: "#FFFFFF",
              fontSize: titleFontSize,
              fontWeight: 900,
              fontFamily: "'Cinzel', 'Times New Roman', Georgia, serif",
              letterSpacing: isVertical ? 6 : 11,
              textTransform: "uppercase",
              textAlign: "center",
              textShadow: `0 0 30px rgba(212, 175, 55, 0.65), 0 6px 18px rgba(0, 0, 0, 0.95)`,
            }}
          >
            {finalTitle}
          </h1>

          {/* Varredura Dinâmica de Luz Dourada (Shimmer Glint) */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: `${glintProgress}%`,
              width: "45%",
              height: "100%",
              background:
                "linear-gradient(90deg, transparent, rgba(255, 240, 170, 0.9), transparent)",
              transform: "skewX(-25deg)",
              pointerEvents: "none",
            }}
          />
        </div>

        {/* Linha Divisória Ornamental com Losangos Dourados */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            width: isVertical ? "80%" : 520,
            margin: "20px 0 16px 0",
          }}
        >
          <div
            style={{
              flex: 1,
              height: 1,
              background: `linear-gradient(90deg, transparent, ${primaryColor})`,
            }}
          />
          <div
            style={{
              width: 9,
              height: 9,
              backgroundColor: primaryColor,
              transform: "rotate(45deg)",
              margin: "0 14px",
              boxShadow: `0 0 12px ${primaryColor}`,
            }}
          />
          <div
            style={{
              flex: 1,
              height: 1,
              background: `linear-gradient(90deg, ${primaryColor}, transparent)`,
            }}
          />
        </div>

        {/* Subtítulo / Lema Decodificado em Monospace */}
        <div
          style={{
            color: "#D0D7E2",
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: isVertical ? 15 : 18,
            fontWeight: 700,
            letterSpacing: isVertical ? 3 : 5,
            textTransform: "uppercase",
            textAlign: "center",
            opacity: 0.95,
          }}
        >
          <ScrambledText text={finalSub} startFrame={14} durationInFrames={40} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
