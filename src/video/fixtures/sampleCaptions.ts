import short02Json from "./short_02_captions.json";
import short03Json from "./short_03_captions.json";
import short03ReelsJson from "./short_03_reels_88s_captions.json";
import short04Json from "./short_04_captions.json";
import { ActData } from "../types";

/**
 * Universal caption fixtures for Remotion video compositions.
 * Used for development previews and CI builds when channel-specific media is not mounted.
 */
export const short02Captions: Record<string, ActData> = short02Json as unknown as Record<string, ActData>;
export const short03Captions: Record<string, ActData> = short03Json as unknown as Record<string, ActData>;
export const short03ReelsCaptions: Record<string, ActData> = short03ReelsJson as unknown as Record<string, ActData>;
export const short04Captions: Record<string, ActData> = short04Json as unknown as Record<string, ActData>;

export const sampleShortCaptions: Record<string, ActData> = {
  short_01: {
    name: "A Cidade Proibida de 18 Andares no Subsolo",
    duration: 65.07,
    words: [
      { word: "Em", start: 0.95, end: 1.22 },
      { word: "1963,", start: 1.22, end: 2.55 },
      { word: "E", start: 2.58, end: 3.1 },
      { word: "encontrou", start: 3.1, end: 3.8 },
    ],
    chunks: [
      {
        start: 0.95,
        end: 2.55,
        text: "Em 1963, um homem derrubou uma parede no porão...",
        words: [
          { word: "Em", start: 0.95, end: 1.22 },
          { word: "1963,", start: 1.22, end: 2.55 },
        ],
      },
      {
        start: 2.58,
        end: 5.12,
        text: "E encontrou uma galeria que não constava em nenhum mapa.",
        words: [
          { word: "E", start: 2.58, end: 3.1 },
          { word: "encontrou", start: 3.1, end: 3.8 },
        ],
      },
    ],
  },
};

export const sampleEpisodeCaptions: Record<string, ActData> = {
  act_00: {
    name: "Prólogo",
    duration: 65.78,
    words: [
      { word: "Documentos", start: 0.0, end: 1.0 },
      { word: "desclassificados", start: 1.0, end: 2.5 },
    ],
    chunks: [
      {
        start: 0.0,
        end: 3.5,
        text: "Documentos desclassificados revelam a história oculta.",
        words: [
          { word: "Documentos", start: 0.0, end: 1.0 },
          { word: "desclassificados", start: 1.0, end: 2.5 },
        ],
      },
    ],
  },
};
