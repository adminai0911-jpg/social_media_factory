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

const GREEN_WORDS = ["MONEY", "HACK", "SECRET", "PROFIT", "WEALTH", "1%", "SUCCESS", "RICH", "GROW", "POWER"];
const RED_WORDS = ["DEATH", "WARNING", "DANGER", "FAKE", "SCAM", "FAIL", "ILLEGAL", "HIJACK", "STOP", "TRAP"];

export const MainVideo: React.FC<{
  title: string;
  script_text: string;
  timings: any[];
  totalDurationInSeconds: number;
}> = ({ title, timings, totalDurationInSeconds }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Find the exact word currently spoken
  const currentWordIndex = timings.findIndex(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.1
  );
  const currentWord = timings[currentWordIndex];

  // ==========================================
  // 1. THE 3-SECOND MUTATOR (Environments)
  // ==========================================
  const environmentIndex = Math.floor(frame / (fps * 3)) % 3;

  // ==========================================
  // 2. CASINO TENSION COUNTERS
  // ==========================================
  // Number that races to 99 and gets stuck vibrating
  const brainHackedPercentage = Math.min(99, Math.floor(interpolate(frame, [0, fps * totalDurationInSeconds * 0.9], [0, 100])));
  const isStalled = brainHackedPercentage === 99;
  const shakeCounterX = isStalled ? Math.sin(frame * 5) * 10 : 0;
  const shakeCounterY = isStalled ? Math.cos(frame * 7) * 10 : 0;

  // Progress Bar near-miss
  const progressWidth = interpolate(frame, [0, fps * totalDurationInSeconds * 0.9], [0, 99], { extrapolateRight: "clamp" });

  // Strobe lighting (horror/alert flashes)
  const isStrobe = currentWord && RED_WORDS.some(rw => currentWord.word.toUpperCase().includes(rw)) && frame % 4 < 2;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", filter: isStrobe ? "invert(100%)" : "none" }}>
      <Audio src={staticFile("audio.mp3")} volume={1.8} />

      {/* ========================================== */}
      {/* BACKGROUND ENVIRONMENTS (Mutates every 3s) */}
      {/* ========================================== */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        {environmentIndex === 0 && (
          // ENV 0: HIGH-SPEED INFINITE TUNNEL (Adrenaline)
          <div style={{ width: "100%", height: "100%", perspective: "800px", backgroundColor: "#050510", display: "flex", justifyContent: "center", alignItems: "center" }}>
            <div
              style={{
                position: "absolute",
                width: "400%", height: "400%",
                background: "conic-gradient(from 0deg, #ff0055, #000, #00f0ff, #000, #ff0055)",
                transform: `rotate(${frame * 2}deg) translateZ(-500px)`,
                opacity: 0.5,
              }}
            />
            {/* Hypnotic zooming rings */}
            {Array.from({ length: 15 }).map((_, i) => {
              const z = ((i * 100) + frame * 30) % 1500;
              return (
                <div key={i} style={{
                  position: "absolute",
                  width: "200px", height: "200px",
                  border: `10px solid hsl(${(frame + i * 20) % 360}, 100%, 50%)`,
                  borderRadius: "50%",
                  transform: `translateZ(${z}px)`,
                  boxShadow: "0 0 50px rgba(255,255,255,0.5)",
                }} />
              );
            })}
          </div>
        )}

        {environmentIndex === 1 && (
          // ENV 1: SATISFYING LIQUID SLIME (ASMR Eye-Candy)
          <div style={{ width: "100%", height: "100%", backgroundColor: "#111" }}>
            <svg style={{ position: "absolute", width: 0, height: 0 }}>
              <defs>
                <filter id="slime-goo">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="30" result="blur" />
                  <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 25 -10" result="goo" />
                  <feBlend in="SourceGraphic" in2="goo" />
                </filter>
              </defs>
            </svg>
            <div style={{ width: "100%", height: "100%", filter: "url(#slime-goo)", position: "relative" }}>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} style={{
                  position: "absolute",
                  width: 300, height: 300,
                  backgroundColor: `hsl(${(frame * 2 + i * 40) % 360}, 100%, 60%)`,
                  borderRadius: "50%",
                  left: `${50 + Math.sin(frame / 20 + i) * 30}%`,
                  top: `${50 + Math.cos(frame / 15 + i * 2) * 40}%`,
                  transform: "translate(-50%, -50%)",
                }} />
              ))}
            </div>
          </div>
        )}

        {environmentIndex === 2 && (
          // ENV 2: AGGRESSIVE KINETIC LASERS
          <div style={{ width: "100%", height: "100%", backgroundColor: "#000", display: "flex", flexDirection: "column", justifyContent: "space-around" }}>
            {Array.from({ length: 20 }).map((_, i) => (
              <div key={i} style={{
                width: "100%", height: "3%",
                backgroundColor: i % 2 === 0 ? "#FF0000" : "#FFF",
                transform: `translateX(${Math.sin(frame / 5 + i) * 50}px)`,
                boxShadow: "0 0 20px #FF0000",
              }} />
            ))}
          </div>
        )}
      </AbsoluteFill>

      {/* ========================================== */}
      {/* SLAMMING MOTION BLUR TYPOGRAPHY */}
      {/* ========================================== */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 100 }}>
        {currentWord && (() => {
          const upperWord = currentWord.word.toUpperCase().replace(/[^A-Z0-9%]/g, '');
          let color = "#FFFD03"; 
          if (GREEN_WORDS.some(gw => upperWord.includes(gw))) color = "#00FF00";
          if (RED_WORDS.some(rw => upperWord.includes(rw))) color = "#FF0000";

          const timeSinceWordStart = currentTime - currentWord.start;
          
          // Slam effect: Scales from 4.0 to 1.0 extremely fast, with blur clearing up
          const scale = interpolate(timeSinceWordStart, [0, 0.1], [4, 1.1], { extrapolateRight: "clamp" });
          const blur = interpolate(timeSinceWordStart, [0, 0.05], [20, 0], { extrapolateRight: "clamp" });
          const rotate = interpolate(timeSinceWordStart, [0, 0.1], [Math.random() * 20 - 10, 0], { extrapolateRight: "clamp" });

          return (
            <div
              style={{
                fontSize: "180px",
                fontFamily: "Arial Black, Impact, sans-serif",
                color: color,
                textAlign: "center",
                WebkitTextStroke: "12px black",
                textShadow: "20px 20px 0px rgba(0,0,0,0.8)",
                lineHeight: 1.0,
                transform: `scale(${scale}) rotate(${rotate}deg)`,
                filter: `blur(${blur}px)`,
                width: "90%",
              }}
            >
              {currentWord.word.toUpperCase()}
            </div>
          );
        })()}
      </AbsoluteFill>

      {/* ========================================== */}
      {/* CASINO HUD & TENSION ELEMENTS */}
      {/* ========================================== */}
      
      {/* Brain Capacity Counter */}
      <div style={{
        position: "absolute", top: 80, right: 40,
        color: isStalled ? "#FF0000" : "#00FFFF",
        fontSize: "60px", fontFamily: "monospace", fontWeight: "bold",
        textShadow: "0 0 20px currentColor",
        transform: `translate(${shakeCounterX}px, ${shakeCounterY}px)`,
        zIndex: 150
      }}>
        SYNC: {brainHackedPercentage}%
      </div>

      {/* 99% Near Miss Progress Bar */}
      <div style={{ position: "absolute", bottom: 60, left: "5%", width: "90%", height: 20, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 10, zIndex: 200 }}>
        <div style={{
          height: "100%", width: `${progressWidth}%`,
          backgroundColor: isStalled && frame % 10 < 5 ? "#FF0000" : "#FFF",
          borderRadius: 10,
          boxShadow: isStalled ? "0 0 30px #FF0000" : "0 0 10px #FFF",
          transition: "width 0.1s linear"
        }} />
        {isStalled && (
          <div style={{ position: "absolute", top: -80, right: 0, color: "#FFF", fontSize: "50px", fontWeight: "bold", color: "#FF0000" }}>
            WAIT FOR IT...
          </div>
        )}
      </div>

    </AbsoluteFill>
  );
};
