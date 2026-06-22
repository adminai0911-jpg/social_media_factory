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

import { loadFont as loadDevanagari } from "@remotion/google-fonts/NotoSansDevanagari";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";

const { fontFamily: devanagariFont } = loadDevanagari("normal", {
  weights: ["700", "900"],
  subsets: ["devanagari"],
});
const { fontFamily: montserratFont } = loadMontserrat("normal", { weights: ["900"] });
const { fontFamily: bebasFont } = loadBebasNeue("normal", { weights: ["400"] });

const GlobalStyle = () => (
  <style>{`* { box-sizing: border-box; }`}</style>
);

const HINDI_FONT = `${devanagariFont}, 'Mangal', 'Sanskrit Text', Arial, sans-serif`;
const TITLE_FONT = `${bebasFont}, ${montserratFont}, Impact, sans-serif`;

const PALETTES = [
  { p: "#FFD700", a: "#FFA500", g: "#FF8C00", bg1: "#0A0A0A", bg2: "#000000" }, // Classic Gold & Black
  { p: "#E5A93C", a: "#F4D03F", g: "#D4AC0D", bg1: "#0F0F0F", bg2: "#050505" }, // Premium Amber
  { p: "#F1C40F", a: "#F39C12", g: "#E67E22", bg1: "#111111", bg2: "#000000" }, // Bright Gold
  { p: "#D4AF37", a: "#C5B358", g: "#B8860B", bg1: "#0C0C0C", bg2: "#030303" }, // Metallic Gold
  { p: "#FFDF00", a: "#D4AF37", g: "#DAA520", bg1: "#000000", bg2: "#050505" }, // Royal Gold
];


const NEURAL_ALERTS = [
  "⚠️  NEURAL LINK ACTIVE",
  "🧠  MIND HACK DETECTED",
  "⚡  DOPAMINE SPIKE NOW",
  "🔴  BRAIN SIGNAL LOCKED",
  "🚨  ATTENTION HIJACKED",
  "💀  REALITY GLITCHING",
  "🔥  ADRENALINE TRIGGER",
  "👁️  SUBLIMINAL UPLOAD",
  "🌀  HYPNOSIS IN PROGRESS",
  "❌  ESCAPE IMPOSSIBLE",
  "🎯  FOCUS LOCKED IN",
  "⚡  SYSTEM OVERRIDE",
];

const RED_WORDS = ["WAKE","SIMULATION","SHADOWS","TRAP","LYING","FAKE","DREAM","FEAR","PANIC","NOW","LIES","BREAK","SCAM","CHEAT","DANGER"];

// ── Background video pools — the engine downloads up to 4 videos ──
const BG_VIDEOS = ["gta.mp4","sand.mp4","bg3.mp4","bg4.mp4"];

