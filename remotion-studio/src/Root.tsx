import { Composition } from "remotion";
import { MainVideo } from "./MainVideo";

const defaultProps = {
  script: {
    style_seed: 1,
    emojis: ["👀", "🔥", "💀"]
  },
  voice: "Adam",
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
        durationInFrames={Math.ceil(15.0 * 30)}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
        calculateMetadata={async ({ props }) => {
          const duration = props.total_duration || 30.0;
          return {
            durationInFrames: Math.ceil(duration * 30),
            props
          };
        }}
      />
    </>
  );
};
