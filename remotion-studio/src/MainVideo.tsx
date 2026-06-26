import {
  AbsoluteFill,
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
  Img,
  random,
  Sequence,
} from "remotion";

import React, { useMemo } from "react";

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

const BilingualText: React.FC<{ text: string }> = ({ text }) => {
  if (!text) return null;
  // Split on Latin characters, numbers, and common symbols (like %, ₹)
  const parts = text.split(/([a-zA-Z0-9₹%]+(?:[ \-][a-zA-Z0-9₹%]+)*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (/[a-zA-Z0-9₹%]/.test(part)) {
          return <span key={i} style={{ margin: "0 6px", fontFamily: TITLE_FONT, fontWeight: 700, letterSpacing: 1 }}>{part}</span>;
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
};

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



  // We need 7 audio offsets now (split screen removed)
  if (!script || !audio_offsets || audio_offsets.length < 7) return null;

  const seed       = script.style_seed || 1;
  const pal        = PALETTES[seed % PALETTES.length];
  const redKw      = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9]/g,"") : "WARNING";
  const activeRedWords = [...RED_WORDS, redKw];

  // Map 7-phase audio offsets (with safe fallbacks to total_duration if missing)
  const [,
    p_auth = total_duration,
    p_l1 = total_duration,
    p_l2 = total_duration,
    p_l3 = total_duration,
    p_proof = total_duration,
    p_cta = total_duration
  ] = audio_offsets;
  
  let phase = 1;
  if (t >= p_auth && t < p_l1) phase = 2;
  else if (t >= p_l1 && t < p_proof) phase = 3;
  else if (t >= p_proof && t < p_cta) phase = 4;
  else if (t >= p_cta && t < p_cta + 2.5) phase = 5;
  else if (t >= p_cta + 2.5) phase = 6;



  const wordIdx = timings.findIndex(w => t >= w.start && t <= w.end + 0.1);
  const wordObj = timings[wordIdx];
  const isRed   = wordObj ? activeRedWords.some(r => wordObj.word.toUpperCase().replace(/[^A-Z0-9]/g,"").includes(r)) : false;

  const subtitleChunks = useMemo(() => {
    if (!timings) return [];
    const chunks = [];
    for (let i = 0; i < timings.length; i += 4) {
      const slice = timings.slice(i, i + 4);
      chunks.push({
        start: slice[0].start,
        end: slice[slice.length - 1].end + 0.1,
        words: slice
      });
    }
    return chunks;
  }, [timings]);

  const activeChunk = subtitleChunks.find(c => t >= c.start && t <= c.end);



  const isVHS         = frame % 50 > 46;

  const shatterActive = phase === 4 && frame < Math.round(p_l1 * fps) + 12;



  const shakeAmt = isRed ? 14 : shatterActive ? 35 : (isVHS ? 4 : 0);

  const sx = shakeAmt > 0 ? (random(frame)     - 0.5) * shakeAmt : 0;

  const sy = shakeAmt > 0 ? (random(frame + 1) - 0.5) * shakeAmt : 0;



  // Helper for Ken Burns Scale (continuous slow zoom)
  const kenBurns = (startOffset: number) => {
    return interpolate(frame, [Math.round(startOffset * fps), Math.round((startOffset + 8) * fps)], [1.0, 1.08], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  };

  // Particle drift offset for background grain

  const grainX = Math.sin(frame * 0.03) * 3;

  const grainY = Math.cos(frame * 0.02) * 3;



  return (

    <AbsoluteFill style={{

      backgroundColor: pal.bg1,

      transform: `translate(${sx}px,${sy}px)`

    }}>

      <GlobalStyle />



      {/* ── AUDIO SEQUENCES (7 parts) ─────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("v32_audio_0.mp3")} volume={1.6} /></Sequence>
      {p_auth && <Sequence from={Math.round(p_auth*fps)}><Audio src={staticFile("v32_audio_1.mp3")} volume={1.6} /></Sequence>}
      {p_l1 && <Sequence from={Math.round(p_l1*fps)}><Audio src={staticFile("v32_audio_2.mp3")} volume={1.6} /></Sequence>}
      {p_l2 && <Sequence from={Math.round(p_l2*fps)}><Audio src={staticFile("v32_audio_3.mp3")} volume={1.6} /></Sequence>}
      {p_l3 && <Sequence from={Math.round(p_l3*fps)}><Audio src={staticFile("v32_audio_4.mp3")} volume={1.6} /></Sequence>}
      {p_proof && <Sequence from={Math.round(p_proof*fps)}><Audio src={staticFile("v32_audio_5.mp3")} volume={1.6} /></Sequence>}
      {p_cta && <Sequence from={Math.round(p_cta*fps)}><Audio src={staticFile("v32_audio_6.mp3")} volume={1.6} /></Sequence>}

      {/* Background Music directly in Remotion */}
      <Audio src={staticFile("hypno.wav")} volume={0.10} />

      {/* ── PREMIUM BACKGROUND & DRIFTING GRAIN ────────────────────── */}

      <AbsoluteFill style={{ zIndex: 0, backgroundColor: pal.bg1 }}>

        <div style={{
          position: "absolute", inset: 0,
          background: `rgba(0,0,0,0.3)`,
        }}/>

        {/* Animated drifting grain — eliminates dead static frames */}

        <div style={{

          position: "absolute", inset: 0, opacity: 0.07, mixBlendMode: "overlay",

          transform: `translate(${grainX}px, ${grainY}px) scale(1.05)`,

          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`

        }}/>

      </AbsoluteFill>



      {/* ── WATERMARK ────────────────────────────────────────────── */}

      <AbsoluteFill style={{ zIndex: 9999 }}>

        <div style={{ position: "absolute", bottom: 40, right: 40, fontFamily: TITLE_FONT, fontSize: 30, color: "rgba(255,255,255,0.2)", fontWeight: 900, letterSpacing: 2 }}>

          @adminAI_0911

        </div>

      </AbsoluteFill>



      {/* ── PHASE 1: HOOK (0 - p_auth) ────────────────────────────────── */}
      <Sequence from={0} durationInFrames={Math.round(p_auth*fps)}>
        <AbsoluteFill style={{
          display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center",
          padding: "60px 40px",
          transform: `scale(${kenBurns(0)})`
        }}>
          <div style={{
             display: "flex", flexDirection: "column", alignItems: "center", gap: 30, width: "100%",
             opacity: interpolate(frame, [0, 10], [0, 1], {extrapolateLeft:"clamp", extrapolateRight:"clamp"}),
             transform: `translateY(${interpolate(frame, [0, 15], [20, 0], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})}px)`
          }}>
            <div style={{ fontFamily: HOOK_FONT, fontSize: 100, fontWeight: 900, color: "#FFFFFF", textAlign: "center", lineHeight: 1.15 }}>
              {(() => {
                const hookText = script.hook || script.phase_1 || "";
                if (!hookText.trim()) throw new Error("Render Validation Failed: Hook text is completely empty.");
                const words = hookText.split(/\s+/).filter(Boolean);
                return words.map((w: string, i: number) => {
                  const hi = activeRedWords.some(r => w.toUpperCase().includes(r)) || i === 0 || i === Math.floor(words.length / 2);
                  const isBgColor = (seed % 3) === 1;
                  return (
                    <span key={i} style={{ 
                      color: hi && !isBgColor ? pal.p : (hi && isBgColor ? pal.bg1 : "#FFFFFF"),
                      backgroundColor: hi && isBgColor ? pal.p : "transparent",
                      padding: hi && isBgColor ? "0 20px" : "0",
                      display: "inline-block", marginRight: 18, marginBottom: 15, borderRadius: 15
                    }}>{w}</span>
                  );
                });
              })()}
            </div>
          </div>
          
          {/* Small Corner Badge Profile Photo */}
          <div style={{ position: "absolute", bottom: 60, left: 60, display: "flex", alignItems: "center", gap: 20 }}>
            <div style={{ width: 100, height: 100, borderRadius: "50%", overflow: "hidden", border: `4px solid ${pal.p}`, boxShadow: `0 10px 30px rgba(0,0,0,0.5)` }}>
              <Img src={staticFile("wealth_profile_photo.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center top" }} />
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>


      {/* UPGRADE #4: CURIOSITY LOOP — planted early, exits 0.5s before Rule 1 to avoid numeric claims collision */}
      {t >= 2.0 && t < (p_l1 - 0.5) && script.curiosity_teaser && (
        <AbsoluteFill style={{ zIndex: 9997, justifyContent: "flex-start",
          alignItems: "center", paddingTop: 250 }}>
          <div style={{
            background: "rgba(12,20,32,0.97)",
            border: `2px solid ${pal.p}66`,
            borderRadius: 16, padding: "14px 36px",
            boxShadow: `0 0 30px ${pal.p}22`,
            opacity: interpolate(frame,
              [Math.round(2.0*fps), Math.round(2.5*fps)], [0, 1],
              {extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
            display: "flex", alignItems: "center", gap: 16
          }}>
            <span style={{ color: pal.p, fontSize: 32,
              fontFamily: TITLE_FONT, fontWeight: 900 }}>❓</span>
            <span style={{ fontFamily: HINDI_FONT, fontSize: 42,
              color: "#FFFFFF", fontWeight: 700 }}>
              {script.curiosity_teaser}
            </span>
          </div>
        </AbsoluteFill>
      )}

      {/* CURIOSITY PAYOFF — explicit resolution at start of proof (closes the loop) */}
      {t >= p_proof && t < (p_proof + 2.5) && script.curiosity_payoff && (
        <AbsoluteFill style={{ zIndex: 9990, justifyContent: "flex-start",
          alignItems: "center", paddingTop: 80 }}>
          <div style={{
            background: `${pal.p}18`,
            border: `2px solid ${pal.p}`,
            borderRadius: 16, padding: "14px 40px",
            boxShadow: `0 0 40px ${pal.p}44`,
            opacity: interpolate(frame,
              [Math.round(p_proof*fps), Math.round(p_proof*fps)+8], [0, 1],
              {extrapolateLeft:"clamp",extrapolateRight:"clamp"})
          }}>
            <span style={{ fontFamily: HINDI_FONT, fontSize: 44,
              color: pal.p, fontWeight: 700 }}>
              {script.curiosity_payoff}
            </span>
          </div>
        </AbsoluteFill>
      )}


      {/* ── PHASE 2: AUTHORITY CLAIM (p_auth - p_l1) ──────────────────── */}

      <Sequence from={Math.round(p_auth*fps)} durationInFrames={Math.round((p_l1-p_auth)*fps)}>

        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, gap: 60, transform: `scale(${kenBurns(p_auth)})` }}>

          {/* Animated face: head-bob + breathing pulse ring = never looks frozen */}
          <div style={{
            width: 380, height: 380, borderRadius: "50%", overflow: "hidden",
            border: `6px solid ${pal.p}`,
            boxShadow: `0 0 0 ${4 + Math.sin(frame*0.1)*5}px ${pal.p}44, 0 0 80px ${pal.p}44`,
            transform: `translateY(${Math.sin(frame*0.07)*5}px) rotate(${Math.sin(frame*0.04)*1.2}deg)`,
            flexShrink: 0
          }}>
            <Img src={staticFile(`host_photo_${(seed % 3) + 1}.png`)}
              style={{ width:"100%", height:"100%", objectFit:"cover",
                objectPosition:"center top",
                transform:`scale(${1.02 + Math.sin(frame*0.05)*0.015}) translateY(${Math.cos(frame*0.06)*3}px)` }} />
          </div>
          <div style={{
            fontFamily: HINDI_FONT, fontSize: 75, fontWeight: 700, color: "#FFFFFF",
            textAlign: "center", lineHeight: 1.4, maxWidth: "90%"
          }}>
            <BilingualText text={script.authority_claim} />
          </div>

        </AbsoluteFill>

      </Sequence>



      {/* ── PHASE 4: STAGGERED NUMBERED LIST (p_l1 - p_proof) ───────── */}

      <Sequence from={Math.round(p_l1*fps)} durationInFrames={Math.round((p_proof - p_l1)*fps)}>

        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "flex-start", alignItems: "center", paddingTop: 180, gap: 30, transform: `scale(${kenBurns(p_l1)})` }}>
          {(Array.isArray(script.numbered_list) ? script.numbered_list : []).slice(0, 3).map((itemRaw: any, i: number) => {
            const itemTime = i === 0 ? p_l1 : i === 1 ? p_l2 : p_l3;
            const endTime = p_proof;
            if (t < itemTime || t >= endTime) return null;
            const slideProgress = interpolate(frame, [Math.round(itemTime*fps), Math.round(itemTime*fps)+18], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
            const continuousScale = 1.0 + (frame - Math.round(itemTime*fps)) * 0.0003;
            const pulseOpacity = 0.5 + Math.sin(frame * 0.05) * 0.3;

            // Handle both legacy string arrays and new object arrays
            const item = typeof itemRaw === 'string' ? { text: itemRaw, type: i === 2 ? "DATA" : "INSIGHT", source: i === 2 ? script.source_tag : "" } : itemRaw;
            const isData = item.type === "DATA" || i === 2;

            return (
              <div key={i} style={{
                display: "flex", alignItems: "center", width: "90%",
                background: isData ? `rgba(15,32,39,0.7)` : "rgba(255,255,255,0.05)",
                padding: "25px 40px", borderRadius: 30,
                border: isData ? `2px solid rgba(0, 242, 254, ${pulseOpacity})` : "1px solid rgba(255,255,255,0.08)",
                boxShadow: isData ? `0 10px 40px rgba(0,242,254,0.2)` : "0 10px 30px rgba(0,0,0,0.5)",
                opacity: slideProgress,
                transform: `translateX(${interpolate(slideProgress, [0, 1], [-80, 0])}px) scale(${continuousScale * 0.75})`,
                position: "relative",
                marginBottom: 20
              }}>
                {/* Type Tag */}
                <div style={{
                  position: "absolute", top: -20, left: 50,
                  background: isData ? "#00F2FE" : "#8A2387",
                  color: isData ? "#0F2027" : "#FFFFFF",
                  fontFamily: TITLE_FONT, fontSize: 22, fontWeight: 900,
                  padding: "6px 16px", borderRadius: 12, letterSpacing: 2,
                  boxShadow: `0 8px 20px ${isData ? "rgba(0,242,254,0.4)" : "rgba(138,35,135,0.4)"}`
                }}>
                  {isData ? "📊 DATA" : "💡 INSIGHT"}
                </div>
                <div style={{
                  width: isData ? 100 : 84, height: isData ? 100 : 84, borderRadius: "50%",
                  background: isData ? "#00F2FE" : `${pal.p}20`,
                  border: isData ? "none" : `2px solid ${pal.p}55`,
                  display: "flex", justifyContent: "center", alignItems: "center",
                  fontFamily: TITLE_FONT, fontSize: isData ? 70 : 60, fontWeight: 900,
                  color: isData ? "#0F2027" : pal.p,
                  marginRight: 28, flexShrink: 0,
                  boxShadow: isData ? `0 0 30px rgba(0,242,254,0.5)` : `0 0 8px ${pal.p}33`
                }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontFamily: HINDI_FONT, fontSize: isData ? 75 : 65, fontWeight: isData ? 700 : 600, color: "#FFFFFF", lineHeight: 1.4
                  }}>
                    <BilingualText text={item.text} />
                  </div>
                  {item.source && (
                    <div style={{ fontFamily: TITLE_FONT, fontSize: 26, color: isData ? "#00F2FE" : `${pal.p}ee`, marginTop: 12, letterSpacing: 1, opacity: 0.9 }}>
                      {item.source}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

        </AbsoluteFill>

      </Sequence>



      {/* ── PHASE 5: PROOF/DEMO (p_proof + 3.0s - p_cta) ────────────────── */}
      <Sequence from={Math.round((p_proof + 3.0)*fps)} durationInFrames={Math.round((p_cta - (p_proof + 3.0))*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: "5% 8%" }}>
          {(() => {
            const fcScale = 1.0 + (frame - Math.round((p_proof + 3.0)*fps)) * 0.0004;
            const fcPulse = 0.6 + Math.sin(frame * 0.08) * 0.4;
            return (
              <div style={{
                border: `3px solid rgba(0, 242, 254, ${fcPulse})`, borderRadius: 20, padding: "70px 60px", width: "96%",
                display: "flex", flexDirection: "column", alignItems: "center",
                background: "linear-gradient(135deg, rgba(15,32,39,0.95), rgba(32,58,67,0.95), rgba(44,83,100,0.95))", 
                backdropFilter: "blur(20px)",
                boxShadow: `0 30px 60px rgba(0,0,0,0.9), 0 0 80px rgba(0,242,254,0.15)`,
                transform: `scale(${fcScale})`,
                position: "relative"
              }}>
                <div style={{
                  position: "absolute", top: -30,
                  background: "#00F2FE", color: "#0F2027",
                  fontFamily: TITLE_FONT, fontSize: 32, fontWeight: 900,
                  padding: "10px 40px", borderRadius: 12, letterSpacing: 3,
                  boxShadow: `0 10px 30px rgba(0,242,254,0.5)`
                }}>
                  ✅ VERIFIED DATA
                </div>
                
                <div style={{
                  fontFamily: HINDI_FONT, fontSize: 75, fontWeight: 700,
                  color: "#FFFFFF", textAlign: "center", lineHeight: 1.4,
                  marginTop: 20
                }}>
                  <BilingualText text={script.proof_demo} />
                </div>
                {script.proof_source && (
                  <div style={{
                    fontFamily: TITLE_FONT, fontSize: 34, color: "#00F2FE",
                    marginTop: 35, letterSpacing: 2, textAlign: "center",
                    borderTop: "1px dashed rgba(0,242,254,0.3)", paddingTop: 20, width: "80%"
                  }}>
                    📚 {script.proof_source}
                  </div>
                )}
              </div>
            );
          })()}
        </AbsoluteFill>
      </Sequence>



      {/* ── PHASE 5: SAVE CARD & CTA (p_cta - p_cta + 2.5s) ────────────────── */}
      <Sequence from={Math.round(p_cta*fps)} durationInFrames={Math.round(2.5*fps)}>
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
            
            <div style={{ 
              display: "flex", flexDirection: "column", gap: 15, width: "100%", alignItems: "flex-start", marginBottom: 40,
              opacity: interpolate(t - p_cta, [1.5, 2.5], [1, 0.4], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})
            }}>
              {(Array.isArray(script.numbered_list) ? script.numbered_list : []).slice(0, 3).map((itemRaw: any, i: number) => {
                const item = typeof itemRaw === 'string' ? itemRaw : itemRaw.text;
                return (
                <div key={i} style={{
                  fontFamily: HINDI_FONT, fontSize: 42, color: "rgba(255,255,255,0.95)",
                  fontWeight: 600, display: "flex", alignItems: "flex-start", gap: 18
                }}>
                  <span style={{ color: pal.p, fontFamily: TITLE_FONT, fontWeight: 900, fontSize: 42, flexShrink: 0, marginTop: 6 }}>{i + 1}.</span>
                  <div style={{ lineHeight: 1.3 }}><BilingualText text={item} /></div>
                </div>
              )})}
            </div>

            {/* Content-specific comment driving question */}
            <div style={{
              fontFamily: HINDI_FONT, fontSize: 46, fontWeight: 700,
              color: pal.p, textAlign: "center",
              borderTop: `2px solid ${pal.p}44`, paddingTop: 30, width: "100%", marginBottom: 20,
              opacity: interpolate(t - p_cta, [1.5, 2.0], [0, 1], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})
            }}>
              {script.comment_question || "Rule 1, 2, ya 3 — kaunsa tumne miss kiya? Comment karo 👇"}
            </div>

            <div style={{
              fontFamily: HINDI_FONT, fontSize: 52, fontWeight: 900,
              color: "#FFFFFF", textAlign: "center", width: "100%",
              opacity: interpolate(t - p_cta, [2.5, 3.0], [0, 1], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})
            }}>
              {script.save_cta}
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── PHASE 6: OUTRO (p_cta + 2.5s - end) ────────────────── */}
      <Sequence from={Math.round((p_cta + 2.5)*fps)}>
        <AbsoluteFill style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", background: pal.bg1 }}>
          <div style={{
            width: 250, height: 250, borderRadius: "50%", background: `${pal.p}22`,
            display: "flex", justifyContent: "center", alignItems: "center", marginBottom: 50,
            border: `4px solid ${pal.p}`, boxShadow: `0 0 60px ${pal.p}66`,
            transform: `scale(${interpolate(frame, [Math.round((p_cta + 2.5)*fps), Math.round((p_cta + 2.8)*fps)], [0, 1], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})})`
          }}>
            <Img src={staticFile(`host_photo_${(seed % 3) + 1}.png`)} style={{ width: 242, height: 242, borderRadius: "50%", objectFit: "cover" }} />
          </div>
          <div style={{ fontFamily: TITLE_FONT, fontSize: 60, fontWeight: 900, color: "#FFFFFF", letterSpacing: 3, marginBottom: 20 }}>
            Wealth_Matrix_Ai
          </div>
          <div style={{ fontFamily: TITLE_FONT, fontSize: 35, fontWeight: 700, color: pal.p, letterSpacing: 2 }}>
            Follow for daily money psychology ➡️
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── DYNAMIC SUBTITLES ────────────────────────────────────── */}
      {/* We don't show subtitles during the Hook (too much text overlap), or the CTA/Outro */}
      {phase > 1 && phase < 5 && activeChunk && (
        <AbsoluteFill style={{ zIndex: 9998, justifyContent: "flex-end", alignItems: "center", paddingBottom: "15%" }}>
          <div style={{
            display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "12px 20px", maxWidth: "90%", padding: "0 5%"
          }}>
            {activeChunk.words.map((wObj: any, idx: number) => {
              const isActive = t >= wObj.start && t <= wObj.end + 0.1;
              const isHighlight = activeRedWords.some(r => wObj.word.toUpperCase().replace(/[^A-Z0-9]/g,"").includes(r));
              
              // Pop-in scale from 90% to 100% when active
              const scale = isActive ? 1.0 : 0.9;
              
              const color = isActive ? (isHighlight ? "#FFE600" : "#FFFFFF") : "rgba(255,255,255,0.4)";
              return (
                <span key={idx} style={{ 
                  fontFamily: TITLE_FONT, fontSize: 55, fontWeight: 900, 
                  color, 
                  WebkitTextStroke: "2px black",
                  textShadow: "0 6px 12px rgba(0,0,0,0.6)",
                  transform: `scale(${scale})`, 
                  transition: "transform 0.1s cubic-bezier(0.175, 0.885, 0.32, 1.275), color 0.1s ease" 
                }}>
                  {wObj.word.toUpperCase()}
                </span>
              );
            })}
          </div>
        </AbsoluteFill>
      )}



      {/* ── VISUAL RETENTION OVERLAYS (THE WATCH TIME HACK) ────────── */}

      {/* 1. Progress Bar at bottom */}

      <AbsoluteFill style={{ zIndex: 9999, justifyContent: "flex-end" }}>

        <div style={{

          height: 12,

          width: `${(frame / (total_duration * fps)) * 100}%`,

          backgroundColor: "#FF0000",

          boxShadow: "0 0 20px #FF0000"

        }} />

      </AbsoluteFill>



      {/* 2. "Wait for it" Sticky Banner for the first 8 seconds */}

      {t > 1.5 && t < p_l3 && (

        <AbsoluteFill style={{ zIndex: 9999, justifyContent: "flex-start", alignItems: "center", paddingTop: 80 }}>

          <div style={{

            background: "rgba(255, 0, 0, 0.9)",

            padding: "15px 40px",

            borderRadius: 15,

            boxShadow: "0 10px 40px rgba(255,0,0,0.8)",

            border: "3px solid #FFFFFF",

          }}>

            <span style={{ fontFamily: TITLE_FONT, fontSize: 45, fontWeight: 900, color: "#FFFFFF", letterSpacing: 2 }}>

              WAIT FOR RULE #3 🚨

            </span>

          </div>

        </AbsoluteFill>

      )}      {/* ── FADE OUT ────────────────────────────────────────────── */}

      {phase === 6 && (

        <AbsoluteFill style={{

          zIndex: 1000, backgroundColor: "black",

          opacity: interpolate(frame, [total_duration * fps - 15, total_duration * fps], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})

        }}/>

      )}

    </AbsoluteFill>

  );

};

export const ThumbnailCover: React.FC<{
  script: any;
}> = ({ script }) => {
  if (!script) return null;

  const seed = script.style_seed || 1;
  const pal = PALETTES[seed % PALETTES.length];
  
  const hook = script.hook || "Wealth Mindset";
  const redKw = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9]/g,"") : "WARNING";
  const activeRedWords = [...RED_WORDS, redKw];
  
  const words = hook.split(/\s+/);

  return (
    <AbsoluteFill style={{ background: pal.bg1, justifyContent: 'center', alignItems: 'center', padding: 80 }}>
      {/* Background Graphic/Glow */}
      <div style={{ position: 'absolute', width: 800, height: 800, borderRadius: '50%', background: pal.p, filter: 'blur(300px)', opacity: 0.15 }} />
      
      {/* Small Corner Badge Profile Photo */}
      <div style={{ position: 'absolute', top: 50, left: 50, display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{ width: 100, height: 100, borderRadius: '50%', overflow: 'hidden', border: `4px solid ${pal.p}`, boxShadow: `0 0 30px rgba(0,0,0,0.5)` }}>
           <Img src={staticFile("wealth_profile_photo.png")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
        <div style={{ fontFamily: TITLE_FONT, color: '#fff', fontSize: 28, fontWeight: 'bold', opacity: 0.8 }}>@WealthMatrixAI</div>
      </div>

      {/* Dominant Visual Text */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'center', gap: '30px 20px', width: '100%', zIndex: 10 }}>
        {words.map((w: string, i: number) => {
          const cleanW = w.toUpperCase().replace(/[^A-Z0-9]/g,"");
          const isHighlight = activeRedWords.some(r => cleanW.includes(r)) || w.length > 8;
          return (
            <span key={i} style={{
              fontFamily: TITLE_FONT,
              fontSize: 110,
              fontWeight: 900,
              lineHeight: 1.1,
              textAlign: 'center',
              textTransform: 'uppercase',
              color: isHighlight ? pal.bg1 : '#FFFFFF',
              backgroundColor: isHighlight ? pal.p : 'transparent',
              padding: isHighlight ? '10px 40px' : '0',
              borderRadius: isHighlight ? 20 : 0,
              boxShadow: isHighlight ? `0 20px 60px ${pal.p}88` : 'none',
              transform: isHighlight ? 'scale(1.05) rotate(-2deg)' : 'none'
            }}>
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