export const MainVideo: React.FC<{
  script: any;
  timings: any[];
  audio_offsets: number[];
  total_duration: number;
}> = ({ script, timings, audio_offsets, total_duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  if (!script || !audio_offsets || audio_offsets.length < 5) return null;

  const seed       = script.style_seed || 1;
  const emojis     = script.emojis || ["👀","🔥","💀"];
  const pal        = PALETTES[seed % PALETTES.length];
  const pal2       = PALETTES[(seed + 7) % PALETTES.length]; // secondary accent
  const alertText  = NEURAL_ALERTS[seed % NEURAL_ALERTS.length];
  const redKw      = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9]/g,"") : "WARNING";
  const subliminal = (script.subliminal_flash_word || "WAKE UP").toUpperCase();
  const serotonin  = Number(script.serotonin_payoff_number || 88319);
  const activeRedWords = [...RED_WORDS, redKw];

  // Choose background videos based on seed
  const bgVideo1 = BG_VIDEOS[seed % BG_VIDEOS.length];
  const bgVideo2 = BG_VIDEOS[(seed + 2) % BG_VIDEOS.length];

  const [,p2,p3,p4,p5] = audio_offsets;
  let phase = 1;
  if (t >= p2 && t < p3) phase = 2;
  else if (t >= p3 && t < p4) phase = 3;
  else if (t >= p4 && t < p5) phase = 4;
  else if (t >= p5) phase = 5;

  const wordIdx = timings.findIndex(w => t >= w.start && t <= w.end + 0.1);
  const word    = timings[wordIdx];
  const isRed   = word ? activeRedWords.some(r => word.word.toUpperCase().replace(/[^A-Z0-9]/g,"").includes(r)) : false;

  const isVHS         = frame % 50 > 46;
  const sublimFrame   = Math.round(p3 * fps) + 90;
  const isSubliminal  = frame === sublimFrame;
  const shatterActive = phase === 4 && frame < Math.round(p4 * fps) + 12;

  const shakeAmt = isRed ? 14 : shatterActive ? 35 : (isVHS ? 4 : 0);
  const sx = shakeAmt > 0 ? (random(frame)     - 0.5) * shakeAmt : 0;
  const sy = shakeAmt > 0 ? (random(frame + 1) - 0.5) * shakeAmt : 0;

  // ── Animated orbs — large, vivid, blended ──
  const o1x = 50 + Math.sin(frame / 40) * 40;
  const o1y = 30 + Math.cos(frame / 35) * 30;
  const o2x = 50 + Math.cos(frame / 28) * 45;
  const o2y = 70 + Math.sin(frame / 50) * 30;
  const o3x = 50 + Math.sin(frame / 55 + 2) * 35;
  const o3y = 50 + Math.cos(frame / 45 + 1) * 40;
  const o4x = 30 + Math.cos(frame / 32) * 25;
  const o4y = 80 + Math.sin(frame / 38) * 20;

  const alertFlash = frame % 6 < 3;

  const tension = phase < 4
    ? interpolate(frame, [0, p4 * fps], [0, 100], { extrapolateRight: "clamp" })
    : 100;

  const panAngle = (frame / fps) * 0.2 * Math.PI * 2;
  const panLeft  = 0.5 + 0.5 * Math.cos(panAngle);

  const bobY = Math.sin(frame / 20) * 10;

  const counterVal = phase === 2 ? null :
    Math.floor(interpolate(frame, [p3 * fps, p4 * fps], [0, serotonin], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp"
    }));

  // Moving scan line position
  const scanY = (frame * 3) % 1920;

  // Glitch offset for VHS mode
  const glitchX = isVHS ? (random(frame + 99) - 0.5) * 30 : 0;

  return (
    <AbsoluteFill style={{
      backgroundColor: pal.bg1,
      transform: `translate(${sx}px,${sy}px)`,
      overflow: "hidden"
    }}>
      <GlobalStyle />

      {/* ── AUDIO ─────────────────────────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("v32_audio_0.mp3")} volume={1.6} /></Sequence>
      {p2 && <Sequence from={Math.round(p2*fps)}><Audio src={staticFile("v32_audio_1.mp3")} volume={1.6} /></Sequence>}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("v32_audio_2.mp3")} volume={1.6} /></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("v32_audio_3.mp3")} volume={1.6} /></Sequence>}
      {p5 && <Sequence from={Math.round(p5*fps)}><Audio src={staticFile("v32_audio_4.mp3")} volume={1.6} /></Sequence>}
      <Sequence from={0}><Audio src={staticFile("hypno.wav")} volume={0.32} loop /></Sequence>
      {Array.from({length:20}).map((_,i)=>{
        const gf = Math.round(p3*fps)+(i*60);
        if(gf < p4*fps) return <Sequence key={i} from={gf}><Audio src={staticFile("ding.wav")} volume={0.6}/></Sequence>;
        return null;
      })}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("riser.wav")} volume={0.5}/></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("impact.wav")} volume={2.0}/></Sequence>}

      {/* ── LAYER 0: DEEP BACKGROUND GRADIENT BASE ─────────────── */}
      <AbsoluteFill style={{ zIndex: 0 }}>
        {/* Simple, clean, dark gradient background to prevent color overlap */}
        <div style={{
          position: "absolute", inset: 0,
          background: `linear-gradient(180deg, ${pal.bg1} 0%, ${pal.bg2} 100%)`
        }}/>

        {/* Subtle top/bottom glow matching the palette, NO muddy overlaps */}
        <div style={{
          position: "absolute", left: 0, right: 0, top: 0, height: "30%",
          background: `linear-gradient(180deg, ${pal.p}22 0%, transparent 100%)`,
          pointerEvents: "none"
        }}/>
        <div style={{
          position: "absolute", left: 0, right: 0, bottom: 0, height: "30%",
          background: `linear-gradient(0deg, ${pal.a}22 0%, transparent 100%)`,
          pointerEvents: "none"
        }}/>

        {/* Animated scanlines (cinematic texture) */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,0.015) 3px,rgba(255,255,255,0.015) 4px)",
          pointerEvents: "none"
        }}/>

        {/* Vignette */}
        <div style={{
          position: "absolute", inset: 0,
          background: "radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.85) 100%)",
          pointerEvents: "none"
        }}/>
      </AbsoluteFill>

      {/* ── LAYER 2: MAIN VISUAL SCREEN ──────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 10 }}>

        {/* Phase 1 & 2: LARGE Premium Floating Glass Screen */}
        <Sequence from={0} durationInFrames={Math.round(p3*fps)}>
          <div style={{
            position: "absolute",
            top: "12%", left: "3%", width: "94%", height: "68%",
            transform: `translateY(${bobY}px)`,
            borderRadius: 36,
            overflow: "hidden",
            boxShadow: `
              0 0 0 2px rgba(255,255,255,0.1),
              0 0 60px ${pal.p}44,
              0 40px 100px rgba(0,0,0,0.9)
            `,
          }}>
            {/* Background video with heavy dark overlay for premium feel and text readability */}
            <OffthreadVideo
              src={staticFile(bgVideo1)}
              style={{
                width: "100%", height: "100%", objectFit: "cover",
                transform: `scale(1.02)`,
                filter: `saturate(1.2) contrast(1.1) brightness(0.6)`,
              }}
            />
            {/* Dark gradient overlay for text readability */}
            <div style={{
              position: "absolute", inset: 0,
              background: `linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.8) 100%)`,
              pointerEvents: "none",
            }}/>
            {/* Elegant Gold Trim */}
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, height: "100%",
              boxShadow: `inset 0 0 0 1px ${pal.p}88`,
              pointerEvents: "none", borderRadius: 36
            }}/>
        </Sequence>

        {/* Phase 3: Split Screen -> Changed to single premium screen */}
        <Sequence from={Math.round(p3*fps)} durationInFrames={Math.round((p4-p3)*fps)}>
          <AbsoluteFill style={{ display: "flex", flexDirection: "column", padding: 24, gap: 14 }}>
            <div style={{
              flex: 1, overflow: "hidden", borderRadius: 30,
              boxShadow: `0 0 0 1px ${pal.p}88, 0 0 60px ${pal.p}22`,
              position: "relative",
            }}>
              <OffthreadVideo src={staticFile(bgVideo2)} style={{
                width: "100%", height: "100%", objectFit: "cover",
                filter: `saturate(1.2) contrast(1.1) brightness(0.6)`
              }}/>
              {/* Clean text overlay box */}
              <div style={{
                position: "absolute", inset: 0,
                background: `linear-gradient(180deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6))`,
                pointerEvents: "none"
              }}/>
            </div>
          </AbsoluteFill>
        </Sequence>

        {/* Phase 4 & 5: Clean Payoff & Save Card */}
        <Sequence from={Math.round(p4*fps)}>
          <AbsoluteFill style={{ display: "flex", flexDirection: "column", padding: 24, gap: 14 }}>
            <div style={{
              flex: 1, overflow: "hidden", borderRadius: 30,
              boxShadow: phase === 5 ? `0 0 0 4px ${pal.p}, 0 0 100px ${pal.p}66` : `0 0 0 1px ${pal.p}88, 0 0 60px ${pal.p}22`,
              position: "relative",
              transform: phase === 5 ? `scale(1.02)` : `scale(1)`,
              transition: "all 0.5s cubic-bezier(0.19, 1, 0.22, 1)"
            }}>
              <OffthreadVideo src={staticFile(bgVideo1)} style={{
                width: "100%", height: "100%", objectFit: "cover",
                filter: phase === 5 ? `saturate(0.8) contrast(1.2) brightness(0.4)` : `saturate(1.2) contrast(1.1) brightness(0.6)`
              }}/>
              {/* Dark overlay */}
              <div style={{
                position: "absolute", inset: 0,
                background: phase === 5 ? `rgba(0,0,0,0.85)` : `linear-gradient(180deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6))`,
                pointerEvents: "none"
              }}/>

              {/* OUTRO SAVE CARD (Phase 5 only) */}
              {phase === 5 && (
                <div style={{
                  position: "absolute", inset: 0,
                  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                  padding: 40, textAlign: "center"
                }}>
                  <div style={{ fontSize: 160, marginBottom: 20 }}>📌</div>
                  <div style={{
                    fontSize: 80, fontFamily: TITLE_FONT, fontWeight: 900,
                    color: "#FFFFFF", marginBottom: 40, letterSpacing: 2
                  }}>
                    SAVE THIS RULE
                  </div>
                  <div style={{
                    fontSize: 45, fontFamily: HINDI_FONT, fontWeight: 700,
                    color: pal.p, background: "rgba(0,0,0,0.5)",
                    padding: "20px 40px", borderRadius: 20,
                    boxShadow: `0 0 0 1px ${pal.p}44`
                  }}>
                    Or You Will Keep Making The Same Mistake.
                  </div>
                </div>
              )}
            </div>
          </AbsoluteFill>
        </Sequence>
      </AbsoluteFill>

      {/* ── LAYER 3: TENSION BAR ─────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 120, pointerEvents: "none" }}>
        <div style={{
          position: "absolute", top: 0, left: 0, height: 7,
          width: `${tension}%`,
          background: `linear-gradient(90deg,${pal.p},${pal.a},${pal.g},${pal2.p})`,
          boxShadow: `0 0 30px ${pal.a}, 0 0 60px ${pal.p}`,
        }}/>
      </AbsoluteFill>

      {/* ── LAYER 4: NEURAL ALERT — PREMIUM GLOW ──────────── */}
      {(phase === 2 || phase === 3) && (
        <AbsoluteFill style={{ zIndex: 150, pointerEvents: "none" }}>
          <div style={{
            position: "absolute", top: "4%", left: "3%", width: "94%",
            textAlign: "center",
            fontFamily: TITLE_FONT, fontSize: 50, letterSpacing: 8, fontWeight: 900,
            color: alertFlash ? "#FFFFFF" : pal.p,
            textShadow: `0 4px 12px rgba(0,0,0,0.8), 0 0 20px ${pal.p}88`,
            background: "none",
            border: "none",
            padding: "10px 0",
          }}>
            {alertText}
          </div>
        </AbsoluteFill>
      )}


      {/* ── LAYER 5: SEROTONIN COUNTER — GOLD GRADIENT ───────────────────────────── */}
      <Sequence from={Math.round(p2*fps)} durationInFrames={Math.round((p4-p2)*fps)}>
        <AbsoluteFill style={{ zIndex: 160, pointerEvents: "none", justifyContent: "flex-end", alignItems: "center", paddingBottom: 55 }}>
          <div style={{
            fontFamily: TITLE_FONT, fontSize: 90, fontWeight: 900, letterSpacing: 4,
            background: `linear-gradient(180deg, ${pal.p}, ${pal.a})`,
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            filter: `drop-shadow(0 4px 10px rgba(0,0,0,0.9)) drop-shadow(0 0 20px ${pal.p}44)`,
          }}>
            {phase === 2 ? "SCANNING..." : counterVal?.toLocaleString()}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── LAYER 6: 8D AUDIO INDICATOR ──────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 130, pointerEvents: "none" }}>
        <div style={{
          position: "absolute", bottom: "28%", right: "4%",
          width: 64, height: 64, borderRadius: "50%",
          border: `2px solid ${pal.a}55`,
          background: `radial-gradient(circle at ${Math.round(panLeft * 100)}% 50%, ${pal.a}77, transparent 70%)`,
          boxShadow: `0 0 25px ${pal.a}55`,
          opacity: phase === 1 || phase === 5 ? 0 : 0.75,
        }}/>
      </AbsoluteFill>

      {/* ── LAYER 7: 4D EMOJIS ───────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 200, pointerEvents: "none" }}>
        {emojis.map((emoji:string, i:number) => {
          const sf = Math.round((p3 + (i * 2.5)) * fps);
          if (frame < sf || frame >= sf + fps * 2) return null;
          const elapsed = frame - sf;
          return (
            <div key={i} style={{
              position: "absolute",
              left: `${18 + (i * 32)}%`,
              top: "42%",
              fontSize: 190,
              transform: `scale(${spring({fps, frame: elapsed, config: {damping: 8}})}) translateY(${interpolate(elapsed, [0, fps*2], [0, -600])}px) rotate(${interpolate(elapsed, [0, fps*2], [0, i % 2 === 0 ? 25 : -25])}deg)`,
              opacity: interpolate(elapsed, [0, fps * 1.6, fps * 2], [1, 1, 0]),
              filter: `drop-shadow(0 0 35px white) drop-shadow(0 0 70px ${pal.p})`,
            }}>
              {emoji}
            </div>
          );
        })}
      </AbsoluteFill>

      {/* ── LAYER 8: HD CAPTION ENGINE — PREMIUM WEALTH TYPOGRAPHY ──── */}
      <AbsoluteFill style={{ zIndex: 300, justifyContent: "flex-end", alignItems: "center", paddingBottom: "20%", pointerEvents: "none" }}>
        {word && phase !== 5 && (() => {
          const elapsed = t - word.start;
          const ai = wordIdx % 4;
          let tf = "";
          let op = 1;

          if (ai === 0) tf = `scale(${spring({fps, frame: frame - Math.round(word.start * fps), config: {damping: 14}})})`;
          else if (ai === 1) tf = `translateY(${Math.sin(frame * 0.5) * 5}px) scale(1.02)`;
          else if (ai === 2) { tf = `scale(1.05)`; }
          else { tf = `scale(${spring({fps, frame: frame - Math.round(word.start * fps), config: {stiffness: 300, damping: 14}})}) rotate(${wordIdx % 2 === 0 ? 2 : -2}deg)`; }

          if (isRed) {
            return (
              <div style={{
                fontFamily: TITLE_FONT, fontSize: 110, fontWeight: 900,
                color: pal.p, // Gold Highlight
                textShadow: `2px 2px 0 #000, -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 0 8px 16px rgba(0,0,0,0.8)`,
                transform: tf, opacity: op,
                textAlign: "center", maxWidth: "90%",
                lineHeight: 1.1, letterSpacing: 4,
                padding: "10px 30px",
                background: "rgba(0,0,0,0.85)",
                borderRadius: 20,
                boxShadow: `0 0 0 2px ${pal.p}AA, 0 10px 30px rgba(0,0,0,0.9)`
              }}>
                {word.word.toUpperCase()}
              </div>
            );
          } else {
            // Hindi caption — crisp white with solid black box
            return (
              <div style={{
                fontFamily: HINDI_FONT, fontSize: 85, fontWeight: 900,
                color: "#FFFFFF",
                transform: tf, opacity: op,
                textAlign: "center", maxWidth: "90%",
                lineHeight: 1.3, letterSpacing: 1,
                background: "rgba(0,0,0,0.85)",
                padding: "15px 40px",
                borderRadius: 24,
                boxShadow: "0 10px 30px rgba(0,0,0,0.8)",
                border: "2px solid rgba(255,255,255,0.1)"
              }}>
                {word.word}
              </div>
            );
          }
        })()}
      </AbsoluteFill>

      {/* ── LAYER 9: COVER FRAME (frame 0) ───────────────────────── */}
      {frame === 0 && (
        <AbsoluteFill style={{ zIndex: 1000 }}>
          <OffthreadVideo src={staticFile(bgVideo1)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(2.0) contrast(1.3) brightness(0.9)" }}/>
          <div style={{ position: "absolute", inset: 0, background: `linear-gradient(160deg,${pal.p}88,${pal.g}55,${pal.a}77)`, mixBlendMode: "overlay" as any }}/>
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <div style={{
              fontFamily: TITLE_FONT, fontSize: 140, fontWeight: 900, letterSpacing: 10,
              background: `linear-gradient(135deg,#fff,${pal.p},${pal.a},${pal.g})`,
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              filter: `drop-shadow(0 0 50px ${pal.p}) drop-shadow(0 0 100px ${pal.g})`,
              textAlign: "center", maxWidth: "92%", lineHeight: 1,
              padding: "0 24px"
            }}>
              {redKw || "SIMULATION"}
            </div>
          </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* ── LAYER 10: SUBLIMINAL FLASH ────────────────────────────── */}
      {isSubliminal && (
        <AbsoluteFill style={{ zIndex: 999, backgroundColor: "#fff" }}>
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <div style={{ fontFamily: TITLE_FONT, fontSize: 240, fontWeight: 900, color: "#000", letterSpacing: 10 }}>
              {subliminal}
            </div>
          </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* ── LAYER 11: FADE OUT ────────────────────────────────────── */}
      {phase === 5 && (
        <AbsoluteFill style={{
          zIndex: 1000, backgroundColor: "black",
          opacity: interpolate(frame, [p5 * fps, total_duration * fps], [0, 1], {extrapolateRight: "clamp"})
        }}/>
      )}
    </AbsoluteFill>
  );
};
