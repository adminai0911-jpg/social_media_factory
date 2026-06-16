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

const { fontFamily: montserratFont } = loadMontserrat("normal", {
  weights: ["900"],
});

const { fontFamily: bebasFont } = loadBebasNeue("normal", {
  weights: ["400"],
});

// ─── FONT LOADER ────────────────────────────────────────────────────────────
const GlobalStyle = () => (
  <style>{`
    * { box-sizing: border-box; }
  `}</style>
);

// ─── DESIGN SYSTEM ──────────────────────────────────────────────────────────
const HINDI_FONT  = `${devanagariFont}, 'Mangal', 'Sanskrit Text', Arial, sans-serif`;
const TITLE_FONT  = `${bebasFont}, ${montserratFont}, Impact, sans-serif`;

// Premium palette pairs: [primary, accent, glow]
const PALETTES = [
  { p: "#FF0055", a: "#00F5FF", g: "#FF00CC", bg: ["#0A0018", "#200040", "#0D0030"] },
  { p: "#FFD700", a: "#FF6600", g: "#FF00AA", bg: ["#1A0800", "#2D1200", "#0D0500"] },
  { p: "#00FF88", a: "#0066FF", g: "#00FFFF", bg: ["#000D1A", "#001A0D", "#000820"] },
  { p: "#FF3366", a: "#FF9933", g: "#FFCC00", bg: ["#1A0008", "#200010", "#100008"] },
  { p: "#AA00FF", a: "#00CCFF", g: "#FF00AA", bg: ["#080018", "#0A0025", "#050012"] },
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
  "❌  ESCAPE IS IMPOSSIBLE",
];

const RED_WORDS = ["WAKE","SIMULATION","SHADOWS","TRAP","LYING","FAKE","DREAM","FEAR","PANIC","NOW","LIES","BREAK","KYA","SCAM","CHEAT"];

