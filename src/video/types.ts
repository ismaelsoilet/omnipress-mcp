export type SupportedLanguage = "pt" | "en";

export interface ChannelIntroProps {
  channelName?: string;
  badgeText?: string;
  subText?: string;
  classifiedCode?: string;
  primaryColor?: string;
  backgroundColor?: string;
  language?: SupportedLanguage;
  audioSrc?: string;
  enableAudio?: boolean;
}

export interface KenBurnsSceneProps {
  imageSrc: string;
  durationInFrames: number;
  direction?: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "snap-zoom" | "dramatic-push" | "tilt-down" | "subtle-zoom";
  headline?: string;
  caption?: string;
  badge?: string;
  showFilmGrain?: boolean;
  showDust?: boolean;
  showCornerBrackets?: boolean;
  cameraShake?: boolean;
  brightness?: number;
  contrast?: number;
}

export interface DocumentaryScene {
  id: string;
  type: "ken-burns" | "document-reveal" | "tactical-map" | "stat-counter" | "video-clip" | "channel-outro" | "heraldic-surgery" | "image-morph";
  mediaSrc: string;
  durationInSeconds: number;
  startInSeconds?: number;
  voiceoverAudioSrc?: string;
  sfxSrc?: string;
  sfxVolume?: number;
  cameraDirection?: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "snap-zoom" | "dramatic-push" | "tilt-down";
  transitionType?: "fade" | "shutter-flash" | "whip-pan" | "cross-dissolve";
  headline?: string;
  subheadline?: string;
  badge?: string;
  notes?: string;
  beforeSrc?: string;
  afterSrc?: string;
}

export interface VoiceoverTrack {
  id: string;
  src: string;
  startInSeconds: number;
  durationInSeconds: number;
  volume?: number;
}

export interface WordTiming {
  word: string;
  start: number;
  end: number;
}

export interface CaptionChunk {
  text: string;
  start: number;
  end: number;
  words: WordTiming[];
}

export interface ActData {
  name: string;
  duration: number;
  words: WordTiming[];
  chunks: CaptionChunk[];
}

export interface ActTimeline {
  id: string;
  globalStart: number;
  globalEnd: number;
}

export interface EpisodeConfig {
  id: string;
  title: string;
  channelSlug: string;
  language: SupportedLanguage;
  backgroundMusicSrc?: string;
  backgroundMusicVolume?: number;
  outroMusicSrc?: string;
  outroMusicStartSec?: number;
  voiceovers?: VoiceoverTrack[];
  scenes: DocumentaryScene[];
  captions?: Record<string, ActData>;
  actTimelines?: ActTimeline[];
  introProps?: ChannelIntroProps;
}

