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
  Sequence
} from "remotion";
import React from "react";

const FONTS = [
  "Impact, sans-serif",
  "'Arial Black', sans-serif",
  "'Bebas Neue', cursive",
  "system-ui, sans-serif"
];

const COLORS = [
  ["#FF0055", "#00FFCC", "#7700FF"], // Cyberpunk Neon
  ["#FFEA00", "#FF00AA", "#00A1FF"], // Vibrant Pop
  ["#00FF66", "#0066FF", "#FF00FF"], // Digital Matrix
  ["#FF3366", "#FF9933", "#00FFCC"], // Tropical Sunset
  ["#FF00CC", "#3300FF", "#00FFFF"]  // Deep Synthwave
];

const BASE_RED_WORDS = ["WAKE", "SIMULATION", "SHADOWS", "TRAP", "LYING", "FAKE", "DREAM", "FEAR", "PANIC", "NOW", "LIES", "BREAK", "KYA"];

export const MainVideo: React.FC<{
  script: any;
  timings: any[];
  audio_offsets: number[];
  total_duration: number;
}> = ({ script, timings, audio_offsets, total_duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  if (!script || !audio_offsets || audio_offsets.length < 5) return null;

  // Data from Python
  const styleSeed = script.style_seed || 1;
  const emojis = script.emojis || ["👀", "🔥", "💀"];
  const dynamicRedWord = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9%]/g, '') : "WARNING";
  const subliminalWord = script.subliminal_flash_word ? script.subliminal_flash_word.toUpperCase() : "WAKE UP";
  const RED_WORDS = [...BASE_RED_WORDS, dynamicRedWord];
  const serotoninTarget = script.serotonin_payoff_number || 47212;
  
  const font = FONTS[styleSeed % FONTS.length];
  const colorPalette = COLORS[styleSeed % COLORS.length];

  // Mathematical Timestamps
  const p1_start = 0;
  const p2_start = audio_offsets[1];
  const p3_start = audio_offsets[2];
  const p4_start = audio_offsets[3];
  const p5_start = audio_offsets[4];

  // Current Math Phase
  let phase = 1;
  if (currentTime >= p2_start && currentTime < p3_start) phase = 2;
  else if (currentTime >= p3_start && currentTime < p4_start) phase = 3;
  else if (currentTime >= p4_start && currentTime < p5_start) phase = 4;
  else if (currentTime >= p5_start) phase = 5;

  // Word Timing Tracking
  const currentWordIndex = timings.findIndex(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.1
  );
  const currentWord = timings[currentWordIndex];

  // Effects Logic
  const isPhase3Glitch = phase === 3 && frame > 0 && frame % 60 === 0;
  const isVHSGlitch = frame % 150 > 140; 
  const subliminalFrame = Math.round(p3_start * fps) + 90; 
  const isSubliminal = frame === subliminalFrame; 
  const shatterSnapActive = phase === 4 && frame < Math.round(p4_start * fps) + 15; 

  // Red Box Word Detection
  let isRedBox = false;
  if (currentWord) {
    const upperWord = currentWord.word.toUpperCase().replace(/[^A-Z0-9%]/g, '');
    if (RED_WORDS.some(rw => upperWord.includes(rw))) {
       isRedBox = true;
    }
  }

  // Camera Shake
  let shakeAmount = 0;
  if (isPhase3Glitch) shakeAmount = 20;
  if (isRedBox) shakeAmount = 30;
  if (shatterSnapActive) shakeAmount = 50;
  const shakeX = shakeAmount > 0 ? (random(frame) - 0.5) * shakeAmount : 0;
  const shakeY = shakeAmount > 0 ? (random(frame + 1) - 0.5) * shakeAmount : 0;

  // Tension Meter Progress Math
  const tensionProgress = phase < 4 ? interpolate(frame, [0, p4_start * fps], [0, 100], {extrapolateRight: "clamp"}) : 100;
  const isTensionCritical = tensionProgress > 95;

  // Liquid Mixing Background Math (Bright & HD)
  const bgAngle = (frame * 0.5) % 360;
  const orb1X = 50 + Math.sin(frame / 40) * 30;
  const orb1Y = 50 + Math.cos(frame / 30) * 30;
  const orb2X = 50 + Math.cos(frame / 35) * 40;
  const orb2Y = 50 + Math.sin(frame / 45) * 40;

  return (
    <AbsoluteFill style={{ 
      backgroundColor: colorPalette[0], // Bright base instead of black
      transform: `translate(${shakeX}px, ${shakeY}px)`,
    }}>
      
      {/* 1. AUDIO LAYER */}
      <Sequence from={0}><Audio src={staticFile(`v31_audio_0.mp3`)} volume={1.5} /></Sequence>
      {audio_offsets[1] && <Sequence from={Math.round(p2_start * fps)}><Audio src={staticFile(`v31_audio_1.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[2] && <Sequence from={Math.round(p3_start * fps)}><Audio src={staticFile(`v31_audio_2.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[3] && <Sequence from={Math.round(p4_start * fps)}><Audio src={staticFile(`v31_audio_3.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[4] && <Sequence from={Math.round(p5_start * fps)}><Audio src={staticFile(`v31_audio_4.mp3`)} volume={1.5} /></Sequence>}
      
      {Array.from({length: 20}).map((_, i) => {
          const glitchFrame = Math.round(p3_start * fps) + (i * 60);
          if (glitchFrame < p4_start * fps) {
             return <Sequence key={`ding-${i}`} from={glitchFrame}><Audio src={staticFile("ding.wav")} volume={0.8} /></Sequence>
          }
          return null;
      })}
      {audio_offsets[2] && <Sequence from={Math.round(p3_start * fps)}><Audio src={staticFile("riser.wav")} volume={0.5} /></Sequence>}
      {audio_offsets[3] && <Sequence from={Math.round(p4_start * fps)}><Audio src={staticFile("impact.wav")} volume={2} /></Sequence>}

      {/* 2. THE HD LIGHT COLOR BLENDING BACKGROUND (V23 Style) */}
      <AbsoluteFill style={{ 
          zIndex: 0, 
          background: `linear-gradient(${bgAngle}deg, ${colorPalette[0]}, ${colorPalette[1]}, ${colorPalette[2]})`,
          overflow: "hidden" 
      }}>
         <div style={{ position:"absolute", width: "150%", height: "150%", top: "-25%", left: "-25%", filter: "blur(60px)"}}>
            <div style={{ position:"absolute", left: `${orb1X}%`, top: `${orb1Y}%`, width: "800px", height: "800px", borderRadius: "50%", background: colorPalette[1], opacity: 0.8, transform: "translate(-50%, -50%)", mixBlendMode: "screen" }} />
            <div style={{ position:"absolute", left: `${orb2X}%`, top: `${orb2Y}%`, width: "900px", height: "900px", borderRadius: "50%", background: colorPalette[2], opacity: 0.8, transform: "translate(-50%, -50%)", mixBlendMode: "screen" }} />
         </div>
      </AbsoluteFill>


      {/* 3. THE VISUAL CORE */}
      <AbsoluteFill style={{ zIndex: 10 }}>
        {/* Phase 1 & 2: Floating Box */}
        <Sequence from={0} durationInFrames={Math.round(p3_start * fps)}>
           <div style={{
             position: "absolute", top: "25%", left: "5%", width: "90%", height: "50%",
             transform: `translateY(${Math.sin(frame / 20) * 20}px)`, 
             boxShadow: `0 30px 80px rgba(0,0,0,0.5), 0 0 100px ${colorPalette[1]}`, 
             border: `6px solid white`, borderRadius: "30px", overflow: "hidden",
           }}>
              <OffthreadVideo src={staticFile(styleSeed % 2 === 0 ? "gta.mp4" : "sand.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
           </div>
        </Sequence>

        {/* Phase 3: SMOOTH SPLIT SCREEN */}
        <Sequence from={Math.round(p3_start * fps)} durationInFrames={Math.round((p4_start - p3_start) * fps)}>
           <AbsoluteFill style={{ display: "flex", flexDirection: "column", padding: "20px", gap: "20px" }}>
             <div style={{ flex: 1, overflow: "hidden", borderRadius: "30px", border: `6px solid ${colorPalette[0]}`, boxShadow: `0 0 50px ${colorPalette[0]}` }}>
                <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)" }} />
             </div>
             <div style={{ flex: 1, overflow: "hidden", borderRadius: "30px", border: `6px solid ${colorPalette[1]}`, boxShadow: `0 0 50px ${colorPalette[1]}` }}>
                <OffthreadVideo src={staticFile("sand.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
             </div>
           </AbsoluteFill>
        </Sequence>

        {/* Phase 4 & 5: THE JACKPOT CLIMAX */}
        <Sequence from={Math.round(p4_start * fps)}>
           {shatterSnapActive ? (
              <AbsoluteFill style={{ flexWrap: "wrap", display: "flex", flexDirection: "row" }}>
                 {Array.from({length: 8}).map((_, i) => (
                    <div key={i} style={{
                      width: "50%", height: "25%", overflow: "hidden",
                      transform: `scale(${1 + random(i)*0.2}) rotate(${(random(i)-0.5)*20}deg) translate(${(random(i)-0.5)*100}px, ${(random(i)-0.5)*100}px)`,
                      border: `5px solid ${colorPalette[i%3]}`,
                      filter: `hue-rotate(${i * 45}deg)`
                    }}>
                      <OffthreadVideo src={staticFile(styleSeed % 2 === 0 ? "sand.mp4" : "gta.mp4")} style={{ width: "200%", height: "400%", objectFit: "cover", transform: `translate(-${(i%2)*50}%, -${Math.floor(i/2)*25}%)` }} />
                    </div>
                 ))}
              </AbsoluteFill>
           ) : (
              <AbsoluteFill>
                 <div style={{ position: "absolute", width: "100%", height: "100%", background: `repeating-linear-gradient(0deg, transparent, transparent 40px, ${colorPalette[0]} 40px, ${colorPalette[0]} 45px)`, opacity: 0.3, transform: `translateY(${(frame*5)%45}px)` }} />
                 <div style={{
                    position: "absolute", top: "25%", left: "10%", width: "80%", height: "50%",
                    transform: `scale(${spring({fps, frame: frame - (Math.round(p4_start*fps)+15), config: {damping: 12}})})`,
                    boxShadow: `0 0 150px ${colorPalette[1]}`, border: `10px solid white`, borderRadius: "40px", overflow: "hidden",
                  }}>
                     <OffthreadVideo src={staticFile(styleSeed % 2 === 0 ? "sand.mp4" : "gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.5)" }} />
                 </div>
                 <div style={{ position: "absolute", bottom: "5%", width: "90%", left: "5%", background: "rgba(0,0,0,0.8)", border: `6px solid ${colorPalette[2]}`, padding: "20px", textAlign: "center", borderRadius: "20px" }}>
                     <h1 style={{ margin: 0, color: colorPalette[1], fontSize: "80px", fontFamily: "monospace", textShadow: `0 0 40px ${colorPalette[1]}` }}>PAYOUT: {serotoninTarget.toLocaleString()}</h1>
                 </div>
              </AbsoluteFill>
           )}
        </Sequence>
      </AbsoluteFill>

      {/* 4. RESTORED FLASHING RED BOX (From V23) */}
      {(phase === 2 || phase === 3) && (
         <AbsoluteFill style={{ pointerEvents: "none", zIndex: 150 }}>
            <div style={{ 
                position: "absolute", top: "5%", left: "5%", width: "90%", 
                background: frame % 10 < 5 ? "#FF0044" : "transparent",
                border: `6px solid ${frame % 10 < 5 ? "white" : "#FF0044"}`,
                color: frame % 10 < 5 ? "white" : "#FF0044",
                padding: "15px", textAlign: "center",
                fontFamily: "monospace", fontSize: "50px", fontWeight: "bold",
                boxShadow: frame % 10 < 5 ? "0 0 50px red" : "none",
                borderRadius: "15px"
            }}>
                ⚠️ NEURAL LINK ACTIVE
            </div>
         </AbsoluteFill>
      )}

      {/* 5. GAMIFICATION DOPAMINE COUNTER (Fixed black smudge!) */}
      <Sequence from={Math.round(p2_start * fps)} durationInFrames={Math.round((p4_start - p2_start) * fps)}>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 150, pointerEvents: "none" }}>
          {/* Removed the blur filter that caused the smudge */}
          <div style={{
              background: "rgba(0,0,0,0.6)", padding: "20px 40px",
              border: `4px solid ${colorPalette[0]}`, borderRadius: "30px", color: "white",
              fontFamily: "monospace", fontSize: "70px", fontWeight: "bold",
              textShadow: `0 0 20px ${colorPalette[0]}`,
              transform: `translateY(300px)` // Moved down so it doesn't block center
          }}>
              {phase === 2 ? "SCANNING..." : Math.floor(interpolate(frame, [p3_start * fps, p4_start * fps], [0, serotoninTarget], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })).toLocaleString()}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* 6. DYNAMIC 4D EMOJIS */}
      <AbsoluteFill style={{ zIndex: 200, pointerEvents: "none" }}>
        {emojis.map((emoji: string, i: number) => {
          const spawnTime = p3_start + (i * 3);
          const spawnFrame = Math.round(spawnTime * fps);
          if (frame < spawnFrame || frame >= spawnFrame + fps * 2) return null;
          return (
            <div key={i} style={{
              position: "absolute", left: `${30 + (i * 20)}%`, top: "50%", fontSize: "150px",
              transform: `scale(${spring({ fps, frame: frame - spawnFrame, config: { damping: 10 } })}) translateY(${interpolate(frame - spawnFrame, [0, fps * 2], [0, -400])}px)`,
              opacity: interpolate(frame - spawnFrame, [0, fps*1.5, fps*2], [1, 1, 0])
            }}>
              {emoji}
            </div>
          );
        })}
      </AbsoluteFill>

      {/* 7. 4D CAPTIONS ENGINE (Crazy Animations, Reduced Size) */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 300, pointerEvents: "none" }}>
        {currentWord && (() => {
          const timeSinceWordStart = currentTime - currentWord.start;
          const animStyle = currentWordIndex % 6; // 6 Different 4D animation styles
          
          let transformStr = "";
          let opacityVal = 1;

          // 4D Animations Logic
          if (animStyle === 0) {
            // Zoom In
            transformStr = `scale(${spring({ fps, frame: frame - Math.round(currentWord.start * fps), config: { damping: 12 } })})`;
          } else if (animStyle === 1) {
            // Floating / Weaving
            transformStr = `translate(${Math.sin(frame)*20}px, ${Math.cos(frame)*20}px) scale(1.1)`;
          } else if (animStyle === 2) {
            // Flashing
            opacityVal = frame % 4 < 2 ? 1 : 0;
            transformStr = `scale(1.2)`;
          } else if (animStyle === 3) {
            // 3D Flip
            const rotX = interpolate(timeSinceWordStart, [0, 0.2], [-90, 0], { extrapolateRight: "clamp" });
            transformStr = `perspective(500px) rotateX(${rotX}deg) scale(1.1)`;
          } else if (animStyle === 4) {
            // Zoom Out
            const s = interpolate(timeSinceWordStart, [0, 0.2], [2, 1], { extrapolateRight: "clamp" });
            transformStr = `scale(${s})`;
          } else {
            // Elastic Pop
            transformStr = `scale(${spring({ fps, frame: frame - Math.round(currentWord.start * fps), config: { tension: 300, friction: 10 } })}) rotate(${(currentWordIndex % 2 === 0 ? 1 : -1) * 10}deg)`;
          }

          const glitchShadow = isVHSGlitch ? "10px 0 red, -10px 0 cyan" : `0 0 30px black`;
          
          if (isRedBox) {
            return (
              <div style={{
                  background: "#FF00AA", padding: "10px 40px", border: "6px solid white",
                  fontSize: "80px", fontFamily: font, fontWeight: "900", color: "#FFF",
                  textAlign: "center", transform: transformStr, opacity: opacityVal,
                  boxShadow: "0 0 80px #FF00AA", borderRadius: "15px",
                  maxWidth: "85%", wordWrap: "break-word", lineHeight: "1.1"
                }}>
                {currentWord.word.toUpperCase()}
              </div>
            );
          } else {
            return (
              <div style={{
                  fontSize: "75px", fontFamily: font, fontWeight: "900", 
                  color: colorPalette[currentWordIndex % colorPalette.length], 
                  textAlign: "center", WebkitTextStroke: "3px white", 
                  textShadow: glitchShadow,
                  transform: transformStr, opacity: opacityVal,
                  maxWidth: "85%", wordWrap: "break-word", lineHeight: "1.1",
                  background: "rgba(0,0,0,0.4)", padding: "10px 20px", borderRadius: "20px"
                }}>
                {currentWord.word.toUpperCase()}
              </div>
            );
          }
        })()}
      </AbsoluteFill>

      {/* 8. THE ADRENALINE COVER GRAPHIC (FIXED) */}
      {frame === 0 && (
        <AbsoluteFill style={{ zIndex: 1000 }}>
             <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
             <div style={{ position: "absolute", width: "100%", height: "100%", background: `linear-gradient(45deg, ${colorPalette[0]}88, ${colorPalette[1]}88)` }} />
             <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
                 <div style={{
                      background: "#FF00AA", padding: "20px 40px", border: "10px solid white",
                      fontSize: "120px", fontFamily: "Impact", fontWeight: "900", color: "#FFF", // Reduced font size to 120px!
                      textAlign: "center", boxShadow: "0 0 100px #000",
                      maxWidth: "90%", wordWrap: "break-word"
                    }}>
                    {dynamicRedWord || "SIMULATION"}
                 </div>
             </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* 9. THE LOOP MIRROR */}
      {phase === 5 && (
         <AbsoluteFill style={{ 
            backgroundColor: "black", opacity: interpolate(frame, [p5_start * fps, total_duration * fps], [0, 1], {extrapolateRight:"clamp"}), zIndex: 1000 
         }} />
      )}

    </AbsoluteFill>
  );
};

