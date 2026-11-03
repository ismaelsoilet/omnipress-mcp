/**
 * Stable public surface for generated editable episode TSX.
 *
 * Generated code lives in channels/<slug>/video/episodes/<episode>/ and must
 * import only from this barrel, never from internal component paths.
 */
export { CoreCompositions, Root } from "./Root";
export { createEpisodeRoot } from "./ChannelRoot";
export type { EpisodeRegistration } from "./ChannelRoot";
export { EpisodeShell } from "./components/EpisodeShell";
export type { EpisodeShellProps } from "./components/EpisodeShell";
export { ChannelIntro } from "./compositions/ChannelIntro";
export {
  SceneKenBurns,
  SceneDocumentReveal,
  SceneHeraldic,
  SceneOutro,
} from "./components/scenes";
export type {
  SceneKenBurnsProps,
  SceneDocumentRevealProps,
  SceneHeraldicProps,
  SceneOutroProps,
} from "./components/scenes";
export { DEFAULT_THEME, resolveTheme, themeVars } from "./theme";
export type { VideoTheme } from "./theme";
export type {
  ActData,
  ActTimeline,
  CaptionChunk,
  ChannelIntroProps,
  DocumentaryScene,
  EpisodeConfig,
  EpisodeTheme,
  KenBurnsSceneProps,
  SupportedLanguage,
  VoiceoverTrack,
  WordTiming,
} from "./types";
