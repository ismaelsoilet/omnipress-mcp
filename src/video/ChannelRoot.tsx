import React from "react";
import { Composition } from "remotion";
import { CoreCompositions } from "./Root";

export interface EpisodeRegistration<
  Props extends Record<string, unknown> = Record<string, unknown>,
> {
  id: string;
  component: React.ComponentType<Props>;
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  defaultProps?: Props;
}

/**
 * Build a Remotion root for a single generated, editable episode.
 *
 * The channel-specific episode TSX lives in
 * channels/<slug>/video/episodes/<episode>/ and is registered through its own
 * entry point. Core compositions stay available for review and comparison.
 */
export const createEpisodeRoot = <
  Props extends Record<string, unknown> = Record<string, unknown>,
>(
  registration: EpisodeRegistration<Props>
): React.FC => {
  const {
    id,
    component,
    width,
    height,
    fps,
    durationInFrames,
    defaultProps,
  } = registration;

  const EpisodeRoot: React.FC = () => {
    return (
      <>
        <CoreCompositions />
        <Composition<any, Props>
          id={id}
          component={component}
          width={width}
          height={height}
          fps={fps}
          durationInFrames={durationInFrames}
          calculateMetadata={({ props }) => ({
            durationInFrames,
            props,
          })}
          defaultProps={defaultProps ?? ({} as Props)}
        />
      </>
    );
  };

  return EpisodeRoot;
};
