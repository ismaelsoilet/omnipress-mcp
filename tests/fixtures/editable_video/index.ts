// Golden fixture for generated editable episode shape. Typechecked in CI.
import { registerRoot } from "remotion";
import { createEpisodeRoot } from "../../../src/video/public";
import { Episode } from "./Episode";

registerRoot(
  createEpisodeRoot({
    id: "Episode-fixture-16x9",
    component: Episode,
    width: 1920,
    height: 1080,
    fps: 30,
    durationInFrames: 570,
    defaultProps: {},
  }),
);
