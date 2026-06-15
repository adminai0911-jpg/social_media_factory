import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  OffthreadVideo,
  random,
  spring,
} from "remotion";
import React from "react";

const RED_WORDS = ["WAKE", "SIMULATION", "SHADOWS", "TRAP", "LYING", "FAKE", "DREAM", "FEAR", "PANIC", "NOW", "LIES", "BREAK"];

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

  // The 3 Phases of the Contrast Trap
  const phase = currentTime < 10 ? 1 : currentTime < 20 ? 2 : 3;

  // Phase 2 & 3 Adrenaline Triggers
  let isImpact = false;
  let shakeAmount = 0;
  if (currentWord && phase >= 2) {
    const upperWord = currentWord.word.toUpperCase().replace(/[^A-Z0-9%]/g, '');
    if (RED_WORDS.some(rw => upperWord.includes(rw))) {
      const timeSinceStart = currentTime - currentWord.start;
      if (timeSinceStart < 0.1) isImpact = true; 
      if (timeSinceStart < 0.3) shakeAmount = phase === 3 ? 40 : 20; 
    }
  }

  const shakeX = shakeAmount > 0 ? (random(frame) - 0.5) * shakeAmount : 0;
  const shakeY = shakeAmount > 0 ? (random(frame + 1) - 0.5) * shakeAmount : 0;

  // Heartbeat changes based on Phase
  const heartRate = phase === 1 ? 60 : phase === 2 ? 120 : 180;
  const beatInterval = (60 / heartRate) * fps;
  const isBeat = frame % beatInterval < (phase === 1 ? 5 : 3);

  // V5 Gamification (Slot Machine Counter)
  const lieCounter = Math.floor(interpolate(frame, [fps*20, fps*30], [0, 9842], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));

  return (
    <AbsoluteFill style={{ 
      backgroundColor: phase === 1 ? "#050510" : isImpact ? "#FFF" : "#000",
      transform: `translate(${shakeX}px, ${shakeY}px)`,
      filter: isImpact ? "invert(1)" : "none",
    }}>
      
      {/* 1. AUDIO LAYER */}
      {/* Phase 1: Clean. Phase 2/3: Schizophrenic whispers fade in */}
      <Audio src={staticFile("audio.mp3")} volume={1.8} />
      {phase >= 2 && <Audio src={staticFile("audio.mp3")} volume={0.8} startFrom={5} />}
      {phase === 3 && <Audio src={staticFile("audio.mp3")} volume={0.8} startFrom={12} />}
      
      {isBeat && <AbsoluteFill style={{ backgroundColor: phase === 1 ? "rgba(255, 180, 50, 0.05)" : "rgba(255, 0, 0, 0.2)", zIndex: 10, mixBlendMode: "screen" }} />}

      {/* 2. DYNAMIC BACKGROUND (Phase 1 vs Phase 2/3) */}
      <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", overflow: "hidden", perspective: "800px" }}>
        
        {phase === 1 && (
           // V12: Euphoric Cosmic Glow
           <div style={{ position: "absolute", width: "200%", height: "200%", background: "radial-gradient(circle at center, #1a0b2e 0%, #050510 50%, #000 100%)" }} />
        )}

        {phase >= 2 && (
           // V6: 4D Fractal Tunnel (Dark, aggressive)
           Array.from({ length: 25 }).map((_, i) => {
             const zPos = ((i * 400) + frame * 50) % 10000 - 5000;
             return (
               <div key={`ring-${i}`} style={{
                 position: "absolute", width: "200px", height: "200px",
                 border: `3px solid hsl(${(frame * 0.2 + i * 14) % 360}, 100%, 50%)`,
                 borderRadius: "50%",
                 transform: `translateZ(${zPos}px) rotate(${frame * (i % 2 === 0 ? 1 : -1)}deg)`,
                 opacity: interpolate(zPos, [-5000, 0, 5000], [0, 0.8, 0]),
               }} />
             );
           })
        )}
      </AbsoluteFill>

      {/* 3. THE VISUAL CORE (Evolving) */}
      <AbsoluteFill style={{ perspective: "1000px", zIndex: 50, justifyContent: "center", alignItems: "center" }}>
        
        {phase === 1 && (
           // V9: Clean Holographic Sand
           <div style={{
             position: "absolute", top: "15%", width: "86%", height: "70%",
             transform: `translateY(${Math.sin(frame/60)*10}px)`, 
             boxShadow: "0 0 150px rgba(255, 200, 100, 0.2)",
             border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: "30px", overflow: "hidden",
           }}>
              <OffthreadVideo src={staticFile("sand.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.1)", filter: "contrast(1.1) saturate(1.2)" }} />
           </div>
        )}

        {phase === 2 && (
           // V7: Split Screen (GTA + Sand) - High Stakes
           <AbsoluteFill style={{ display: "flex", flexDirection: "column" }}>
             <div style={{ flex: 1, overflow: "hidden", borderBottom: "5px solid cyan" }}>
                <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.2) scaleX(-1)" }} />
             </div>
             <div style={{ flex: 1, overflow: "hidden", borderTop: "5px solid magenta" }}>
                <OffthreadVideo src={staticFile("sand.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.2)" }} />
             </div>
           </AbsoluteFill>
        )}

        {phase === 3 && (
           // V8: Shattered Reality + V5 Slot Machine
           <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} style={{
                  position: "absolute", width: "40%", height: "40%",
                  clipPath: `polygon(${random(i)*100}% ${random(i+1)*100}%, ${random(i+2)*100}% ${random(i+3)*100}%, ${random(i+4)*100}% ${random(i+5)*100}%)`,
                  transform: `translateZ(${(i*100 + frame*10)%1000 - 500}px) rotate(${frame + i*20}deg)`,
                  opacity: 0.8
                }}>
                   <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "250%", height: "250%", objectFit: "cover" }} />
                </div>
              ))}
              
              {/* V5: The Slot Machine Dopamine Trap */}
              <div style={{
                position: "absolute", top: "10%", background: "rgba(0,0,0,0.8)", padding: "20px",
                border: "4px solid red", borderRadius: "10px", color: "red",
                fontFamily: "monospace", fontSize: "60px", fontWeight: "bold",
                textShadow: "0 0 20px red", zIndex: 1000
              }}>
                LIES DETECTED:<br/>
                {lieCounter.toString().padStart(5, '0')}
              </div>
           </AbsoluteFill>
        )}
      </AbsoluteFill>

      {/* 4. TYPOGRAPHY */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 100, pointerEvents: "none" }}>
        {currentWord && (() => {
          const timeSinceWordStart = currentTime - currentWord.start;
          
          if (phase === 1) {
            // V12 Euphoric Typography
            const yOffset = spring({ fps, frame: frame - Math.round(currentWord.start * fps), config: { damping: 15, mass: 1, stiffness: 100 }, from: 50, to: 0 });
            return (
              <div style={{
                  fontSize: "140px", fontFamily: "'Playfair Display', serif", color: "#FFF", textAlign: "center",
                  textShadow: "0 0 40px rgba(255,255,255,0.8)", transform: `translateY(${yOffset}px)`, width: "80%"
                }}>
                {currentWord.word}
              </div>
            );
          } else {
            // V10 Aggressive Typography
            const scale = interpolate(timeSinceWordStart, [0, 0.2], [1.8, 1.2], { extrapolateRight: "clamp" });
            const color = RED_WORDS.some(rw => currentWord.word.toUpperCase().includes(rw)) ? "#FF0000" : "#FFF";
            return (
              <div style={{
                  fontSize: "180px", fontFamily: "Impact, sans-serif", fontWeight: "bold", color: color,
                  textAlign: "center", WebkitTextStroke: "6px black", textShadow: color === "#FF0000" ? "0 0 50px red" : "0 0 30px black",
                  transform: `scale(${scale})`, width: "90%"
                }}>
                {currentWord.word.toUpperCase()}
              </div>
            );
          }
        })()}
      </AbsoluteFill>

      {/* 5. V12/V10 SUBLIMINAL SHARE */}
      {frame > fps * 25 && frame % 15 === 0 && (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 500, backgroundColor: "#FFF", mixBlendMode: "difference" }}>
          <div style={{ fontSize: "200px", color: "#FFF", fontWeight: "bold", fontFamily: "Impact" }}>SHARE</div>
        </AbsoluteFill>
      )}

    </AbsoluteFill>
  );
};
