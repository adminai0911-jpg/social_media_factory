import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  Img,
  random,
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

const RED_WORDS = ["WAKE","SIMULATION","SHADOWS","TRAP","LYING","FAKE","DREAM","FEAR","PANIC","NOW","LIES","BREAK","SCAM","CHEAT","DANGER"];

export const MainVideo: React.FC<{
  script: any;
  timings: any[];
  audio_offsets: number[];
  total_duration: number;
}> = ({ script, timings, audio_offsets, total_duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // We need 8 audio offsets now
  if (!script || !audio_offsets || audio_offsets.length < 8) return null;

  const seed       = script.style_seed || 1;
  const pal        = PALETTES[seed % PALETTES.length];
  const redKw      = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9]/g,"") : "WARNING";
  const activeRedWords = [...RED_WORDS, redKw];

  // Map 8-phase audio offsets
  const [, p2, p3, p_l1, p_l2, p_l3, p_proof, p_cta] = audio_offsets;
  
  let phase = 1;
  if (t >= p2 && t < p3) phase = 2;
  else if (t >= p3 && t < p_l1) phase = 3;
  else if (t >= p_l1 && t < p_proof) phase = 4;
  else if (t >= p_proof && t < p_cta) phase = 5;
  else if (t >= p_cta) phase = 6;

  // Captions System
  const wordIdx = timings.findIndex(w => t >= w.start && t <= w.end + 0.1);
  const wordObj = timings[wordIdx];
  const isRed   = wordObj ? activeRedWords.some(r => wordObj.word.toUpperCase().replace(/[^A-Z0-9]/g,"").includes(r)) : false;

  const isVHS         = frame % 50 > 46;
  const shatterActive = phase === 4 && frame < Math.round(p_l1 * fps) + 12;

  const shakeAmt = isRed ? 14 : shatterActive ? 35 : (isVHS ? 4 : 0);
  const sx = shakeAmt > 0 ? (random(frame)     - 0.5) * shakeAmt : 0;
  const sy = shakeAmt > 0 ? (random(frame + 1) - 0.5) * shakeAmt : 0;

  // Helper for Ken Burns Scale
  const kenBurns = (startOffset: number) => {
    return interpolate(frame, [Math.round(startOffset * fps), Math.round((startOffset + 6) * fps)], [1, 1.05], { extrapolateRight: "clamp" });
  };

  return (
    <AbsoluteFill style={{
      backgroundColor: pal.bg1,
      transform: `translate(${sx}px,${sy}px)`
    }}>
      <GlobalStyle />

      {/* ── AUDIO SEQUENCES (8 parts) ─────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("v32_audio_0.mp3")} volume={1.6} /></Sequence>
      {p2 && <Sequence from={Math.round(p2*fps)}><Audio src={staticFile("v32_audio_1.mp3")} volume={1.6} /></Sequence>}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("v32_audio_2.mp3")} volume={1.6} /></Sequence>}
      {p_l1 && <Sequence from={Math.round(p_l1*fps)}><Audio src={staticFile("v32_audio_3.mp3")} volume={1.6} /></Sequence>}
      {p_l2 && <Sequence from={Math.round(p_l2*fps)}><Audio src={staticFile("v32_audio_4.mp3")} volume={1.6} /></Sequence>}
      {p_l3 && <Sequence from={Math.round(p_l3*fps)}><Audio src={staticFile("v32_audio_5.mp3")} volume={1.6} /></Sequence>}
      {p_proof && <Sequence from={Math.round(p_proof*fps)}><Audio src={staticFile("v32_audio_6.mp3")} volume={1.6} /></Sequence>}
      {p_cta && <Sequence from={Math.round(p_cta*fps)}><Audio src={staticFile("v32_audio_7.mp3")} volume={1.6} /></Sequence>}
      
      {/* ── SFX ─────────────────────────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("hypno.wav")} volume={0.15} loop /></Sequence>
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("riser.wav")} volume={0.5}/></Sequence>}
      {/* Ticks for staggered list items */}
      {p_l1 && <Sequence from={Math.round(p_l1*fps)}><Audio src={staticFile("ding.wav")} volume={1.5}/></Sequence>}
      {p_l2 && <Sequence from={Math.round(p_l2*fps)}><Audio src={staticFile("ding.wav")} volume={1.5}/></Sequence>}
      {p_l3 && <Sequence from={Math.round(p_l3*fps)}><Audio src={staticFile("ding.wav")} volume={1.5}/></Sequence>}
      {p_proof && <Sequence from={Math.round(p_proof*fps)}><Audio src={staticFile("impact.wav")} volume={1.5}/></Sequence>}
      {p_cta && <Sequence from={Math.round(p_cta*fps)}><Audio src={staticFile("impact.wav")} volume={2.0}/></Sequence>}

      {/* ── PREMIUM BACKGROUND & GRAIN ───────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 0, backgroundColor: pal.bg1 }}>
        <div style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.6) 100%)`,
        }}/>
        {/* Subtle noise texture */}
        <div style={{
          position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "overlay",
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}/>
      </AbsoluteFill>

      {/* ── WATERMARK ────────────────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 9999 }}>
        <div style={{ position: "absolute", bottom: 40, right: 40, fontFamily: TITLE_FONT, fontSize: 30, color: "rgba(255,255,255,0.2)", fontWeight: 900, letterSpacing: 2 }}>
          @adminAI_0911
        </div>
      </AbsoluteFill>

      {/* ── PHASE 1: HOOK (0 - p2) ────────────────────────────────── */}
      <Sequence from={0} durationInFrames={Math.round(p2*fps)}>
        <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: 60, transform: `scale(${kenBurns(0)})` }}>
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
      <Sequence from={Math.round(p2*fps)} durationInFrames={Math.round((p3-p2)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "row", transform: `scale(${kenBurns(p2)})` }}>
          {/* LEFT: Poor Mindset */}
          <div style={{ flex: 1, borderRight: "2px solid rgba(255,255,255,0.1)", display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "25%", opacity: interpolate(frame, [p2*fps, p2*fps+15], [0, 1]) }}>
            <div style={{ fontFamily: TITLE_FONT, fontSize: 45, color: "rgba(255,255,255,0.5)", letterSpacing: 2, marginBottom: 40, transform: `translateY(${interpolate(frame, [p2*fps, p2*fps+15], [20, 0])}px)` }}>POOR MINDSET</div>
            <div style={{ fontSize: 180, marginBottom: 60, transform: `scale(${interpolate(frame, [p2*fps, p2*fps+20], [0.8, 1])})` }}>😞</div>
            <div style={{ fontFamily: HINDI_FONT, fontSize: 60, color: "#FFFFFF", textAlign: "center", padding: 40 }}>
              {script.split_screen?.left?.split("-")[1] || "Saves money"}
            </div>
          </div>
          {/* RIGHT: Rich Mindset */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: "25%", opacity: interpolate(frame, [p2*fps+15, p2*fps+30], [0, 1], {extrapolateLeft: "clamp"}) }}>
            <div style={{ fontFamily: TITLE_FONT, fontSize: 45, color: pal.p, letterSpacing: 2, marginBottom: 40, transform: `translateY(${interpolate(frame, [p2*fps+15, p2*fps+30], [20, 0], {extrapolateLeft: "clamp"})}px)` }}>RICH MINDSET</div>
            <div style={{ fontSize: 180, marginBottom: 60, transform: `scale(${interpolate(frame, [p2*fps+15, p2*fps+35], [0.8, 1], {extrapolateLeft: "clamp"})})` }}>🧠</div>
            <div style={{ fontFamily: HINDI_FONT, fontSize: 60, color: "#FFFFFF", textAlign: "center", padding: 40 }}>
              {script.split_screen?.right?.split("-")[1] || "Invests money"}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 3: AUTHORITY CLAIM (p3 - p_l1) ──────────────────── */}
      <Sequence from={Math.round(p3*fps)} durationInFrames={Math.round((p_l1-p3)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, gap: 60, transform: `scale(${kenBurns(p3)})` }}>
          <div style={{
            width: 420, height: 420, borderRadius: "50%",
            overflow: "hidden", border: `6px solid ${pal.p}`,
            boxShadow: `0 0 0 3px ${pal.bg1}, 0 0 0 9px ${pal.p}55, 0 0 80px ${pal.p}44`, flexShrink: 0
          }}>
            <Img src={staticFile("host_photo.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center top" }} />
          </div>
          <div style={{
            fontFamily: HINDI_FONT, fontSize: 75, fontWeight: 700, color: "#FFFFFF",
            textAlign: "center", lineHeight: 1.3, maxWidth: "90%"
          }}>
            {script.authority_claim}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 4: STAGGERED NUMBERED LIST (p_l1 - p_proof) ───────── */}
      <Sequence from={Math.round(p_l1*fps)} durationInFrames={Math.round((p_proof-p_l1)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "10% 8%", transform: `scale(${kenBurns(p_l1)})` }}>
          {(script.numbered_list || []).map((item: string, i: number) => {
            const itemTime = i === 0 ? p_l1 : i === 1 ? p_l2 : p_l3;
            if (t < itemTime) return null; // Staggered reveal
            
            return (
              <div key={i} style={{
                display: "flex", alignItems: "center",
                background: "rgba(255,255,255,0.05)",
                padding: "40px 50px", borderRadius: 30, marginBottom: 40,
                border: "1px solid rgba(255,255,255,0.08)",
                boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
                opacity: interpolate(frame, [Math.round(itemTime*fps), Math.round(itemTime*fps)+15], [0, 1], {extrapolateLeft: "clamp"}),
                transform: `translateX(${interpolate(frame, [Math.round(itemTime*fps), Math.round(itemTime*fps)+15], [-50, 0], {extrapolateLeft: "clamp"})}px)`
              }}>
                <div style={{
                  width: 90, height: 90, borderRadius: "50%", background: pal.p,
                  display: "flex", justifyContent: "center", alignItems: "center",
                  fontFamily: TITLE_FONT, fontSize: 50, fontWeight: 900, color: pal.bg1,
                  marginRight: 40, flexShrink: 0
                }}>
                  {i + 1}
                </div>
                <div style={{
                  fontFamily: HINDI_FONT, fontSize: 68, fontWeight: 700, color: "#FFFFFF", lineHeight: 1.2
                }}>
                  {item}
                </div>
              </div>
            );
          })}
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 5: PROOF/DEMO (p_proof - p_cta) ────────────────── */}
      <Sequence from={Math.round(p_proof*fps)} durationInFrames={Math.round((p_cta-p_proof)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, transform: `scale(${kenBurns(p_proof)})` }}>
          <div style={{
            border: `2px solid rgba(255,255,255,0.2)`, borderRadius: 30, padding: "80px 60px", width: "95%",
            display: "flex", flexDirection: "column", alignItems: "center",
            background: "rgba(0,0,0,0.6)", backdropFilter: "blur(20px)",
            boxShadow: `0 30px 60px rgba(0,0,0,0.8), inset 0 0 100px rgba(255,255,255,0.05)`
          }}>
            <div style={{ fontSize: 130, marginBottom: 40 }}>📊</div>
            <div style={{
              fontFamily: TITLE_FONT, fontSize: 50, fontWeight: 900,
              color: "rgba(255,255,255,0.5)", letterSpacing: 4, marginBottom: 30
            }}>
              FACT CHECK
            </div>
            <div style={{
              fontFamily: HINDI_FONT, fontSize: 75, fontWeight: 700,
              color: pal.p, textAlign: "center", lineHeight: 1.3
            }}>
              {script.proof_demo}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 6: SAVE CARD & CTA (p_cta - end) ────────────────── */}
      <Sequence from={Math.round(p_cta*fps)}>
        <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: 60, transform: `scale(${kenBurns(p_cta)})` }}>
          <div style={{
            border: `4px solid ${pal.p}`, borderRadius: 40, padding: "70px 60px", width: "95%",
            display: "flex", flexDirection: "column", alignItems: "center",
            boxShadow: `0 0 80px ${pal.p}44, 0 0 200px ${pal.p}22`,
            background: "rgba(0,0,0,0.5)"
          }}>
            <div style={{ fontSize: 110, marginBottom: 30 }}>🔖</div>
            <div style={{
              fontFamily: TITLE_FONT, fontSize: 75, fontWeight: 900,
              color: pal.p, letterSpacing: 4, marginBottom: 40, textAlign: "center"
            }}>
              SAVE KARO
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: 20, width: "100%", alignItems: "flex-start", marginBottom: 60 }}>
              {(script.numbered_list || []).map((item: string, i: number) => (
                <div key={i} style={{
                  fontFamily: HINDI_FONT, fontSize: 45, color: "rgba(255,255,255,0.7)",
                  fontWeight: 600, display: "flex", alignItems: "center", gap: 20
                }}>
                  <span style={{ color: pal.p, fontFamily: TITLE_FONT, fontWeight: 900, fontSize: 45 }}>{i + 1}.</span>
                  {item}
                </div>
              ))}
            </div>

            <div style={{
              fontFamily: HINDI_FONT, fontSize: 65, fontWeight: 900,
              color: "#FFFFFF", textAlign: "center", borderTop: `2px solid rgba(255,255,255,0.1)`, paddingTop: 40, width: "100%"
            }}>
              {script.save_cta}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── DYNAMIC SUBTITLES ────────────────────────────────────── */}
      {/* We don't show subtitles during the Hook (too much text overlap) or the CTA */}
      {phase > 1 && phase < 6 && wordObj && (
        <AbsoluteFill style={{ zIndex: 9998, justifyContent: "flex-end", alignItems: "center", paddingBottom: 150 }}>
          <div style={{
            background: "rgba(0,0,0,0.8)", padding: "20px 40px", borderRadius: 20,
            border: `2px solid ${pal.p}55`,
            boxShadow: "0 10px 40px rgba(0,0,0,0.8)",
            transform: `scale(${interpolate(frame, [Math.round(wordObj.start*fps), Math.round(wordObj.start*fps)+5], [0.9, 1], {extrapolateLeft: "clamp"})})`
          }}>
            <span style={{ fontFamily: HINDI_FONT, fontSize: 65, fontWeight: 900, color: isRed ? pal.p : "#FFFFFF" }}>
              {wordObj.word.toUpperCase()}
            </span>
          </div>
        </AbsoluteFill>
      )}

      {/* ── FADE OUT ────────────────────────────────────────────── */}
      {phase === 6 && (
        <AbsoluteFill style={{
          zIndex: 1000, backgroundColor: "black",
          opacity: interpolate(frame, [total_duration * fps - 15, total_duration * fps], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})
        }}/>
      )}
    </AbsoluteFill>
  );
};