// ─── COMPONENT ──────────────────────────────────────────────────────────────
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
  const alertText  = NEURAL_ALERTS[seed % NEURAL_ALERTS.length];
  const redKw      = script.red_box_keyword ? script.red_box_keyword.toUpperCase().replace(/[^A-Z0-9]/g,"") : "WARNING";
  const subliminal = (script.subliminal_flash_word || "WAKE UP").toUpperCase();
  const serotonin  = Number(script.serotonin_payoff_number || 88319);
  const activeRedWords = [...RED_WORDS, redKw];

  const [,p2,p3,p4,p5] = audio_offsets;
  let phase = 1;
  if (t >= p2 && t < p3) phase = 2;
  else if (t >= p3 && t < p4) phase = 3;
  else if (t >= p4 && t < p5) phase = 4;
  else if (t >= p5) phase = 5;

  const wordIdx = timings.findIndex(w => t >= w.start && t <= w.end + 0.1);
  const word    = timings[wordIdx];
  const isRed   = word ? activeRedWords.some(r => word.word.toUpperCase().replace(/[^A-Z0-9]/g,"").includes(r)) : false;

  // VHS glitch pulse
  const isVHS         = frame % 120 > 112;
  const sublimFrame   = Math.round(p3 * fps) + 90;
  const isSubliminal  = frame === sublimFrame;
  const shatterActive = phase === 4 && frame < Math.round(p4 * fps) + 12;

  // Micro camera shake — only on dramatic events
  const shakeAmt = isRed ? 18 : shatterActive ? 40 : (isVHS ? 6 : 0);
  const sx = shakeAmt > 0 ? (random(frame)     - 0.5) * shakeAmt : 0;
  const sy = shakeAmt > 0 ? (random(frame + 1) - 0.5) * shakeAmt : 0;

  // Animated background orbs

  const o1x = 50 + Math.sin(frame / 45) * 35;
  const o1y = 50 + Math.cos(frame / 38) * 35;
  const o2x = 50 + Math.cos(frame / 30) * 42;
  const o2y = 50 + Math.sin(frame / 52) * 42;
  const o3x = 50 + Math.sin(frame / 60 + 2) * 30;
  const o3y = 50 + Math.cos(frame / 48 + 1) * 38;

  // Alert flash
  const alertFlash = frame % 6 < 3;

  // Tension bar
  const tension = phase < 4
    ? interpolate(frame, [0, p4 * fps], [0, 100], { extrapolateRight: "clamp" })
    : 100;

  // 8D panning indicator for visual sync (audio pans L→R→L)
  const panAngle    = (frame / fps) * 0.2 * Math.PI * 2;
  const panLeft     = 0.5 + 0.5 * Math.cos(panAngle);  // 0→1 oscillation


  // ── Floating screen bob
  const bobY = Math.sin(frame / 22) * 14;

  // ── Serotonin counter
  const counterVal = phase === 2 ? null :
    Math.floor(interpolate(frame, [p3 * fps, p4 * fps], [0, serotonin], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp"
    }));

  return (
    <AbsoluteFill style={{
      backgroundColor: pal.bg[0],
      transform: `translate(${sx}px,${sy}px)`,
      overflow: "hidden"
    }}>
      <GlobalStyle />

      {/* ── AUDIO ─────────────────────────────────────────────────────── */}
      <Sequence from={0}><Audio src={staticFile("v32_audio_0.mp3")} volume={1.6} /></Sequence>
      {p2 && <Sequence from={Math.round(p2*fps)}><Audio src={staticFile("v32_audio_1.mp3")} volume={1.6} /></Sequence>}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("v32_audio_2.mp3")} volume={1.6} /></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("v32_audio_3.mp3")} volume={1.6} /></Sequence>}
      {p5 && <Sequence from={Math.round(p5*fps)}><Audio src={staticFile("v32_audio_4.mp3")} volume={1.6} /></Sequence>}

      {/* 8D Hypnotic Spatial Music */}
      <Sequence from={0}><Audio src={staticFile("hypno.wav")} volume={0.35} loop /></Sequence>

      {/* SFX */}
      {Array.from({length:20}).map((_,i)=>{
        const gf = Math.round(p3*fps)+(i*60);
        if(gf < p4*fps) return <Sequence key={i} from={gf}><Audio src={staticFile("ding.wav")} volume={0.7}/></Sequence>;
        return null;
      })}
      {p3 && <Sequence from={Math.round(p3*fps)}><Audio src={staticFile("riser.wav")} volume={0.5}/></Sequence>}
      {p4 && <Sequence from={Math.round(p4*fps)}><Audio src={staticFile("impact.wav")} volume={2.0}/></Sequence>}

      {/* ── LAYER 1: DEEP DARK PREMIUM BACKGROUND ─────────────────────── */}
      <AbsoluteFill style={{ zIndex: 0 }}>
        {/* Deep mesh gradient base with integrated soft moving orbs (optimized to render 10x faster with 0ms blur overhead) */}
        <div style={{
          position: "absolute", inset: 0,
          background: `
            radial-gradient(circle at ${o1x}% ${o1y}%, ${pal.p}33, transparent 50%),
            radial-gradient(circle at ${o2x}% ${o2y}%, ${pal.a}25, transparent 55%),
            radial-gradient(circle at ${o3x}% ${o3y}%, ${pal.g}20, transparent 45%),
            radial-gradient(ellipse at 50% 50%, ${pal.bg[1]} 0%, ${pal.bg[0]} 60%, ${pal.bg[2]} 100%)
          `
        }}/>
        {/* Fine scanlines for cinematic texture */}
        <div style={{ position:"absolute", inset:0, backgroundImage:"repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.06) 3px,rgba(0,0,0,0.06) 4px)", pointerEvents:"none" }}/>
        {/* Vignette overlay */}
        <div style={{ position:"absolute", inset:0, background:"radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.7) 100%)", pointerEvents:"none" }}/>
      </AbsoluteFill>

      {/* ── LAYER 2: MAIN VISUAL SCREEN ───────────────────────────────── */}
      <AbsoluteFill style={{ zIndex: 10 }}>

        {/* Phase 1 & 2: Premium Floating Glass Screen */}
        <Sequence from={0} durationInFrames={Math.round(p3*fps)}>
          <div style={{
            position:"absolute", top:"18%", left:"4%", width:"92%", height:"60%",
            transform:`translateY(${bobY}px)`,
            borderRadius:40,
            overflow:"hidden",
            // Optimized neon glow (looks just as premium but renders 4x faster)
            boxShadow:`
              0 0 0 2px rgba(255,255,255,0.2),
              0 0 30px ${pal.p}aa,
              0 30px 80px rgba(0,0,0,0.7)
            `,
          }}>
            {/* The actual video */}
            <OffthreadVideo
              src={staticFile(seed%2===0?"gta.mp4":"sand.mp4")}
              style={{ width:"100%", height:"100%", objectFit:"cover",
                filter:`saturate(1.6) contrast(1.15) brightness(1.05)` }}
            />
            {/* Glass gloss — top reflection */}
            <div style={{
              position:"absolute", top:0, left:0, right:0, height:"45%",
              background:"linear-gradient(to bottom, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.06) 60%, transparent 100%)",
              pointerEvents:"none", borderRadius:"40px 40px 0 0"
            }}/>
            {/* Bottom gradient fade into background */}
            <div style={{
              position:"absolute", bottom:0, left:0, right:0, height:"35%",
              background:`linear-gradient(to top, ${pal.bg[0]}CC 0%, transparent 100%)`,
              pointerEvents:"none"
            }}/>
            {/* Neon corner accents */}
            {[["0%","0%","0 0"],["100%","0%","0 0"],["0%","100%","0 0"],["100%","100%","0 0"]].map(([x,y,r],i)=>(
              <div key={i} style={{
                position:"absolute", left:x, top:y, width:40, height:40,
                borderTop:i<2?`3px solid ${pal.p}`:undefined,
                borderBottom:i>=2?`3px solid ${pal.p}`:undefined,
                borderLeft:i%2===0?`3px solid ${pal.p}`:undefined,
                borderRight:i%2===1?`3px solid ${pal.p}`:undefined,
                borderRadius:r, pointerEvents:"none",
                boxShadow:`0 0 20px ${pal.p}`,
                opacity:0.9
              }}/>
            ))}
          </div>
        </Sequence>

        {/* Phase 3: Split Screen */}
        <Sequence from={Math.round(p3*fps)} durationInFrames={Math.round((p4-p3)*fps)}>
          <AbsoluteFill style={{ display:"flex", flexDirection:"column", padding:16, gap:16 }}>
            {[{src:"gta.mp4", flip:true, col:pal.p},{src:"sand.mp4", flip:false, col:pal.a}].map(({src,flip,col},i)=>(
              <div key={i} style={{
                flex:1, overflow:"hidden", borderRadius:32,
                boxShadow:`0 0 0 2px ${col}80, 0 0 50px ${col}60, 0 0 100px ${col}30`,
              }}>
                <OffthreadVideo src={staticFile(src)} style={{
                  width:"100%", height:"100%", objectFit:"cover",
                  transform:flip?"scaleX(-1)":undefined,
                  filter:"saturate(1.7) contrast(1.15) brightness(1.05)"
                }}/>
                <div style={{ position:"absolute", inset:0, background:`linear-gradient(135deg,${col}22,transparent 60%)`, pointerEvents:"none" }}/>
              </div>
            ))}
          </AbsoluteFill>
        </Sequence>

        {/* Phase 4 & 5: Climax */}
        <Sequence from={Math.round(p4*fps)}>
          {shatterActive ? (
            <AbsoluteFill style={{ display:"flex", flexWrap:"wrap" }}>
              {Array.from({length:4}).map((_,i)=>(
                <div key={i} style={{
                  width:"50%", height:"50%", overflow:"hidden",
                  transform:`scale(${1+random(i)*0.25}) rotate(${(random(i)-0.5)*25}deg) translate(${(random(i)-0.5)*120}px,${(random(i)-0.5)*120}px)`,
                  border:`4px solid ${PALETTES[i%PALETTES.length].p}`,
                  filter:`hue-rotate(${i*45}deg) saturate(2)`
                }}>
                  <OffthreadVideo src={staticFile(seed%2===0?"sand.mp4":"gta.mp4")} style={{ width:"200%",height:"200%",objectFit:"cover",transform:`translate(-${(i%2)*50}%,-${Math.floor(i/2)*50}%)` }}/>
                </div>
              ))}
            </AbsoluteFill>
          ) : (
            <AbsoluteFill>
              {/* Scan pulse lines */}
              <div style={{ position:"absolute",inset:0,background:`repeating-linear-gradient(0deg,transparent,transparent 44px,${pal.p}18 44px,${pal.p}18 48px)`,transform:`translateY(${(frame*4)%48}px)`,opacity:0.4 }}/>
              {/* Climax Screen */}
              <div style={{
                position:"absolute", top:"20%", left:"4%", width:"92%", height:"58%",
                transform:`scale(${spring({fps,frame:frame-(Math.round(p4*fps)+12),config:{damping:14}})})`,
                borderRadius:44, overflow:"hidden",
                boxShadow:`0 0 0 3px rgba(255,255,255,0.3),0 0 60px ${pal.a},0 0 120px ${pal.p},0 0 200px ${pal.g}55,0 60px 140px rgba(0,0,0,0.9)`,
              }}>
                <OffthreadVideo src={staticFile(seed%2===0?"sand.mp4":"gta.mp4")} style={{ width:"100%",height:"100%",objectFit:"cover",filter:"saturate(1.8) contrast(1.2) brightness(1.1)" }}/>
                <div style={{ position:"absolute",top:0,left:0,right:0,height:"40%",background:"linear-gradient(to bottom,rgba(255,255,255,0.25),transparent)",pointerEvents:"none" }}/>
              </div>
              {/* PAYOUT — pure gradient text, zero box */}
              <div style={{ position:"absolute",bottom:"6%",width:"92%",left:"4%",textAlign:"center" }}>
                <div style={{
                  fontSize:96, fontFamily:TITLE_FONT, fontWeight:900,
                  background:`linear-gradient(90deg,${pal.p},${pal.a},${pal.g})`,
                  WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
                  filter:`drop-shadow(0 0 30px ${pal.a}) drop-shadow(0 0 60px ${pal.p})`,
                  letterSpacing:4
                }}>
                  PAYOUT: {serotonin.toLocaleString()}
                </div>
              </div>
            </AbsoluteFill>
          )}
        </Sequence>
      </AbsoluteFill>

      {/* ── LAYER 3: TENSION BAR (top edge progress) ──────────────────── */}
      <AbsoluteFill style={{ zIndex:120, pointerEvents:"none" }}>
        <div style={{
          position:"absolute", top:0, left:0, height:6,
          width:`${tension}%`,
          background:`linear-gradient(90deg,${pal.p},${pal.a},${pal.g})`,
          boxShadow:`0 0 20px ${pal.a}, 0 0 40px ${pal.p}`,
          transition:"none"
        }}/>
      </AbsoluteFill>

      {/* ── LAYER 4: DYNAMIC NEURAL ALERT ─────────────────────────────── */}
      {(phase===2||phase===3) && (
        <AbsoluteFill style={{ zIndex:150, pointerEvents:"none" }}>
          <div style={{
            position:"absolute", top:"4%", left:"4%", width:"92%",
            padding:"12px 24px",
            background: alertFlash
              ? `linear-gradient(90deg,${pal.p}EE,${pal.g}EE,${pal.a}EE)`
              : "transparent",
            border:`3px solid ${alertFlash ? "rgba(255,255,255,0.9)" : pal.p}`,
            borderRadius:20,
            textAlign:"center",
            fontFamily:TITLE_FONT, fontSize:48, letterSpacing:6, fontWeight:900,
            color: alertFlash ? "#fff" : pal.p,
            textShadow: alertFlash
              ? `0 0 30px white, 0 0 60px ${pal.p}`
              : `0 0 20px ${pal.p}, 0 0 40px ${pal.g}`,
            boxShadow: alertFlash
              ? `0 0 40px ${pal.p}88, 0 0 80px ${pal.g}44, inset 0 1px 0 rgba(255,255,255,0.3)`
              : "none",
            backdropFilter: alertFlash ? "blur(4px)" : "none",
          }}>
            {alertText}
          </div>
        </AbsoluteFill>
      )}

      {/* ── LAYER 5: SEROTONIN COUNTER ─────────────────────────────────── */}
      <Sequence from={Math.round(p2*fps)} durationInFrames={Math.round((p4-p2)*fps)}>
        <AbsoluteFill style={{ zIndex:160, pointerEvents:"none", justifyContent:"flex-end", alignItems:"center", paddingBottom:60 }}>
          <div style={{
            fontFamily:TITLE_FONT, fontSize:88, fontWeight:900, letterSpacing:3,
            background:`linear-gradient(90deg,${pal.p},${pal.a})`,
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
            filter:`drop-shadow(0 0 24px ${pal.p}) drop-shadow(0 0 48px ${pal.a})`,
          }}>
            {phase===2 ? "SCANNING..." : counterVal?.toLocaleString()}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ── LAYER 6: 8D AUDIO VISUAL PANNING INDICATOR ────────────────── */}
      {/* Subtle circular ring that shows audio moving L↔R */}
      <AbsoluteFill style={{ zIndex:130, pointerEvents:"none" }}>
        <div style={{
          position:"absolute", bottom:"30%", right:"5%",
          width:60, height:60, borderRadius:"50%",
          border:`2px solid ${pal.a}44`,
          background:`radial-gradient(circle at ${Math.round(panLeft*100)}% 50%, ${pal.a}66, transparent 70%)`,
          boxShadow:`0 0 20px ${pal.a}44`,
          opacity: phase === 1 || phase === 5 ? 0 : 0.7,
        }}/>
      </AbsoluteFill>

      {/* ── LAYER 7: 4D EMOJIS ─────────────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex:200, pointerEvents:"none" }}>
        {emojis.map((emoji:string,i:number)=>{
          const sf = Math.round((p3+(i*2.5))*fps);
          if(frame<sf||frame>=sf+fps*2) return null;
          const elapsed = frame-sf;
          return (
            <div key={i} style={{
              position:"absolute",
              left:`${20+(i*30)}%`,
              top:"45%",
              fontSize:180,
              transform:`scale(${spring({fps,frame:elapsed,config:{damping:8}})}) translateY(${interpolate(elapsed,[0,fps*2],[0,-500])}px) rotate(${interpolate(elapsed,[0,fps*2],[0,i%2===0?20:-20])}deg)`,
              opacity:interpolate(elapsed,[0,fps*1.6,fps*2],[1,1,0]),
              filter:`drop-shadow(0 0 30px white) drop-shadow(0 0 60px ${pal.p})`,
            }}>
              {emoji}
            </div>
          );
        })}
      </AbsoluteFill>

      {/* ── LAYER 8: HD CAPTION ENGINE ─────────────────────────────────── */}
      <AbsoluteFill style={{ zIndex:300, justifyContent:"center", alignItems:"center", pointerEvents:"none" }}>
        {word && (()=>{
          const elapsed = t - word.start;
          const ai = wordIdx % 6;
          let tf = "";
          let op = 1;

          if(ai===0) tf=`scale(${spring({fps,frame:frame-Math.round(word.start*fps),config:{damping:12}})})`;
          else if(ai===1) tf=`translate(${Math.sin(frame)*12}px,${Math.cos(frame)*12}px) scale(1.08)`;
          else if(ai===2){ op=frame%4<2?1:0; tf=`scale(1.15)`; }
          else if(ai===3){
            const rx=interpolate(elapsed,[0,0.18],[-90,0],{extrapolateRight:"clamp"});
            tf=`perspective(600px) rotateX(${rx}deg)`;
          } else if(ai===4){
            const s=interpolate(elapsed,[0,0.18],[2.2,1],{extrapolateRight:"clamp"});
            tf=`scale(${s})`;
          } else {
            tf=`scale(${spring({fps,frame:frame-Math.round(word.start*fps),config:{stiffness:280,damping:12}})}) rotate(${wordIdx%2===0?8:-8}deg)`;
          }



          if(isRed){
            // RED keyword — gradient glow, zero background box
            return (
              <div style={{
                fontFamily:TITLE_FONT, fontSize:100, fontWeight:900,
                background:`linear-gradient(135deg,#FF0044,#FF6600,#FFD700)`,
                WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
                filter:`drop-shadow(0 0 15px #FF0044) drop-shadow(0 0 4px black)`,
                transform:tf, opacity:op,
                textAlign:"center", maxWidth:"90%",
                lineHeight:1.1, letterSpacing:4,
                WebkitTextStroke:"1px rgba(255,100,0,0.3)"
              }}>
                {word.word.toUpperCase()}
              </div>
            );
          } else {
            // Normal word — pure text, zero box, max readability
            return (
              <div style={{
                fontFamily:HINDI_FONT, fontSize:84, fontWeight:900,
                color:"#FFFFFF",
                textShadow:`
                  0 0 4px black,
                  0 0 20px ${pal.p}
                `,
                WebkitTextStroke:"2px rgba(0,0,0,0.6)",
                transform:tf, opacity:op,
                textAlign:"center", maxWidth:"90%",
                lineHeight:1.2, letterSpacing:2,
              }}>
                {word.word}
              </div>
            );
          }
        })()}
      </AbsoluteFill>

      {/* ── LAYER 9: COVER FRAME (frame 0 only) ───────────────────────── */}
      {frame===0 && (
        <AbsoluteFill style={{ zIndex:1000 }}>
          <OffthreadVideo src={staticFile("gta.mp4")} style={{ width:"100%",height:"100%",objectFit:"cover",filter:"saturate(1.5) contrast(1.2) brightness(0.85)" }}/>
          <div style={{ position:"absolute",inset:0,background:`linear-gradient(160deg,${pal.p}77,${pal.g}44,${pal.a}66)` }}/>
          <AbsoluteFill style={{ justifyContent:"center",alignItems:"center" }}>
            <div style={{
              fontFamily:TITLE_FONT, fontSize:130, fontWeight:900, letterSpacing:8,
              background:`linear-gradient(135deg,#fff,${pal.p},${pal.a})`,
              WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
              filter:`drop-shadow(0 0 40px ${pal.p}) drop-shadow(0 0 80px ${pal.g})`,
              textAlign:"center", maxWidth:"92%", lineHeight:1,
              padding:"0 24px"
            }}>
              {redKw||"SIMULATION"}
            </div>
          </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* ── LAYER 10: SUBLIMINAL FLASH ────────────────────────────────── */}
      {isSubliminal && (
        <AbsoluteFill style={{ zIndex:999, backgroundColor:"#fff" }}>
          <AbsoluteFill style={{ justifyContent:"center",alignItems:"center" }}>
            <div style={{ fontFamily:TITLE_FONT,fontSize:220,fontWeight:900,color:"#000",letterSpacing:8 }}>
              {subliminal}
            </div>
          </AbsoluteFill>
        </AbsoluteFill>
      )}

      {/* ── LAYER 11: FADE OUT (Phase 5) ──────────────────────────────── */}
      {phase===5 && (
        <AbsoluteFill style={{
          zIndex:1000, backgroundColor:"black",
          opacity:interpolate(frame,[p5*fps,total_duration*fps],[0,1],{extrapolateRight:"clamp"})
        }}/>
      )}

    </AbsoluteFill>
  );
};
