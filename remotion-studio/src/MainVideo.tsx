import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import React from "react";

const GREEN_WORDS = ["MONEY", "HACK", "SECRET", "PROFIT", "WEALTH", "1%", "SUCCESS"];
const RED_WORDS = ["DEATH", "WARNING", "DANGER", "FAKE", "SCAM", "FAIL"];

export const MainVideo: React.FC<{
  title: string;
  script_text: string;
  timings: any[];
  totalDurationInSeconds: number;
}> = ({ title, timings, totalDurationInSeconds }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const currentWordIndex = timings.findIndex(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.1
  );
  const currentWord = timings[currentWordIndex];

  // Algorithmic manipulations
  const shakeX = Math.sin(frame * 2.5) * 6;
  const shakeY = Math.cos(frame * 3.5) * 6;
  const zoom = interpolate(frame, [0, fps * totalDurationInSeconds], [1, 1.2]);
  
  // Fake progress bar that stops right before the end
  const progressWidth = interpolate(
    frame,
    [0, fps * totalDurationInSeconds * 0.95, fps * totalDurationInSeconds],
    [0, 95, 95] // Stalls at 95% to keep people waiting
  );

  // Subliminal flash (pattern interrupt) every 3 seconds
  const isFlash = frame % (fps * 3) < 2;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Audio src={staticFile("audio.mp3")} volume={1.5} />
      
      {/* Subliminal Flash Layer */}
      {isFlash && <AbsoluteFill style={{ backgroundColor: "rgba(255, 255, 255, 0.1)", zIndex: 50 }} />}

      <AbsoluteFill
        style={{
          transform: `scale(${zoom}) translate(${shakeX}px, ${shakeY}px)`,
          transformOrigin: "center",
        }}
      >
        {/* --- TOP HALF (Cinematic) --- */}
        <AbsoluteFill style={{ height: "50%", overflow: "hidden", backgroundColor: "#0a0a14" }}>
          <div
            style={{
              position: "absolute",
              width: "150%", height: "150%",
              background: "radial-gradient(circle at center, #2b003a 0%, #000 60%)",
              transform: `rotate(${frame * 0.1}deg)`,
            }}
          />
          {Array.from({ length: 40 }).map((_, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                top: `${Math.random() * 100}%`,
                left: `${(i * 3 + frame * (Math.random() * 0.8)) % 100}%`,
                width: Math.random() * 4 + 1,
                height: Math.random() * 4 + 1,
                backgroundColor: "white",
                borderRadius: "50%",
                opacity: Math.random() * 0.9,
                filter: "blur(1px)",
              }}
            />
          ))}
        </AbsoluteFill>

        {/* --- BOTTOM HALF (Satisfying Logic) --- */}
        <AbsoluteFill style={{ top: "50%", height: "50%", overflow: "hidden", backgroundColor: "#111" }}>
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "space-evenly" }}>
            {Array.from({ length: 25 }).map((_, i) => {
              const h = 200 + Math.sin(frame / 10 + i * 0.4) * 200;
              return (
                <div
                  key={i}
                  style={{
                    width: "3%",
                    height: h,
                    backgroundColor: `hsl(${(frame * 2 + i * 15) % 360}, 100%, 50%)`,
                    borderRadius: 10,
                    boxShadow: "0 0 15px rgba(255,255,255,0.2)",
                  }}
                />
              );
            })}
          </div>
        </AbsoluteFill>

        <div style={{ position: "absolute", top: "50%", left: 0, right: 0, height: 12, backgroundColor: "#fff", transform: "translateY(-50%)", boxShadow: "0px 0px 40px rgba(0,0,0,0.9)" }} />
      </AbsoluteFill>

      {/* --- HORMOZI STYLE CAPTIONS --- */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {currentWord && (() => {
          const upperWord = currentWord.word.toUpperCase().replace(/[^A-Z0-9%]/g, '');
          let color = "#FFFD03"; 
          if (GREEN_WORDS.some(gw => upperWord.includes(gw))) color = "#00FF00";
          if (RED_WORDS.some(rw => upperWord.includes(rw))) color = "#FF0000";

          const timeSinceWordStart = currentTime - currentWord.start;
          const scale = interpolate(timeSinceWordStart, [0, 0.08], [0.3, 1.05], { extrapolateRight: "clamp" });
          const rotate = interpolate(timeSinceWordStart, [0, 0.1], [-6, 3], { extrapolateRight: "clamp" });

          return (
            <div
              style={{
                fontSize: "190px",
                fontFamily: "Arial Black, Impact, sans-serif",
                color: color,
                textAlign: "center",
                WebkitTextStroke: "10px black",
                textShadow: "20px 20px 0px black",
                lineHeight: 1.0,
                transform: `scale(${scale}) rotate(${rotate}deg)`,
                zIndex: 100,
              }}
            >
              {currentWord.word.toUpperCase()}
            </div>
          );
        })()}
      </AbsoluteFill>

      {/* --- FAKE PROGRESS BAR --- */}
      <div
        style={{
          position: "absolute",
          bottom: 20,
          left: "5%",
          width: "90%",
          height: 8,
          backgroundColor: "rgba(255,255,255,0.2)",
          borderRadius: 4,
          zIndex: 200,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progressWidth}%`,
            backgroundColor: "#FF0000",
            borderRadius: 4,
          }}
        />
      </div>

      {/* --- FAKE LIKE HEART (Pops up near the middle to trigger tapping) --- */}
      {frame > fps * (totalDurationInSeconds * 0.4) && frame < fps * (totalDurationInSeconds * 0.45) && (
        <div
          style={{
            position: "absolute",
            right: 40,
            bottom: "40%",
            fontSize: "120px",
            filter: "drop-shadow(0px 0px 20px red)",
            animation: "pulse 0.5s infinite alternate",
            zIndex: 150,
            opacity: interpolate(frame, [fps * (totalDurationInSeconds * 0.4), fps * (totalDurationInSeconds * 0.41)], [0, 1], { extrapolateRight: "clamp" })
          }}
        >
          ❤️
        </div>
      )}
    </AbsoluteFill>
  );
};
