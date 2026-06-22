import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  OffthreadVideo,
  Img,
  random,
  spring,
  Sequence
} from "remotion";
import React from "react";

import { loadFont as loadDevanagari } from "@remotion/google-fonts/NotoSansDevanagari";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";

const { fontFamily: devanagariFont } = loadDevanagari("normal", {
  weights: ["700", "900"],
  subsets: ["devanagari"],
});
const { fontFamily: montserratFont } = loadMontserrat("normal", { weights: ["900", "700", "600"] });
const { fontFamily: playfairFont } = loadPlayfair("normal", { weights: ["900", "700"] });

const GlobalStyle = () => (
  <style>{`* { box-sizing: border-box; }`}</style>
);

const HINDI_FONT = `${devanagariFont}, 'Mangal', 'Sanskrit Text', Arial, sans-serif`;
const TITLE_FONT = `${montserratFont}, Impact, sans-serif`;
const HOOK_FONT = `${playfairFont}, Georgia, serif`;

const PALETTES = [
  { p: "#FAC775", a: "#F8B133", g: "#E59400", bg1: "#0C1420", bg2: "#080D15" }, // Navy & Amber
  { p: "#FAC775", a: "#F8B133", g: "#E59400", bg1: "#0A1118", bg2: "#05090D" }, // Deep Navy
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
      transform: `translate(${sx}px,${sy}px)`
    }}>
      <GlobalStyle />

      {/* ── AUDIO ─────────────────────────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("v32_audio_0.mp3")} volume={1.6} /></Sequence>
      {p2 && <Sequence from={Math.round(p2*fps)}><Audio src={staticFile("v32_audio_1.mp3")} volume={1.6} /></Sequence>}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("v32_audio_2.mp3")} volume={1.6} /></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("v32_audio_3.mp3")} volume={1.6} /></Sequence>}
      {p5 && <Sequence from={Math.round(p5*fps)}><Audio src={staticFile("v32_audio_4.mp3")} volume={1.6} /></Sequence>}
      <Sequence from={0}><Audio src={staticFile("hypno.wav")} volume={0.15} loop /></Sequence>
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("riser.wav")} volume={0.5}/></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("impact.wav")} volume={2.0}/></Sequence>}

      {/* ── BACKGROUND ────────────────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 0, backgroundColor: pal.bg1 }}>
        <div style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.4) 100%)`,
        }}/>
      </AbsoluteFill>

      {/* ── PHASE 1: HOOK (0 - p2) ────────────────────────────────── */}
      <Sequence from={0} durationInFrames={Math.round(p2*fps)}>
        <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: 60 }}>
          <div style={{
            fontFamily: HOOK_FONT, fontSize: 100, fontWeight: 900, color: "#FFFFFF",
            textAlign: "center", lineHeight: 1.2,
          }}>
            {script.hook?.split(" ").map((w: string, i: number) => {
              const isHighlight = activeRedWords.some(r => w.toUpperCase().includes(r)) || i === Math.floor(script.hook.split(" ").length / 2);
              return (
                <span key={i} style={{ color: isHighlight ? pal.p : "#FFFFFF", display: "inline-block", marginRight: 20 }}>
                  {w}
                </span>
              );
            })}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 2: SPLIT SCREEN (p2 - p3) ─────────────────────── */}
      <Sequence from={Math.round(p2*fps)} durationInFrames={Math.round((p4-p3)*fps > 0 ? (p3-p2)*fps : 0)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "row" }}>
          {/* LEFT: Poor Mindset */}
          <div style={{ flex: 1, borderRight: "2px solid rgba(255,255,255,0.1)", display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "25%" }}>
            <div style={{ fontFamily: TITLE_FONT, fontSize: 45, color: "rgba(255,255,255,0.5)", letterSpacing: 2, marginBottom: 40 }}>POOR MINDSET</div>
            <div style={{ fontSize: 180, marginBottom: 60 }}>😞</div>
            <div style={{ fontFamily: HINDI_FONT, fontSize: 60, color: "#FFFFFF", textAlign: "center", padding: 40 }}>
              {script.split_screen?.left?.split("-")[1] || "Saves money"}
            </div>
          </div>
          {/* RIGHT: Rich Mindset */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "25%" }}>
            <div style={{ fontFamily: TITLE_FONT, fontSize: 45, color: pal.p, letterSpacing: 2, marginBottom: 40 }}>RICH MINDSET</div>
            <div style={{ fontSize: 180, marginBottom: 60 }}>🧠</div>
            <div style={{ fontFamily: HINDI_FONT, fontSize: 60, color: "#FFFFFF", textAlign: "center", padding: 40 }}>
              {script.split_screen?.right?.split("-")[1] || "Invests money"}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 3: AUTHORITY CLAIM (p3 - p4) ──────────────────── */}
      <Sequence from={Math.round(p3*fps)} durationInFrames={Math.round((p4-p3)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, gap: 60 }}>
          {/* Premium circular photo frame */}
          <div style={{
            width: 420, height: 420, borderRadius: "50%",
            overflow: "hidden",
            border: `6px solid ${pal.p}`,
            boxShadow: `0 0 0 3px ${pal.bg1}, 0 0 0 9px ${pal.p}55, 0 0 80px ${pal.p}44`,
            flexShrink: 0
          }}>
            <Img
              src={staticFile("host_photo.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center top" }}
            />
          </div>
          {/* Authority statement */}
          <div style={{
            fontFamily: HINDI_FONT, fontSize: 75, fontWeight: 700, color: "#FFFFFF",
            textAlign: "center", lineHeight: 1.3, maxWidth: "90%"
          }}>
            {script.authority_claim}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 4: NUMBERED LIST (p4 - p5) ──────────────────── */}
      <Sequence from={Math.round(p4*fps)} durationInFrames={Math.round((p5-p4)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "10% 8%" }}>
          {(script.numbered_list || []).map((item: string, i: number) => (
            <div key={i} style={{
              display: "flex", alignItems: "center",
              background: "rgba(255,255,255,0.05)",
              padding: "40px 50px", borderRadius: 30, marginBottom: 40,
              border: "1px solid rgba(255,255,255,0.08)",
              boxShadow: "0 10px 30px rgba(0,0,0,0.5)"
            }}>
              <div style={{
                width: 90, height: 90, borderRadius: "50%",
                background: pal.p,
                display: "flex", justifyContent: "center", alignItems: "center",
                fontFamily: TITLE_FONT, fontSize: 50, fontWeight: 900, color: pal.bg1,
                marginRight: 40, flexShrink: 0
              }}>
                {i + 1}
              </div>
              <div style={{
                fontFamily: HINDI_FONT, fontSize: 68, fontWeight: 700,
                color: "#FFFFFF", lineHeight: 1.2
              }}>
                {item}
              </div>
            </div>
          ))}
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 5: SAVE CARD (p5 - end) ─────────────────────── */}
      <Sequence from={Math.round(p5*fps)}>
        <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: 60 }}>
          <div style={{
            border: `4px solid ${pal.p}`, borderRadius: 40, padding: "70px 60px", width: "90%",
            display: "flex", flexDirection: "column", alignItems: "center",
            boxShadow: `0 0 80px ${pal.p}44, 0 0 200px ${pal.p}22`,
            background: "rgba(0,0,0,0.5)"
          }}>
            <div style={{ fontSize: 110, marginBottom: 30 }}>🔖</div>
            <div style={{
              fontFamily: TITLE_FONT, fontSize: 75, fontWeight: 900,
              color: pal.p, letterSpacing: 4, marginBottom: 55, textAlign: "center"
            }}>
              SAVE KARO
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 25, width: "100%", alignItems: "flex-start" }}>
              {(script.numbered_list || []).map((item: string, i: number) => (
                <div key={i} style={{
                  fontFamily: HINDI_FONT, fontSize: 55, color: "#FFFFFF",
                  fontWeight: 700, display: "flex", alignItems: "center", gap: 20
                }}>
                  <span style={{ color: pal.p, fontFamily: TITLE_FONT, fontWeight: 900, fontSize: 55 }}>{i + 1}.</span>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── FADE OUT ────────────────────────────────────────────── */}
      {phase === 5 && (
        <AbsoluteFill style={{
          zIndex: 1000, backgroundColor: "black",
          opacity: interpolate(frame, [p5 * fps, total_duration * fps], [0, 1], {extrapolateRight: "clamp"})
        }}/>
      )}
    </AbsoluteFill>
  );
};
