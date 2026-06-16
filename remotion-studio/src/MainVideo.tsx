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

// ── 30 VIBRANT PALETTES — bright, alive, always visually different ──
const PALETTES = [
  { p: "#FF0055", a: "#00F5FF", g: "#FF00CC", bg1: "#1A0010", bg2: "#00101A" },
  { p: "#FFD700", a: "#FF4500", g: "#FFAA00", bg1: "#1A1000", bg2: "#200500" },
  { p: "#00FF88", a: "#0066FF", g: "#00FFFF", bg1: "#001A0F", bg2: "#000A1A" },
  { p: "#FF3366", a: "#FF9900", g: "#FFE000", bg1: "#1A000E", bg2: "#1A0A00" },
  { p: "#AA00FF", a: "#00CCFF", g: "#FF00AA", bg1: "#0E0020", bg2: "#001A25" },
  { p: "#FF6600", a: "#FFDD00", g: "#FF0099", bg1: "#200800", bg2: "#1A1400" },
  { p: "#00FFCC", a: "#FF00FF", g: "#00AAFF", bg1: "#00201A", bg2: "#1A001A" },
  { p: "#FF1493", a: "#00FF7F", g: "#FFD700", bg1: "#200010", bg2: "#001A0A" },
  { p: "#7B00FF", a: "#FF6600", g: "#00FFFF", bg1: "#0A0020", bg2: "#200800" },
  { p: "#00BFFF", a: "#FF69B4", g: "#ADFF2F", bg1: "#001520", bg2: "#200010" },
  { p: "#FF4500", a: "#1E90FF", g: "#FFD700", bg1: "#200500", bg2: "#001020" },
  { p: "#39FF14", a: "#FF0090", g: "#00CFFF", bg1: "#011A00", bg2: "#1A0010" },
  { p: "#FF007F", a: "#7FFF00", g: "#00AAFF", bg1: "#1A000A", bg2: "#0A1A00" },
  { p: "#FFB300", a: "#FF4081", g: "#40C4FF", bg1: "#1A0E00", bg2: "#1A001A" },
  { p: "#E040FB", a: "#00E676", g: "#FFEA00", bg1: "#150020", bg2: "#001A0A" },
  { p: "#FF5722", a: "#00BCD4", g: "#CDDC39", bg1: "#200800", bg2: "#001520" },
  { p: "#00E5FF", a: "#FF1744", g: "#76FF03", bg1: "#001520", bg2: "#200005" },
  { p: "#FF6D00", a: "#00BFA5", g: "#FFD600", bg1: "#1A0800", bg2: "#001A15" },
  { p: "#D500F9", a: "#00E5FF", g: "#FFFF00", bg1: "#12001A", bg2: "#001520" },
  { p: "#F50057", a: "#00BFA5", g: "#FF6D00", bg1: "#1A000A", bg2: "#001A15" },
  { p: "#76FF03", a: "#FF3D00", g: "#00B0FF", bg1: "#051A00", bg2: "#200500" },
  { p: "#FFAB00", a: "#D500F9", g: "#00E5FF", bg1: "#1A0E00", bg2: "#12001A" },
  { p: "#00E676", a: "#FF6D00", g: "#E040FB", bg1: "#001A0A", bg2: "#1A0800" },
  { p: "#40C4FF", a: "#FF5252", g: "#FFD740", bg1: "#001520", bg2: "#1A0500" },
  { p: "#FF5252", a: "#40C4FF", g: "#B2FF59", bg1: "#1A0500", bg2: "#001520" },
  { p: "#FF80AB", a: "#80D8FF", g: "#CCFF90", bg1: "#1A0010", bg2: "#001520" },
  { p: "#64FFDA", a: "#FF6E40", g: "#EA80FC", bg1: "#001A15", bg2: "#1A0800" },
  { p: "#FFFF00", a: "#FF0055", g: "#00FFCC", bg1: "#1A1A00", bg2: "#1A0010" },
  { p: "#FF1744", a: "#69F0AE", g: "#FF9100", bg1: "#1A0005", bg2: "#001A0A" },
  { p: "#AA00FF", a: "#FFAB40", g: "#18FFFF", bg1: "#0E0020", bg2: "#1A0E00" },
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
        {/* Animated full-screen gradient background */}
        <div style={{
          position: "absolute", inset: 0,
          background: `
            radial-gradient(ellipse at ${o1x}% ${o1y}%, ${pal.p}88 0%, transparent 50%),
            radial-gradient(ellipse at ${o2x}% ${o2y}%, ${pal.a}77 0%, transparent 55%),
            radial-gradient(ellipse at ${o3x}% ${o3y}%, ${pal.g}66 0%, transparent 48%),
            radial-gradient(ellipse at ${o4x}% ${o4y}%, ${pal2.p}55 0%, transparent 45%),
            radial-gradient(ellipse at 50% 50%, ${pal.bg2} 0%, ${pal.bg1} 100%)
          `,
        }}/>

        {/* Color-blend overlay for true mix-blend effect */}
        <div style={{
          position: "absolute", inset: 0,
          background: `
            linear-gradient(135deg, ${pal.p}33 0%, transparent 40%, ${pal.a}33 100%)
          `,
          mixBlendMode: "screen" as any,
        }}/>

        {/* Secondary vibrant orb overlay — screen blend */}
        <div style={{
          position: "absolute", inset: 0,
          background: `
            radial-gradient(circle at ${100-o2x}% ${100-o1y}%, ${pal2.a}60 0%, transparent 50%),
            radial-gradient(circle at ${o3x}% ${o4y}%, ${pal2.g}50 0%, transparent 45%)
          `,
          mixBlendMode: "screen" as any,
          opacity: 0.85,
        }}/>

        {/* Animated scanlines (cinematic texture) */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,0.025) 3px,rgba(255,255,255,0.025) 4px)",
          pointerEvents: "none"
        }}/>

        {/* Moving horizontal scan beam */}
        <div style={{
          position: "absolute", left: 0, right: 0,
          top: scanY, height: 2,
          background: `linear-gradient(90deg, transparent, ${pal.p}44, ${pal.a}66, ${pal.g}44, transparent)`,
          opacity: 0.6, pointerEvents: "none"
        }}/>

        {/* Vignette */}
        <div style={{
          position: "absolute", inset: 0,
          background: "radial-gradient(ellipse at 50% 50%, transparent 30%, rgba(0,0,0,0.65) 100%)",
          pointerEvents: "none"
        }}/>

        {/* Grid lines — futuristic HUD */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: `
            linear-gradient(${pal.p}08 1px, transparent 1px),
            linear-gradient(90deg, ${pal.p}08 1px, transparent 1px)
          `,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
          opacity: 0.5,
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
              0 0 0 2px rgba(255,255,255,0.25),
              0 0 60px ${pal.p}99,
              0 0 120px ${pal.a}55,
              0 40px 100px rgba(0,0,0,0.8)
            `,
          }}>
            {/* Background video with VHS glitch */}
            <OffthreadVideo
              src={staticFile(bgVideo1)}
              style={{
                width: "100%", height: "100%", objectFit: "cover",
                transform: isVHS
                  ? `scale(1.06) translateX(${glitchX}px)`
                  : `scale(1.02)`,
                filter: isVHS
                  ? `saturate(2.5) contrast(1.8) hue-rotate(${(frame * 3) % 360}deg) brightness(1.2)`
                  : `saturate(1.8) contrast(1.25) brightness(1.1)`,
              }}
            />
            {/* Inner color overlay blended on top of video */}
            <div style={{
              position: "absolute", inset: 0,
              background: `linear-gradient(135deg, ${pal.p}22 0%, transparent 50%, ${pal.a}22 100%)`,
              mixBlendMode: "overlay" as any,
              pointerEvents: "none",
            }}/>
            {/* Glass gloss — top reflection */}
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, height: "40%",
              background: "linear-gradient(to bottom, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0.08) 60%, transparent 100%)",
              pointerEvents: "none", borderRadius: "36px 36px 0 0"
            }}/>
            {/* Bottom gradient fade */}
            <div style={{
              position: "absolute", bottom: 0, left: 0, right: 0, height: "40%",
              background: `linear-gradient(to top, ${pal.bg1}EE 0%, transparent 100%)`,
              pointerEvents: "none"
            }}/>
            {/* Neon corner accents */}
            {[["0%","0%","tl"],["100%","0%","tr"],["0%","100%","bl"],["100%","100%","br"]].map(([x,y,pos],i) => (
              <div key={i} style={{
                position: "absolute",
                left: pos.endsWith("r") ? undefined : x,
                right: pos.endsWith("r") ? "0%" : undefined,
                top: pos.startsWith("b") ? undefined : y,
                bottom: pos.startsWith("b") ? "0%" : undefined,
                width: 50, height: 50,
                borderTop: !pos.startsWith("b") ? `3px solid ${pal.p}` : undefined,
                borderBottom: pos.startsWith("b") ? `3px solid ${pal.p}` : undefined,
                borderLeft: !pos.endsWith("r") ? `3px solid ${pal.p}` : undefined,
                borderRight: pos.endsWith("r") ? `3px solid ${pal.p}` : undefined,
                boxShadow: `0 0 25px ${pal.p}, 0 0 50px ${pal.p}66`,
                opacity: 0.9, pointerEvents: "none",
              }}/>
            ))}
          </div>
        </Sequence>

        {/* Phase 3: Split Screen */}
        <Sequence from={Math.round(p3*fps)} durationInFrames={Math.round((p4-p3)*fps)}>
          <AbsoluteFill style={{ display: "flex", flexDirection: "column", padding: 14, gap: 14 }}>
            {[{src:bgVideo1, flip:true, col:pal.p, col2:pal.g},{src:bgVideo2, flip:false, col:pal.a, col2:pal2.p}].map(({src,flip,col,col2},i) => (
              <div key={i} style={{
                flex: 1, overflow: "hidden", borderRadius: 30,
                boxShadow: `0 0 0 2px ${col}99, 0 0 60px ${col}77, 0 0 120px ${col2}44`,
                position: "relative",
              }}>
                <OffthreadVideo src={staticFile(src)} style={{
                  width: "100%", height: "100%", objectFit: "cover",
                  transform: flip ? "scaleX(-1)" : undefined,
                  filter: `saturate(2.0) contrast(1.3) brightness(1.15) hue-rotate(${flip ? "15deg" : "-10deg"})`
                }}/>
                {/* Color blend overlay per panel */}
                <div style={{
                  position: "absolute", inset: 0,
                  background: `linear-gradient(135deg, ${col}33, transparent 60%, ${col2}22)`,
                  mixBlendMode: "screen" as any,
                  pointerEvents: "none"
                }}/>
              </div>
            ))}
          </AbsoluteFill>
        </Sequence>

        {/* Phase 4 & 5: Climax */}
        <Sequence from={Math.round(p4*fps)}>
          {shatterActive ? (
            <AbsoluteFill style={{ display: "flex", flexWrap: "wrap" }}>
              {Array.from({length:4}).map((_,i) => (
                <div key={i} style={{
                  width: "50%", height: "50%", overflow: "hidden",
                  transform: `scale(${1 + random(i) * 0.3}) rotate(${(random(i) - 0.5) * 30}deg) translate(${(random(i) - 0.5) * 140}px,${(random(i) - 0.5) * 140}px)`,
                  border: `4px solid ${PALETTES[i % PALETTES.length].p}`,
                  filter: `hue-rotate(${i * 60}deg) saturate(2.5) brightness(1.2)`
                }}>
                  <OffthreadVideo src={staticFile(bgVideo2)} style={{ width: "200%", height: "200%", objectFit: "cover", transform: `translate(-${(i%2)*50}%,-${Math.floor(i/2)*50}%)` }}/>
                </div>
              ))}
            </AbsoluteFill>
          ) : (
            <AbsoluteFill>
              {/* Animated scan pulse lines */}
              <div style={{ position: "absolute", inset: 0, background: `repeating-linear-gradient(0deg,transparent,transparent 44px,${pal.p}22 44px,${pal.p}22 48px)`, transform: `translateY(${(frame * 4) % 48}px)`, opacity: 0.5 }}/>
              {/* Climax Screen */}
              <div style={{
                position: "absolute", top: "15%", left: "3%", width: "94%", height: "62%",
                transform: `scale(${spring({fps, frame: frame - (Math.round(p4 * fps) + 12), config: { damping: 14 }})})`,
                borderRadius: 44, overflow: "hidden",
                boxShadow: `
                  0 0 0 3px rgba(255,255,255,0.4),
                  0 0 80px ${pal.a},
                  0 0 160px ${pal.p},
                  0 0 240px ${pal.g}66,
                  0 80px 160px rgba(0,0,0,0.95)
                `,
              }}>
                <OffthreadVideo src={staticFile(bgVideo1)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(2.2) contrast(1.35) brightness(1.2)" }}/>
                {/* Climax color blend */}
                <div style={{
                  position: "absolute", inset: 0,
                  background: `linear-gradient(180deg, ${pal.p}33 0%, transparent 40%, ${pal.a}33 100%)`,
                  mixBlendMode: "overlay" as any,
                  pointerEvents: "none"
                }}/>
                <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "35%", background: "linear-gradient(to bottom,rgba(255,255,255,0.3),transparent)", pointerEvents: "none" }}/>
              </div>
              {/* PAYOUT */}
              <div style={{ position: "absolute", bottom: "5%", width: "94%", left: "3%", textAlign: "center" }}>
                <div style={{
                  fontSize: 100, fontFamily: TITLE_FONT, fontWeight: 900,
                  background: `linear-gradient(90deg,${pal.p},${pal.a},${pal.g},${pal2.p})`,
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                  filter: `drop-shadow(0 0 40px ${pal.a}) drop-shadow(0 0 80px ${pal.p})`,
                  letterSpacing: 4
                }}>
                  PAYOUT: {serotonin.toLocaleString()}
                </div>
              </div>
            </AbsoluteFill>
          )}
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

      {/* ── LAYER 4: NEURAL ALERT ────────────────────────────────── */}
      {(phase === 2 || phase === 3) && (
        <AbsoluteFill style={{ zIndex: 150, pointerEvents: "none" }}>
          <div style={{
            position: "absolute", top: "4%", left: "3%", width: "94%",
            padding: "14px 24px",
            background: alertFlash
              ? `linear-gradient(90deg, ${pal.p}EE, ${pal.g}EE, ${pal.a}EE)`
              : `${pal.bg1}CC`,
            border: `3px solid ${alertFlash ? "rgba(255,255,255,0.95)" : pal.p}`,
            borderRadius: 22,
            textAlign: "center",
            fontFamily: TITLE_FONT, fontSize: 50, letterSpacing: 5, fontWeight: 900,
            color: alertFlash ? "#fff" : pal.p,
            textShadow: alertFlash
              ? `0 0 30px white, 0 0 60px ${pal.p}, 0 0 90px ${pal.g}`
              : `0 0 20px ${pal.p}, 0 0 40px ${pal.g}`,
            boxShadow: alertFlash
              ? `0 0 60px ${pal.p}99, 0 0 100px ${pal.g}55, inset 0 1px 0 rgba(255,255,255,0.4)`
              : "none",
            backdropFilter: "blur(8px)",
          }}>
            {alertText}
          </div>
        </AbsoluteFill>
      )}

      {/* ── LAYER 5: SEROTONIN COUNTER ───────────────────────────── */}
      <Sequence from={Math.round(p2*fps)} durationInFrames={Math.round((p4-p2)*fps)}>
        <AbsoluteFill style={{ zIndex: 160, pointerEvents: "none", justifyContent: "flex-end", alignItems: "center", paddingBottom: 55 }}>
          <div style={{
            fontFamily: TITLE_FONT, fontSize: 92, fontWeight: 900, letterSpacing: 3,
            background: `linear-gradient(90deg,${pal.p},${pal.a},${pal.g})`,
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            filter: `drop-shadow(0 0 30px ${pal.p}) drop-shadow(0 0 60px ${pal.a})`,
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

      {/* ── LAYER 8: HD CAPTION ENGINE ───────────────────────────── */}
      {/* Positioned at BOTTOM 30% — not center — clean gradient text, NO box background */}
      <AbsoluteFill style={{ zIndex: 300, justifyContent: "flex-end", alignItems: "center", paddingBottom: "18%", pointerEvents: "none" }}>
        {word && (() => {
          const elapsed = t - word.start;
          const ai = wordIdx % 6;
          let tf = "";
          let op = 1;

          if (ai === 0) tf = `scale(${spring({fps, frame: frame - Math.round(word.start * fps), config: {damping: 12}})})`;
          else if (ai === 1) tf = `translate(${Math.sin(frame) * 10}px,${Math.cos(frame) * 8}px) scale(1.06)`;
          else if (ai === 2) { op = frame % 4 < 2 ? 1 : 0.6; tf = `scale(1.12)`; }
          else if (ai === 3) {
            const rx = interpolate(elapsed, [0, 0.18], [-80, 0], {extrapolateRight: "clamp"});
            tf = `perspective(600px) rotateX(${rx}deg)`;
          } else if (ai === 4) {
            const s = interpolate(elapsed, [0, 0.18], [2.0, 1], {extrapolateRight: "clamp"});
            tf = `scale(${s})`;
          } else {
            tf = `scale(${spring({fps, frame: frame - Math.round(word.start * fps), config: {stiffness: 280, damping: 12}})}) rotate(${wordIdx % 2 === 0 ? 7 : -7}deg)`;
          }

          if (isRed) {
            return (
              <div style={{
                fontFamily: TITLE_FONT, fontSize: 108, fontWeight: 900,
                background: `linear-gradient(135deg,#FF0044,#FF6600,#FFD700)`,
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                filter: `drop-shadow(0 0 20px #FF0044) drop-shadow(0 0 40px #FF6600) drop-shadow(0 4px 8px black)`,
                transform: tf, opacity: op,
                textAlign: "center", maxWidth: "92%",
                lineHeight: 1.1, letterSpacing: 5,
              }}>
                {word.word.toUpperCase()}
              </div>
            );
          } else {
            // Hindi word — vibrant gradient color, strong glow, NO background box
            const colors = [
              `linear-gradient(135deg,#FFFFFF,${pal.p})`,
              `linear-gradient(135deg,${pal.p},${pal.a})`,
              `linear-gradient(135deg,${pal.a},${pal.g})`,
              `linear-gradient(135deg,${pal.g},#FFFFFF)`,
              `linear-gradient(135deg,${pal2.p},${pal2.a})`,
              `linear-gradient(135deg,#FFD700,#FF5500)`,
            ];
            const wordGrad = colors[wordIdx % colors.length];
            const glowCol = [pal.p, pal.a, pal.g, "#FFFFFF", pal2.p, "#FFD700"][wordIdx % 6];
            return (
              <div style={{
                fontFamily: HINDI_FONT, fontSize: 88, fontWeight: 900,
                background: wordGrad,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter: `drop-shadow(0 0 12px ${glowCol}) drop-shadow(0 0 30px ${glowCol}88) drop-shadow(0 4px 8px rgba(0,0,0,0.9))`,
                transform: tf, opacity: op,
                textAlign: "center", maxWidth: "92%",
                lineHeight: 1.2, letterSpacing: 2,
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
