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
  direction?: "zoom-in" | "zoom-out" | "pan-left" | "pan-right";
  headline?: string;
  caption?: string;
  badge?: string;
  showFilmGrain?: boolean;
}

export interface DocumentaryScene {
  id: string;
  type: "ken-burns" | "document-reveal" | "tactical-map" | "stat-counter" | "video-clip";
  mediaSrc: string;
  durationInSeconds: number;
  voiceoverAudioSrc?: string;
  headline?: string;
  subheadline?: string;
  badge?: string;
  notes?: string;
}

export interface EpisodeConfig {
  id: string;
  title: string;
  channelSlug: string;
  language: SupportedLanguage;
  backgroundMusicSrc?: string;
  backgroundMusicVolume?: number;
  scenes: DocumentaryScene[];
}
