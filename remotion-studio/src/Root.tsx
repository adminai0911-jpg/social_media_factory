import { Composition } from "remotion";
import { MainVideo, ThumbnailCover } from "./MainVideo";
import React from "react";

const defaultProps = {
  script: {
    style_seed: 1,
    emojis: ["👀", "🔥", "💀"],
    red_box_keyword: "LIES",
    subliminal_flash_word: "WAKE UP",
    serotonin_payoff_number: 88319,
    micro_niche: "Test Niche",
    phase_1: "test hook",
    phase_2: "test build",
    phase_3: "test interrupt",
    phase_4: "test payoff",
    phase_5: "test loop",
    caption: "Test caption #viral #trending #fyp #mindset #growth"
  },
  timings: [],
  audio_offsets: [0.0, 5.0, 10.0, 20.0, 25.0],
  total_duration: 30.0
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MainVideo"
        component={MainVideo}
        durationInFrames={Math.ceil(30.0 * 25)}
        fps={25}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
        calculateMetadata={async ({ props }) => {
          const duration = props.total_duration || 30.0;
          return {
            durationInFrames: Math.ceil(duration * 25),
            props
          };
        }}
      />
      <Composition
        id="ThumbnailCover"
        component={ThumbnailCover}
        durationInFrames={1}
        fps={25}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
      <Composition
        id="ThumbnailCover"
        component={ThumbnailCover}
        durationInFrames={1}
        fps={25}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
    </>
  );
};
