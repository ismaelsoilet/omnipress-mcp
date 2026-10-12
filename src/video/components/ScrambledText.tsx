import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

interface ScrambledTextProps {
  text: string;
  startFrame?: number;
  durationInFrames?: number;
  encryptedChars?: string;
  style?: React.CSSProperties;
  className?: string;
  goldGlitch?: boolean;
}

const CIPHER_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*@!$<>[]+/";

export const ScrambledText: React.FC<ScrambledTextProps> = ({
  text,
  startFrame = 0,
  durationInFrames = 35,
  encryptedChars = CIPHER_CHARS,
  style,
  goldGlitch = true,
}) => {
  const frame = useCurrentFrame();
  const activeFrame = Math.max(0, frame - startFrame);

  const displayedText = useMemo(() => {
    return text.split("").map((char, index) => {
      if (char === " ") return { char: " ", locked: true };

      // Revelação progressiva da esquerda para a direita
      const charDelay = (index / text.length) * (durationInFrames * 0.65);
      const progress = activeFrame - charDelay;
      const threshold = durationInFrames * 0.35;

      if (progress >= threshold) {
        return { char, locked: true };
      }

      if (progress < 0) {
        // Antes do início para este caractere, mostra glifo cifrado
        const seedIndex = Math.abs(Math.sin(index * 7919) * encryptedChars.length);
        return { char: encryptedChars[Math.floor(seedIndex)], locked: false };
      }

      // Durante a decodificação: jitter pseudo-aleatório determinístico por frame
      const jitterIndex =
        Math.abs(Math.sin(activeFrame * 17 + index * 101)) * encryptedChars.length;
      return { char: encryptedChars[Math.floor(jitterIndex)], locked: false };
    });
  }, [text, activeFrame, durationInFrames, encryptedChars]);

  return (
    <span
      style={{
        fontFamily: "'Courier New', Courier, monospace",
        display: "inline-flex",
        flexWrap: "wrap",
        ...style,
      }}
    >
      {displayedText.map((item, idx) => (
        <span
          key={idx}
          style={{
            color: item.locked
              ? style?.color || "#FFFFFF"
              : goldGlitch
              ? "#D4AF37"
              : "rgba(255, 255, 255, 0.4)",
            textShadow: item.locked
              ? style?.textShadow || "none"
              : "0 0 8px rgba(212, 175, 55, 0.8)",
            opacity: item.locked ? 1 : 0.85,
            transition: "color 0.1s ease",
          }}
        >
          {item.char}
        </span>
      ))}
    </span>
  );
};
