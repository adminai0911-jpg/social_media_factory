import { Composition } from "remotion";
import { MainVideo } from "./MainVideo";

const defaultProps = {
  title: "The Simulation",
  script_text: "This fact will mess with your perception of time.",
  timings: [
    { word: "This", start: 0.0, end: 0.3 }
  ],
  totalDurationInSeconds: 15.0
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
          const duration = props.totalDurationInSeconds || 15.0;
          return {
            durationInFrames: Math.ceil(duration * 30),
            props
          };
        }}
      />
    </>
  );
};
