import { ActData } from "../types";

/**
 * Universal agnostic caption fixtures for Remotion video compositions.
 * Used for development previews, automated testing, and CI builds
 * when channel-specific media is not mounted.
 */
export const sampleShortCaptions: Record<string, ActData> = {
  short_01: {
    name: "Abertura / Exemplo de Short",
    duration: 65.0,
    words: [
      { word: "Bem-vindo", start: 0.5, end: 1.2 },
      { word: "ao", start: 1.2, end: 1.4 },
      { word: "OmniPress,", start: 1.4, end: 2.2 },
      { word: "o", start: 2.3, end: 2.5 },
      { word: "motor", start: 2.5, end: 2.9 },
      { word: "de", start: 2.9, end: 3.1 },
      { word: "publicação", start: 3.1, end: 3.8 },
      { word: "programática.", start: 3.8, end: 4.8 },
    ],
    chunks: [
      {
        start: 0.5,
        end: 2.2,
        text: "Bem-vindo ao OmniPress,",
        words: [
          { word: "Bem-vindo", start: 0.5, end: 1.2 },
          { word: "ao", start: 1.2, end: 1.4 },
          { word: "OmniPress,", start: 1.4, end: 2.2 },
        ],
      },
      {
        start: 2.3,
        end: 4.8,
        text: "o motor de publicação programática.",
        words: [
          { word: "o", start: 2.3, end: 2.5 },
          { word: "motor", start: 2.5, end: 2.9 },
          { word: "de", start: 2.9, end: 3.1 },
          { word: "publicação", start: 3.1, end: 3.8 },
          { word: "programática.", start: 3.8, end: 4.8 },
        ],
      },
    ],
  },
};

export const sampleEpisodeCaptions: Record<string, ActData> = {
  act_00: {
    name: "Prólogo",
    duration: 60.0,
    words: [
      { word: "Este", start: 0.0, end: 0.8 },
      { word: "é", start: 0.8, end: 1.0 },
      { word: "um", start: 1.0, end: 1.3 },
      { word: "episódio", start: 1.3, end: 2.2 },
      { word: "de", start: 2.2, end: 2.4 },
      { word: "demonstração.", start: 2.4, end: 3.5 },
    ],
    chunks: [
      {
        start: 0.0,
        end: 3.5,
        text: "Este é um episódio de demonstração.",
        words: [
          { word: "Este", start: 0.0, end: 0.8 },
          { word: "é", start: 0.8, end: 1.0 },
          { word: "um", start: 1.0, end: 1.3 },
          { word: "episódio", start: 1.3, end: 2.2 },
          { word: "de", start: 2.2, end: 2.4 },
          { word: "demonstração.", start: 2.4, end: 3.5 },
        ],
      },
    ],
  },
};
