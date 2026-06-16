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

// Load HD Hindi-supporting Google Font via @font-face in index.css is not reliable in Remotion.
// Instead we inline a global style element to load from Google Fonts CDN.
const GlobalFontStyle = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@900&family=Bebas+Neue&family=Inter:wght@900&display=swap');
  `}</style>
);

// Hindi-supporting font stack – fallback includes system Hindi fonts
const HINDI_FONT = "'Noto Sans Devanagari', 'Mangal', 'Sanskrit Text', sans-serif";
const IMPACT_FONT = "'Bebas Neue', 'Impact', sans-serif";

const COLORS = [
  ["#FF0055", "#00FFCC", "#7700FF"], // Cyberpunk Neon
  ["#FFEA00", "#FF00AA", "#00A1FF"], // Vibrant Pop
  ["#00FF66", "#0066FF", "#FF00FF"], // Digital Matrix
  ["#FF3366", "#FF9933", "#00FFCC"], // Tropical Sunset
  ["#FF00CC", "#3300FF", "#00FFFF"]  // Deep Synthwave
];

const BASE_RED_WORDS = ["WAKE", "SIMULATION", "SHADOWS", "TRAP", "LYING", "FAKE", "DREAM", "FEAR", "PANIC", "NOW", "LIES", "BREAK", "KYA"];

// Dynamic rotating neural alerts – changes on every run
const NEURAL_ALERTS = [
  { icon: "⚠️", text: "NEURAL LINK ACTIVE" },
  { icon: "🧠", text: "MIND HACK DETECTED" },
  { icon: "🔴", text: "DOPAMINE SPIKE NOW" },
  { icon: "⚡", text: "BRAIN SIGNAL LOCKED" },
  { icon: "🚨", text: "ATTENTION HIJACKED" },
  { icon: "💀", text: "REALITY GLITCHING" },
  { icon: "🔥", text: "ADRENALINE TRIGGER" },
  { icon: "👁️", text: "SUBLIMINAL UPLOAD" },
  { icon: "🌀", text: "HYPNOSIS IN PROGRESS" },
  { icon: "❌", text: "ESCAPE IS IMPOSSIBLE" },
];

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
  
  // Pick a unique neural alert based on styleSeed so it changes each run
  const alertIndex = styleSeed % NEURAL_ALERTS.length;
  const currentAlert = NEURAL_ALERTS[alertIndex];
  
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

  // 8D Stereo Simulation - slow left-right audio panning effect via visual shift indicator
  const stereoPan = Math.sin(frame / (fps * 3)) * 0.5 + 0.5; // 0 to 1 oscillation

  // Liquid Mixing Background Math (Bright & HD)
  const bgAngle = (frame * 0.5) % 360;
  const orb1X = 50 + Math.sin(frame / 40) * 30;
  const orb1Y = 50 + Math.cos(frame / 30) * 30;
  const orb2X = 50 + Math.cos(frame / 35) * 40;
  const orb2Y = 50 + Math.sin(frame / 45) * 40;

  // Neural Alert blinking
  const alertFlash = frame % 8 < 4;

  return (
    <AbsoluteFill style={{ 
      backgroundColor: colorPalette[0],
      transform: `translate(${shakeX}px, ${shakeY}px)`,
    }}>
      
      {/* Inline font loader */}
      <GlobalFontStyle />
      
      {/* 1. AUDIO LAYER - Voice Over */}
      <Sequence from={0}><Audio src={staticFile(`v32_audio_0.mp3`)} volume={1.5} /></Sequence>
      {audio_offsets[1] && <Sequence from={Math.round(p2_start * fps)}><Audio src={staticFile(`v32_audio_1.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[2] && <Sequence from={Math.round(p3_start * fps)}><Audio src={staticFile(`v32_audio_2.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[3] && <Sequence from={Math.round(p4_start * fps)}><Audio src={staticFile(`v32_audio_3.mp3`)} volume={1.5} /></Sequence>}
      {audio_offsets[4] && <Sequence from={Math.round(p5_start * fps)}><Audio src={staticFile(`v32_audio_4.mp3`)} volume={1.5} /></Sequence>}

      {/* HYPNOTIC BACKGROUND MUSIC (loops throughout video) */}
      <Sequence from={0}><Audio src={staticFile(`hypno.wav`)} volume={0.3} loop /></Sequence>

      {/* SFX */}
      {Array.from({length: 20}).map((_, i) => {
          const glitchFrame = Math.round(p3_start * fps) + (i * 60);
          if (glitchFrame < p4_start * fps) {
             return <Sequence key={`ding-${i}`} from={glitchFrame}><Audio src={staticFile("ding.wav")} volume={0.8} /></Sequence>
          }
          return null;
      })}
      {audio_offsets[2] && <Sequence from={Math.round(p3_start * fps)}><Audio src={staticFile("riser.wav")} volume={0.5} /></Sequence>}
      {audio_offsets[3] && <Sequence from={Math.round(p4_start * fps)}><Audio src={staticFile("impact.wav")} volume={2} /></Sequence>}

      {/* 2. THE HD LIGHT COLOR BLENDING BACKGROUND */}
      <AbsoluteFill style={{ 
          zIndex: 0, 
          background: `linear-gradient(${bgAngle}deg, ${colorPalette[0]}, ${colorPalette[1]}, ${colorPalette[2]})`,
          overflow: "hidden" 
      }}>
         <div style={{ position:"absolute", width: "150%", height: "150%", top: "-25%", left: "-25%", filter: "blur(60px)"}}>
            <div style={{ position:"absolute", left: `${orb1X}%`, top: `${orb1Y}%`, width: "800px", height: "800px", borderRadius: "50%", background: colorPalette[1], opacity: 0.85, transform: "translate(-50%, -50%)", mixBlendMode: "screen" }} />
            <div style={{ position:"absolute", left: `${orb2X}%`, top: `${orb2Y}%`, width: "900px", height: "900px", borderRadius: "50%", background: colorPalette[2], opacity: 0.85, transform: "translate(-50%, -50%)", mixBlendMode: "screen" }} />
         </div>
         {/* Scan lines overlay for that cinematic HD feel */}
         <div style={{ position:"absolute", width:"100%", height:"100%", backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px)", zIndex:1 }} />
      </AbsoluteFill>

      {/* 3. THE VISUAL CORE - Bigger Floating Screen */}
      <AbsoluteFill style={{ zIndex: 10 }}>
        {/* Phase 1 & 2: Floating Box — BIGGER & GLOSSY */}
        <Sequence from={0} durationInFrames={Math.round(p3_start * fps)}>
           <div style={{
             position: "absolute", top: "20%", left: "3%", width: "94%", height: "58%",
             transform: `translateY(${Math.sin(frame / 20) * 15}px)`, 
             // HD glossy border with neon glow — NO grey background box
             boxShadow: `0 40px 100px rgba(0,0,0,0.6), 0 0 120px ${colorPalette[1]}, inset 0 0 30px rgba(255,255,255,0.1)`, 
             border: `5px solid rgba(255,255,255,0.8)`, 
             borderRadius: "36px", overflow: "hidden",
             backdropFilter: "blur(10px)",
           }}>
              {/* Inner gloss effect at top */}
              <div style={{ position:"absolute", top:0, left:0, right:0, height:"30%", background:"linear-gradient(to bottom, rgba(255,255,255,0.25), transparent)", zIndex:2, pointerEvents:"none", borderRadius:"36px 36px 0 0" }} />
              <OffthreadVideo 
                src={staticFile(styleSeed % 2 === 0 ? "gta.mp4" : "sand.mp4")} 
                style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.4) contrast(1.1) brightness(1.1)" }} 
              />
           </div>
        </Sequence>

        {/* Phase 3: SMOOTH SPLIT SCREEN */}
        <Sequence from={Math.round(p3_start * fps)} durationInFrames={Math.round((p4_start - p3_start) * fps)}>
           <AbsoluteFill style={{ display: "flex", flexDirection: "column", padding: "15px", gap: "15px" }}>
             <div style={{ flex: 1, overflow: "hidden", borderRadius: "30px", border: `5px solid ${colorPalette[0]}`, boxShadow: `0 0 60px ${colorPalette[0]}, inset 0 0 20px rgba(255,255,255,0.05)` }}>
                <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)", filter:"saturate(1.5) contrast(1.1)" }} />
             </div>
             <div style={{ flex: 1, overflow: "hidden", borderRadius: "30px", border: `5px solid ${colorPalette[1]}`, boxShadow: `0 0 60px ${colorPalette[1]}, inset 0 0 20px rgba(255,255,255,0.05)` }}>
                <OffthreadVideo src={staticFile("sand.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", filter:"saturate(1.5) contrast(1.1)" }} />
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
                    position: "absolute", top: "22%", left: "3%", width: "94%", height: "56%",
                    transform: `scale(${spring({fps, frame: frame - (Math.round(p4_start*fps)+15), config: {damping: 12}})})`,
                    boxShadow: `0 0 200px ${colorPalette[1]}, 0 0 60px white`, 
                    border: `8px solid white`, borderRadius: "40px", overflow: "hidden",
                  }}>
                     <div style={{ position:"absolute", top:0, left:0, right:0, height:"30%", background:"linear-gradient(to bottom, rgba(255,255,255,0.2), transparent)", zIndex:2, pointerEvents:"none" }} />
                     <OffthreadVideo src={staticFile(styleSeed % 2 === 0 ? "sand.mp4" : "gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.6) contrast(1.2) brightness(1.1)" }} />
                 </div>
                 {/* PAYOUT counter — pure text, NO dark box */}
                 <div style={{ position: "absolute", bottom: "5%", width: "94%", left: "3%", textAlign: "center" }}>
                     <h1 style={{ 
                       margin: 0, color: "white", fontSize: "90px", 
                       fontFamily: IMPACT_FONT, 
                       textShadow: `0 0 60px ${colorPalette[1]}, 0 0 20px white, 4px 4px 0 black`,
                       WebkitTextStroke: "3px black"
                     }}>PAYOUT: {serotoninTarget.toLocaleString()}</h1>
                 </div>
              </AbsoluteFill>
           )}
        </Sequence>
      </AbsoluteFill>

      {/* 4. DYNAMIC NEURAL ALERT BAR — changes every run, no grey box */}
      {(phase === 2 || phase === 3) && (
         <AbsoluteFill style={{ pointerEvents: "none", zIndex: 150 }}>
            <div style={{ 
                position: "absolute", top: "4%", left: "3%", width: "94%", 
                background: alertFlash 
                  ? `linear-gradient(90deg, #FF0044, #FF6600)` 
                  : "transparent",
                border: `5px solid ${alertFlash ? "white" : "#FF0044"}`,
                color: alertFlash ? "white" : "#FF0044",
                padding: "14px 20px", textAlign: "center",
                fontFamily: IMPACT_FONT, 
                fontSize: "52px", fontWeight: "bold",
                letterSpacing: "4px",
                boxShadow: alertFlash ? "0 0 60px red, 0 0 20px orange" : "none",
                borderRadius: "18px",
                // NO background box when not flashing — just border and text
            }}>
                {currentAlert.icon} {currentAlert.text}
            </div>
         </AbsoluteFill>
      )}

      {/* 5. GAMIFICATION DOPAMINE COUNTER — NO dark box, pure glowing text */}
      <Sequence from={Math.round(p2_start * fps)} durationInFrames={Math.round((p4_start - p2_start) * fps)}>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 150, pointerEvents: "none" }}>
          <div style={{
              // NO background/box — pure text with strong glow
              padding: "0",
              color: colorPalette[0],
              fontFamily: IMPACT_FONT, 
              fontSize: "80px", fontWeight: "bold",
              textShadow: `0 0 40px ${colorPalette[0]}, 0 0 80px white, 4px 4px 0 black`,
              WebkitTextStroke: "3px black",
              transform: `translateY(300px)`,
              letterSpacing: "2px"
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
              position: "absolute", left: `${25 + (i * 25)}%`, top: "48%", fontSize: "160px",
              transform: `scale(${spring({ fps, frame: frame - spawnFrame, config: { damping: 10 } })}) translateY(${interpolate(frame - spawnFrame, [0, fps * 2], [0, -450])}px)`,
              opacity: interpolate(frame - spawnFrame, [0, fps*1.5, fps*2], [1, 1, 0]),
              filter: `drop-shadow(0 0 20px white)`
            }}>
              {emoji}
            </div>
          );
        })}
      </AbsoluteFill>

      {/* 7. HD CAPTION ENGINE — NO background box, text-shadow + glow only */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", zIndex: 300, pointerEvents: "none" }}>
        {currentWord && (() => {
          const timeSinceWordStart = currentTime - currentWord.start;
          const animStyle = currentWordIndex % 6;
          
          let transformStr = "";
          let opacityVal = 1;

          if (animStyle === 0) {
            transformStr = `scale(${spring({ fps, frame: frame - Math.round(currentWord.start * fps), config: { damping: 12 } })})`;
          } else if (animStyle === 1) {
            transformStr = `translate(${Math.sin(frame)*15}px, ${Math.cos(frame)*15}px) scale(1.1)`;
          } else if (animStyle === 2) {
            opacityVal = frame % 4 < 2 ? 1 : 0;
            transformStr = `scale(1.2)`;
          } else if (animStyle === 3) {
            const rotX = interpolate(timeSinceWordStart, [0, 0.2], [-90, 0], { extrapolateRight: "clamp" });
            transformStr = `perspective(500px) rotateX(${rotX}deg) scale(1.1)`;
          } else if (animStyle === 4) {
            const s = interpolate(timeSinceWordStart, [0, 0.2], [2, 1], { extrapolateRight: "clamp" });
            transformStr = `scale(${s})`;
          } else {
            transformStr = `scale(${spring({ fps, frame: frame - Math.round(currentWord.start * fps), config: { tension: 300, friction: 10 } })}) rotate(${(currentWordIndex % 2 === 0 ? 1 : -1) * 8}deg)`;
          }

          const glitchShadow = isVHSGlitch 
            ? "10px 0 red, -10px 0 cyan" 
            : `0 0 40px white, 0 0 80px ${colorPalette[currentWordIndex % colorPalette.length]}, 4px 4px 0 black`;
          
          if (isRedBox) {
            // Red-highlighted words: vivid color, NO background box — just border + shadow
            return (
              <div style={{
                  border: `6px solid white`,
                  borderRadius: "16px",
                  padding: "8px 40px", 
                  background: `linear-gradient(135deg, #FF0044, #FF6600)`,
                  fontSize: "90px", fontFamily: IMPACT_FONT, fontWeight: "900", color: "#FFF",
                  textAlign: "center", transform: transformStr, opacity: opacityVal,
                  textShadow: "0 0 80px #FF0044, 4px 4px 0 black",
                  boxShadow: "0 0 100px #FF0044, 0 0 40px orange",
                  maxWidth: "88%", wordWrap: "break-word", lineHeight: "1.1",
                  letterSpacing: "2px"
                }}>
                {currentWord.word.toUpperCase()}
              </div>
            );
          } else {
            return (
              <div style={{
                  // ZERO background/box — only text with multi-layer shadow for HD readability
                  fontSize: "80px", fontFamily: HINDI_FONT, fontWeight: "900", 
                  color: "white", 
                  textAlign: "center",
                  textShadow: glitchShadow,
                  WebkitTextStroke: "2px black",
                  transform: transformStr, opacity: opacityVal,
                  maxWidth: "88%", wordWrap: "break-word", lineHeight: "1.2",
                  // NO background, NO borderRadius, NO padding box
                }}>
                {currentWord.word}
              </div>
            );
          }
        })()}
      </AbsoluteFill>

      {/* 8. SUBLIMINAL FLASH */}
      {isSubliminal && (
        <AbsoluteFill style={{ zIndex: 999, backgroundColor: "white", opacity: 0.9 }}>
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <div style={{ 
              fontSize: "200px", fontFamily: IMPACT_FONT, color: "black", fontWeight: "900",
              textShadow: "none"
            }}>{subliminalWord}</div>
          </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* 9. THE ADRENALINE COVER (Frame 0 only) */}
      {frame === 0 && (
        <AbsoluteFill style={{ zIndex: 1000 }}>
             <OffthreadVideo src={staticFile("gta.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", filter:"saturate(1.4) contrast(1.1)" }} />
             <div style={{ position: "absolute", width: "100%", height: "100%", background: `linear-gradient(45deg, ${colorPalette[0]}88, ${colorPalette[1]}88)` }} />
             <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
                 <div style={{
                      background: `linear-gradient(135deg, #FF0044, #FF6600)`,
                      padding: "20px 50px", 
                      border: "10px solid white",
                      fontSize: "120px", fontFamily: IMPACT_FONT, fontWeight: "900", color: "#FFF",
                      textAlign: "center", 
                      boxShadow: "0 0 150px #FF0044, 0 0 50px orange",
                      textShadow: "0 0 80px #FF0044, 6px 6px 0 black",
                      maxWidth: "90%", wordWrap: "break-word",
                      borderRadius: "24px",
                      letterSpacing: "4px"
                    }}>
                     {dynamicRedWord || "SIMULATION"}
                  </div>
             </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* 10. THE LOOP MIRROR (fade out) */}
      {phase === 5 && (
         <AbsoluteFill style={{ 
            backgroundColor: "black", 
            opacity: interpolate(frame, [p5_start * fps, total_duration * fps], [0, 1], {extrapolateRight:"clamp"}), 
            zIndex: 1000 
         }} />
      )}

    </AbsoluteFill>
  );
};
