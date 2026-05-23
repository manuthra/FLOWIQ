import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from analyzer import calculate_funnel, calculate_cohort, get_ai_insights

st.set_page_config(
    page_title="FlowIQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@300;400;500&display=swap');

:root {
    --bg:       #060914;
    --surface:  #0c1120;
    --surface2: #111827;
    --border:   #1e2d45;
    --neon:     #00f5c4;
    --neon-dim: rgba(0,245,196,0.12);
    --neon-glow:rgba(0,245,196,0.35);
    --hot:      #ff3d6b;
    --gold:     #ffc94d;
    --white:    #f0f6ff;
    --muted:    #8892a4;
    --text:     #ccd6f6;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif 
    background: var(--bg) 
    color: var(--text) 
}

.stApp {
    background: var(--bg) 
}

.main .block-container {
    padding: 0 
    max-width: 100% 
}

#MainMenu, footer, header { visibility: hidden; }

/* ══ TOPBAR ══ */
.topbar {
    display: flex;
    flex-wrap: wrap;
    overflow-x: hidden;        
    align-items: center;
    justify-content: space-between;
    padding: 0 52px;
    height: 58px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 200;
}

.tb-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    letter-spacing: 5px;
    color: var(--neon);
    text-shadow: 0 0 24px var(--neon-glow);
}

.tb-logo span { color: var(--white); }

.tb-pills { display:flex; gap:6px; }

.tb-pill {
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    padding: 5px 14px;
    border-radius: 999px;
    border: 1px solid var(--border);
    color: var(--muted);
}

.tb-pill.on {
    border-color: var(--neon);
    color: var(--neon);
    background: var(--neon-dim);
}

.tb-live {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: var(--muted);
}

.live-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--neon);
    box-shadow: 0 0 10px var(--neon);
    animation: blink-dot 2s ease infinite;
}

@keyframes blink-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(0.8); }
}

/* ══ HERO ══ */
.hero {
    display: grid;
    grid-template-columns: 60% 40%;
    min-height: 580px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}

/* ── PARTICLE CANVAS ── */
#hero-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

/* ── HERO BG LAYERS ── */
.hero-bg-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,245,196,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,245,196,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
    animation: grid-pulse 8s ease-in-out infinite;
}

@keyframes grid-pulse {
    0%,100% { opacity: 0.6; }
    50%      { opacity: 1; }
}

/* radial vignette so grid fades at edges */
.hero-bg-vignette {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 80% at 30% 50%,
        transparent 0%,
        rgba(6,9,20,0.55) 60%,
        rgba(6,9,20,0.92) 100%);
    pointer-events: none;
    z-index: 1;
}

/* horizontal scan sweep */
.hero-scan {
    position: absolute;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0,245,196,0.6), transparent);
    box-shadow: 0 0 24px 6px rgba(0,245,196,0.18);
    animation: scan-sweep 6s linear infinite;
    z-index: 2;
    pointer-events: none;
}

@keyframes scan-sweep {
    0%   { top: -4px; opacity: 0; }
    5%   { opacity: 1; }
    95%  { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}

/* data stream ticker on the far left edge */
.hero-stream {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg,
        transparent,
        rgba(0,245,196,0.8) 30%,
        rgba(0,245,196,0.4) 70%,
        transparent);
    animation: stream-pulse 3s ease-in-out infinite alternate;
    z-index: 3;
    pointer-events: none;
}

@keyframes stream-pulse {
    from { opacity:0.4; box-shadow: 0 0 8px rgba(0,245,196,0.3); }
    to   { opacity:1;   box-shadow: 0 0 20px rgba(0,245,196,0.7); }
}

/* floating hex decorations */
.hex-deco {
    position: absolute;
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    color: rgba(0,245,196,0.18);
    letter-spacing: 2px;
    pointer-events: none;
    z-index: 2;
    animation: hex-float 12s ease-in-out infinite;
}

.hex-deco:nth-child(1) { top: 12%;  left: 8%;  animation-delay: 0s;   animation-duration: 11s; }
.hex-deco:nth-child(2) { top: 28%;  left: 48%; animation-delay: 2s;   animation-duration: 14s; }
.hex-deco:nth-child(3) { top: 65%;  left: 22%; animation-delay: 4s;   animation-duration: 9s;  }
.hex-deco:nth-child(4) { top: 78%;  left: 55%; animation-delay: 1s;   animation-duration: 13s; }
.hex-deco:nth-child(5) { top: 42%;  left: 76%; animation-delay: 3s;   animation-duration: 10s; }
.hex-deco:nth-child(6) { top: 8%;   left: 65%; animation-delay: 5s;   animation-duration: 15s; }

@keyframes hex-float {
    0%,100% { transform: translateY(0px) rotate(0deg);  opacity: 0.18; }
    33%     { transform: translateY(-14px) rotate(3deg); opacity: 0.35; }
    66%     { transform: translateY(8px) rotate(-2deg);  opacity: 0.12; }
}

/* corner brackets */
.corner-tl, .corner-tr, .corner-bl, .corner-br {
    position: absolute;
    width: 28px; height: 28px;
    z-index: 3;
    pointer-events: none;
}
.corner-tl { top: 20px; left: 20px;
    border-top: 1.5px solid rgba(0,245,196,0.5);
    border-left: 1.5px solid rgba(0,245,196,0.5); }
.corner-tr { top: 20px; right: 20px;
    border-top: 1.5px solid rgba(0,245,196,0.5);
    border-right: 1.5px solid rgba(0,245,196,0.5); }
.corner-bl { bottom: 20px; left: 20px;
    border-bottom: 1.5px solid rgba(0,245,196,0.5);
    border-left: 1.5px solid rgba(0,245,196,0.5); }
.corner-br { bottom: 20px; right: 20px;
    border-bottom: 1.5px solid rgba(0,245,196,0.5);
    border-right: 1.5px solid rgba(0,245,196,0.5); }

.hero-l {
    padding: 80px 64px 72px;
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    z-index: 10;
}

/* moving neon glow behind text */
.hero-l::before {
    content: '';
    position: absolute;
    width: 700px; height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,245,196,0.09) 0%, transparent 65%);
    top: -200px; left: -180px;
    pointer-events: none;
    animation: orb-drift 9s ease-in-out infinite alternate;
}

@keyframes orb-drift {
    from { transform: translate(0,0); }
    to   { transform: translate(60px,40px); }
}

/* second orb, hot color */
.hero-l::after {
    content: '';
    position: absolute;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,61,107,0.05) 0%, transparent 65%);
    bottom: -100px; right: 0;
    pointer-events: none;
    animation: orb-drift2 13s ease-in-out infinite alternate;
}

@keyframes orb-drift2 {
    from { transform: translate(0,0); }
    to   { transform: translate(-40px,-30px); }
}

.h-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--neon);
    margin-bottom: 36px;
    position: relative;
    opacity: 0;
    animation: up 0.6s 0.1s ease forwards;
}

.h-eyebrow::before {
    content: '';
    width: 30px; height: 1.5px;
    background: var(--neon);
    box-shadow: 0 0 8px var(--neon);
}

.h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(32px, 5vw, 56px);
    line-height: 0.92;
    letter-spacing: 2px;
    color: var(--white);
    margin-bottom: 36px;
    position: relative;
    opacity: 0;
    animation: up 0.7s 0.2s ease forwards;
}

.h1-accent {
    color: var(--neon);
    text-shadow: 0 0 50px var(--neon-glow), 0 0 100px rgba(0,245,196,0.1);
    position: relative;
    display: inline-block;
}

.h1-accent::before,
.h1-accent::after {
    content: attr(data-t);
    position: absolute;
    inset: 0;
    opacity: 0;
}

.h1-accent::before {
    color: var(--hot);
    text-shadow: none;
    animation: ga 6s 4s step-end infinite;
}

.h1-accent::after {
    color: var(--gold);
    text-shadow: none;
    animation: gb 6s 4s step-end infinite;
}

@keyframes ga {
    0%,88%,91%,100% { opacity:0; transform:translate(0); }
    89% { opacity:0.8; transform:translate(-4px,1px); clip-path:polygon(0 25%,100% 25%,100% 55%,0 55%); }
}

@keyframes gb {
    0%,88%,92%,100% { opacity:0; transform:translate(0); }
    90% { opacity:0.6; transform:translate(4px,-2px); clip-path:polygon(0 60%,100% 60%,100% 78%,0 78%); }
}

.h-body {
    font-size: 17px;
    font-weight: 400;
    line-height: 1.8;
    color: var(--muted);
    max-width: 460px;
    margin-bottom: 52px;
    position: relative;
    opacity: 0;
    animation: up 0.7s 0.35s ease forwards;
}

.h-body strong { color: var(--text); font-weight: 600; }

.h-cta {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: var(--neon);
    color: var(--bg);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 15px 32px;
    clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
    transition: all 0.2s;
    position: relative;
    opacity: 0;
    animation: up 0.7s 0.5s ease forwards;
    cursor: default;
}

.h-cta:hover {
    box-shadow: 0 0 40px var(--neon-glow);
    letter-spacing: 2px;
}

/* ── HERO RIGHT ── */
.hero-r {
    background: rgba(12,17,32,0.85);
    backdrop-filter: blur(2px);
    padding: 52px 44px;
    display: flex;
    flex-direction: column;
    gap: 0;
    position: relative;
    overflow: hidden;
    z-index: 10;
}

/* grid bg */
.hero-r::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 44px 44px;
    opacity: 0.35;
    pointer-events: none;
}

.hr-block {
    padding-bottom: 28px;
    margin-bottom: 28px;
    border-bottom: 1px solid var(--border);
    position: relative;
    opacity: 0;
    animation: up 0.6s ease forwards;
}

.hr-block:last-child {
    border-bottom: none;
    padding-bottom: 0;
    margin-bottom: 0;
}

.hr-block:nth-child(1) { animation-delay: 0.3s; }
.hr-block:nth-child(2) { animation-delay: 0.42s; }
.hr-block:nth-child(3) { animation-delay: 0.54s; }
.hr-block:nth-child(4) { animation-delay: 0.66s; }

.hr-lbl {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}

.hr-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 56px;
    line-height: 1;
    letter-spacing: 2px;
    color: var(--white);
    position: relative;
}

.hr-val.neon {
    color: var(--neon);
    text-shadow: 0 0 30px var(--neon-glow);
}

.terminal {
    background: rgba(0,0,0,0.5);
    border: 1px solid var(--border);
    border-left: 2px solid var(--neon);
    padding: 18px 20px;
    margin-top: auto;
    position: relative;
    flex-shrink: 0;
}

.tl {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    line-height: 2;
    color: var(--muted);
}

.tl .cmd { color: var(--neon); }
.tl .res { color: var(--gold); }

.cur {
    display: inline-block;
    width: 7px; height: 14px;
    background: var(--neon);
    vertical-align: middle;
    margin-left: 2px;
    animation: cur-blink 1s step-end infinite;
}

@keyframes cur-blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ══ UPLOAD STRIP ══ */
.upload-strip {
    background: var(--surface);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 44px 64px;
}

.us-head {
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--neon);
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 14px;
}

.us-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

div[data-testid="stFileUploader"] {
    background: rgba(0,245,196,0.025) 
    border: 1px dashed rgba(0,245,196,0.22) 
    border-radius: 0 
    color: white;
    padding: 4px 
    transition: all 0.3s;
}

div[data-testid="stFileUploader"]:hover {
    background: rgba(0,245,196,0.055) 
    border-color: rgba(0,245,196,0.55) 
}

div[data-testid="stFileUploader"] section { padding: 22px }

div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] p {
    color: var(--muted) 
    font-family: 'Fira Code', monospace 
    font-size: 12px 
}
div[data-testid="stFileUploader"] label {
    color: white;
}
.stCheckbox p {
    color: white;
}            
div[data-testid="stFileUploader"] button {
    background: transparent 
    color: var(--neon) 
    border: 1px solid var(--neon) 
    border-radius: 0 
    padding: 11px 26px 
    font-family: 'Fira Code', monospace 
    font-size: 11px 
    letter-spacing: 2px 
    text-transform: uppercase 
    transition: all 0.2s 
}

div[data-testid="stFileUploader"] button:hover {
    background: var(--neon) 
    color: var(--bg) 
    box-shadow: 0 0 24px var(--neon-glow) 
}

.stCheckbox label {
    color: white
    font-family: 'Fira Code', monospace 
    font-size: 11px 
    letter-spacing: 2px 
}

/* ══ DASHBOARD ══ */
.dash { padding: 0 64px 72px; }

.s-head {
    padding: 44px 0 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
    display: flex;
    align-items: baseline;
    gap: 14px;
}

.s-num {
    font-family: 'Fira Code', monospace;
    font-size: 10px;
    color: var(--neon);
    letter-spacing: 2px;
}

.s-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    letter-spacing: 4px;
    color: var(--white);
}

/* ── METRIC CARDS ── */
.mc {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 28px 24px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    animation: up 0.5s ease both;
}

.mc:hover {
    border-color: var(--neon);
    transform: translateY(-3px);
    box-shadow: 0 0 0 1px var(--neon), 0 12px 40px rgba(0,245,196,0.08);
}

.mc::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    border-style: solid;
    border-width: 0 20px 20px 0;
    border-color: transparent var(--border) transparent transparent;
    transition: border-color 0.25s;
}

.mc:hover::after { border-color: transparent var(--neon) transparent transparent; }

.mc-lbl {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 14px;
}

.mc-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 56px;
    line-height: 1;
    letter-spacing: 1px;
    color: var(--white);
}

.mc-val.neon { color:var(--neon); text-shadow:0 0 22px var(--neon-glow); }
.mc-val.hot  { color:var(--hot);  text-shadow:0 0 22px rgba(255,61,107,0.45); }
.mc-val.gold { color:var(--gold); text-shadow:0 0 22px rgba(255,201,77,0.35); }

.mc-bar {
    position: absolute;
    bottom:0; left:0; right:0;
    height: 2px;
    background: var(--neon);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.4s ease;
}

.mc:hover .mc-bar { transform: scaleX(1); }

/* ── CHART CARDS ── */
.cc {
    background: var(--surface);
    border: 1px solid var(--border);
    animation: up 0.6s 0.1s ease both;
}

.cc-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 18px;
    border-bottom: 1px solid var(--border);
    background: rgba(0,0,0,0.2);
}

.cc-title {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text);
}

.cc-badge {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    padding: 3px 9px;
    border: 1px solid var(--neon);
    color: var(--neon);
    letter-spacing: 1px;
}

/* ── INSIGHT MAIN ── */
.ins-main {
    background: linear-gradient(135deg, var(--surface2), rgba(0,245,196,0.04));
    border: 1px solid var(--border);
    border-left: 3px solid var(--neon);
    padding: 34px 40px;
    margin-bottom: 2px;
    position: relative;
    overflow: hidden;
    animation: up 0.6s ease both;
}

.ins-main::after {
    content: '!';
    position: absolute;
    right: 28px; top: 10px;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 110px;
    color: rgba(0,245,196,0.04);
    line-height: 1;
    pointer-events: none;
}

.ins-tag {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--neon);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.ins-tag::before {
    content: '';
    width: 18px; height: 1.5px;
    background: var(--neon);
    display: inline-block;
}

.ins-body {
    font-size: 19px;
    font-weight: 500;
    color: var(--white);
    line-height: 1.6;
    max-width: 700px;
}

/* ── FIX ROWS ── */
.fix-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: none;
    padding: 20px 28px;
    display: grid;
    grid-template-columns: 130px 1fr auto;
    align-items: center;
    gap: 20px;
    transition: background 0.2s, border-color 0.2s;
    animation: up 0.5s ease both;
}

.fix-row:hover {
    background: var(--surface2);
    border-color: rgba(0,245,196,0.18);
}

.fix-step {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    color: var(--neon);
    border-right: 1px solid var(--border);
    padding-right: 20px;
}

.fix-issue {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    color: var(--muted);
    margin-bottom: 5px;
}

.fix-action {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
}

.fix-action::before { content: '→ '; color: var(--neon); }

.fix-tags { display:flex; flex-direction:column; gap:5px; align-items:flex-end; }

.ftag {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 9px;
    border: 1px solid currentColor;
    white-space: nowrap;
}

.ftag.high   { color: var(--hot); }
.ftag.medium { color: var(--gold); }
.ftag.low    { color: var(--neon); }

/* ── QUICK WIN ── */
.qw {
    background: rgba(0,245,196,0.06);
    border: 1px solid rgba(0,245,196,0.22);
    border-top: none;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 18px;
    animation: up 0.5s ease both;
}

.qw-lbl {
    font-family: 'Fira Code', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--neon);
    white-space: nowrap;
    padding-right: 18px;
    border-right: 1px solid rgba(0,245,196,0.22);
}

.qw-text {
    font-size: 14px;
    font-weight: 500;
    color: var(--neon);
}

/* ── EMPTY STATE ── */
.empty {
    min-height: 52vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 22px;
}

.empty-ring {
    width: 96px; height: 96px;
    border-radius: 50%;
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    position: relative;
    animation: spin 10s linear infinite;
}

@keyframes spin { to { transform:rotate(360deg); } }

.empty-ring::before {
    content: '';
    position: absolute;
    inset: 7px;
    border-radius: 50%;
    border: 1.5px solid var(--neon);
    border-top-color: transparent;
    animation: spin 3s linear infinite reverse;
}

.empty-inner {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 18px;
    letter-spacing: 3px;
    color: var(--neon);
    animation: spin 10s linear infinite reverse;
}

.empty-h {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 40px;
    letter-spacing: 5px;
    color: var(--border);
}

.empty-p {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
}

/* ══ ANIMATIONS ══ */
@keyframes up {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
}

.mc:nth-child(1){animation-delay:.05s}
.mc:nth-child(2){animation-delay:.12s}
.mc:nth-child(3){animation-delay:.19s}
.mc:nth-child(4){animation-delay:.26s}
.fix-row:nth-child(2){animation-delay:.07s}
.fix-row:nth-child(3){animation-delay:.14s}
.fix-row:nth-child(4){animation-delay:.21s}

.stSpinner > div { border-top-color: var(--neon) }
</style>
""", unsafe_allow_html=True)

# ── TOPBAR ──
st.markdown("""
<div class="topbar">
  <div class="tb-logo">FLOW<span>IQ</span></div>
  <div class="tb-pills">
    <span class="tb-pill on">Dashboard</span>
    <span class="tb-pill">Cohorts</span>
    <span class="tb-pill">Reports</span>
  </div>
  <div class="tb-live">
    <div class="live-dot"></div>
    AI ENGINE ONLINE
  </div>
</div>
""", unsafe_allow_html=True)

# ── HERO (uses components.html so JS canvas actually runs) ──
components.html("""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Fira+Code:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{margin:0;padding:0;background:#060914;overflow:hidden;}

.hero {
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 420px;             
  border-bottom: 1px solid #1e2d45;
  position: relative;
  overflow: hidden;
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.hero-r { display: none; }
.hero-l { padding: 40px 24px; border-right: none; }                

#hero-canvas {
  position: absolute;
  inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
}

.hero-bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0,245,196,0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,245,196,0.045) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none; z-index: 0;
  animation: grid-pulse 8s ease-in-out infinite;
}
@keyframes grid-pulse { 0%,100%{opacity:.6} 50%{opacity:1} }

.hero-bg-vignette {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 80% at 30% 50%,
    transparent 0%, rgba(6,9,20,.55) 60%, rgba(6,9,20,.92) 100%);
  pointer-events: none; z-index: 1;
}

.hero-scan {
  position: absolute; left:0; right:0; height:2px;
  background: linear-gradient(90deg,transparent,rgba(0,245,196,.65),transparent);
  box-shadow: 0 0 28px 8px rgba(0,245,196,.18);
  animation: scan-sweep 6s linear infinite;
  z-index: 2; pointer-events: none;
}
@keyframes scan-sweep {
  0%{top:-4px;opacity:0} 5%{opacity:1} 95%{opacity:1} 100%{top:100%;opacity:0}
}

.hero-stream {
  position: absolute; left:0; top:0; bottom:0; width:2px;
  background: linear-gradient(180deg,transparent,rgba(0,245,196,.8) 30%,rgba(0,245,196,.4) 70%,transparent);
  animation: stream-pulse 3s ease-in-out infinite alternate;
  z-index: 3; pointer-events: none;
}
@keyframes stream-pulse {
  from{opacity:.4;box-shadow:0 0 8px rgba(0,245,196,.3)}
  to{opacity:1;box-shadow:0 0 20px rgba(0,245,196,.7)}
}

.hex-deco {
  position: absolute;
  font-family: 'Fira Code', monospace; font-size:10px;
  color: rgba(0,245,196,.2); letter-spacing:2px;
  pointer-events:none; z-index:2;
  animation: hex-float 12s ease-in-out infinite;
}
.hex-deco:nth-child(1){top:12%;left:8%;animation-delay:0s;animation-duration:11s}
.hex-deco:nth-child(2){top:28%;left:48%;animation-delay:2s;animation-duration:14s}
.hex-deco:nth-child(3){top:65%;left:22%;animation-delay:4s;animation-duration:9s}
.hex-deco:nth-child(4){top:78%;left:55%;animation-delay:1s;animation-duration:13s}
.hex-deco:nth-child(5){top:42%;left:76%;animation-delay:3s;animation-duration:10s}
.hex-deco:nth-child(6){top:8%;left:65%;animation-delay:5s;animation-duration:15s}
@keyframes hex-float {
  0%,100%{transform:translateY(0) rotate(0deg);opacity:.2}
  33%{transform:translateY(-14px) rotate(3deg);opacity:.38}
  66%{transform:translateY(8px) rotate(-2deg);opacity:.12}
}

.corner-tl,.corner-tr,.corner-bl,.corner-br{
  position:absolute;width:28px;height:28px;z-index:3;pointer-events:none;
}
.corner-tl{top:20px;left:20px;border-top:1.5px solid rgba(0,245,196,.55);border-left:1.5px solid rgba(0,245,196,.55)}
.corner-tr{top:20px;right:20px;border-top:1.5px solid rgba(0,245,196,.55);border-right:1.5px solid rgba(0,245,196,.55)}
.corner-bl{bottom:20px;left:20px;border-bottom:1.5px solid rgba(0,245,196,.55);border-left:1.5px solid rgba(0,245,196,.55)}
.corner-br{bottom:20px;right:20px;border-bottom:1.5px solid rgba(0,245,196,.55);border-right:1.5px solid rgba(0,245,196,.55)}

/* HERO LEFT */
.hero-l {
  padding: 80px 64px 72px;
  border-right: 1px solid #1e2d45;
  display: flex; flex-direction: column; justify-content: center;
  position: relative; overflow: hidden; z-index: 10;
}
.hero-l::before {
  content:''; position:absolute;
  width:700px;height:700px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,245,196,.09) 0%,transparent 65%);
  top:-200px;left:-180px;pointer-events:none;
  animation:orb-drift 9s ease-in-out infinite alternate;
}
@keyframes orb-drift{from{transform:translate(0,0)}to{transform:translate(60px,40px)}}
.hero-l::after {
  content:'';position:absolute;
  width:400px;height:400px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,61,107,.06) 0%,transparent 65%);
  bottom:-100px;right:0;pointer-events:none;
  animation:orb-drift2 13s ease-in-out infinite alternate;
}
@keyframes orb-drift2{from{transform:translate(0,0)}to{transform:translate(-40px,-30px)}}

.h-eyebrow {
  display:inline-flex;align-items:center;gap:12px;
  font-family:'Fira Code',monospace;font-size:11px;
  letter-spacing:3px;text-transform:uppercase;color:#00f5c4;
  margin-bottom:36px;opacity:0;animation:up .6s .1s ease forwards;
}
.h-eyebrow::before{content:'';width:30px;height:1.5px;background:#00f5c4;box-shadow:0 0 8px #00f5c4}

.h1 {
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(28px, 4vw, 48px);line-height:.92;
  letter-spacing:2px;color:#f0f6ff;margin-bottom:36px;
  opacity:0;animation:up .7s .2s ease forwards;
}
.h1-accent {
  color:#00f5c4;
  text-shadow:0 0 50px rgba(0,245,196,.35),0 0 100px rgba(0,245,196,.1);
  display:inline-block;position:relative;
}
.h1-accent::before,.h1-accent::after{content:attr(data-t);position:absolute;inset:0;opacity:0}
.h1-accent::before{color:#ff3d6b;text-shadow:none;animation:ga 6s 4s step-end infinite}
.h1-accent::after{color:#ffc94d;text-shadow:none;animation:gb 6s 4s step-end infinite}
@keyframes ga{0%,88%,91%,100%{opacity:0;transform:translate(0)}89%{opacity:.8;transform:translate(-4px,1px);clip-path:polygon(0 25%,100% 25%,100% 55%,0 55%)}}
@keyframes gb{0%,88%,92%,100%{opacity:0;transform:translate(0)}90%{opacity:.6;transform:translate(4px,-2px);clip-path:polygon(0 60%,100% 60%,100% 78%,0 78%)}}

.h-body {
  font-size:17px;font-weight:400;line-height:1.8;color:#8892a4;
  max-width:460px;margin-bottom:52px;
  opacity:0;animation:up .7s .35s ease forwards;
}
.h-body strong{color:#ccd6f6;font-weight:600}

.h-cta {
  display:inline-flex;align-items:center;gap:12px;
  background:#00f5c4;color:#060914;
  font-family:'Plus Jakarta Sans',sans-serif;
  font-size:13px;font-weight:700;letter-spacing:1px;padding:15px 32px;
  clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px));
  transition:all .2s;cursor:default;
  opacity:0;animation:up .7s .5s ease forwards;
}
.h-cta:hover{box-shadow:0 0 40px rgba(0,245,196,.35);letter-spacing:2px}

/* HERO RIGHT */
.hero-r {
  background:rgba(12,17,32,.88);
  backdrop-filter:blur(2px);
  padding:52px 44px;
  display:flex;flex-direction:column;gap:0;
  position:relative;overflow:hidden;z-index:10;
}
.hero-r::before {
  content:'';position:absolute;inset:0;
  background-image:linear-gradient(#1e2d45 1px,transparent 1px),linear-gradient(90deg,#1e2d45 1px,transparent 1px);
  background-size:44px 44px;opacity:.35;pointer-events:none;
}
.hr-block {
  padding-bottom:28px;margin-bottom:28px;
  border-bottom:1px solid #1e2d45;
  position:relative;opacity:0;animation:up .6s ease forwards;
}
.hr-block:last-child{border-bottom:none;padding-bottom:0;margin-bottom:0}
.hr-block:nth-child(1){animation-delay:.3s}
.hr-block:nth-child(2){animation-delay:.42s}
.hr-block:nth-child(3){animation-delay:.54s}
.hr-block:nth-child(4){animation-delay:.66s}

.hr-lbl{font-family:'Fira Code',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#8892a4;margin-bottom:8px}
.hr-val{font-family:'Bebas Neue',sans-serif;font-size:56px;line-height:1;letter-spacing:2px;color:#f0f6ff}
.hr-val.neon{color:#00f5c4;text-shadow:0 0 30px rgba(0,245,196,.35)}

.terminal{
  background:rgba(0,0,0,.5);
  border:1px solid #1e2d45;border-left:2px solid #00f5c4;
  padding:18px 20px;margin-top:auto;
}
.tl{font-family:'Fira Code',monospace;font-size:11px;line-height:2;color:#8892a4}
.tl .cmd{color:#00f5c4} .tl .res{color:#ffc94d}
.cur{display:inline-block;width:7px;height:14px;background:#00f5c4;vertical-align:middle;margin-left:2px;animation:cur-blink 1s step-end infinite}
@keyframes cur-blink{0%,100%{opacity:1}50%{opacity:0}}

@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<div class="hero">
  <canvas id="hero-canvas"></canvas>
  <div class="hero-bg-grid"></div>
  <div class="hero-bg-vignette"></div>
  <div class="hero-scan"></div>
  <div class="hero-stream"></div>
  <div class="corner-tl"></div>
  <div class="corner-tr"></div>
  <div class="corner-bl"></div>
  <div class="corner-br"></div>
  <div class="hex-deco">0x4F2A</div>
  <div class="hex-deco">DROP_RATE</div>
  <div class="hex-deco">0xC8FF</div>
  <div class="hex-deco">FUNNEL</div>
  <div class="hex-deco">0x1E9B</div>
  <div class="hex-deco">AI_SCAN</div>

  <div class="hero-l">
    <div class="h-eyebrow">⚡ Behavioral Flow Analyzer</div>
    <div class="h1">
      Every drop-off<br>costs you.<br>
      <span class="h1-accent" data-t="Fix it now.">Fix it now.</span>
    </div>
    <div class="h-body">
      Upload session data and let AI pinpoint exactly <strong>where users drop off</strong>
      — with specific, prioritised fixes you can ship today.
    </div>
    <div class="h-cta">↓ &nbsp;Upload CSV below</div>
  </div>

  <div class="hero-r">
    <div class="hr-block">
      <div class="hr-lbl">avg time to insight</div>
      <div class="hr-val neon">&lt; 3s</div>
    </div>
    <div class="hr-block">
      <div class="hr-lbl">AI model</div>
      <div class="hr-val" style="font-size:30px;letter-spacing:3px;color:#8892a4;">INSIGHT ENGINE</div>
    </div>
    <div class="hr-block">
      <div class="hr-lbl">analysis depth</div>
      <div class="hr-val">DEEP</div>
    </div>
    <div class="hr-block">
      <div class="terminal">
        <div class="tl"><span class="cmd">$ flowiq</span> --run funnel.csv</div>
        <div class="tl"><span class="res">→ scanning drop-off patterns</span></div>
        <div class="tl"><span class="res">→ running AI inference</span></div>
        <div class="tl">ready<span class="cur"></span></div>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const canvas = document.getElementById('hero-canvas');
  const hero   = canvas.parentElement;

  const resize = () => { canvas.width = hero.offsetWidth; canvas.height = hero.offsetHeight; };
  resize();
  new ResizeObserver(resize).observe(hero);

  const ctx    = canvas.getContext('2d');
  const NEON   = '#00f5c4';
  const HOT    = '#ff3d6b';
  const GOLD   = '#ffc94d';
  const COLORS = [NEON,NEON,NEON,HOT,GOLD];

  const particles = Array.from({length:100},()=>({
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    r:Math.random()*1.8+.3,
    vx:(Math.random()-.5)*.38, vy:(Math.random()-.5)*.38,
    color:COLORS[Math.floor(Math.random()*COLORS.length)],
    alpha:Math.random()*.55+.15, pulse:Math.random()*Math.PI*2
  }));

  const nodes = Array.from({length:8},()=>({
    x:Math.random()*canvas.width, y:Math.random()*canvas.height,
    r:Math.random()*5+4,
    vx:(Math.random()-.5)*.18, vy:(Math.random()-.5)*.18,
    alpha:Math.random()*.4+.2, pulse:Math.random()*Math.PI*2
  }));

  const COL_W = 22;
  const makeRain = () => Array.from({length:Math.ceil(canvas.width/COL_W)},()=>({
    y:-Math.random()*canvas.height,
    speed:Math.random()*.55+.2,
    chars:Array.from({length:20},()=>Math.random()<.5?'1':'0'),
    alpha:Math.random()*.065+.02
  }));
  let rain = makeRain();

  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);

    /* binary rain */
    ctx.font='11px "Fira Code",monospace';
    rain.forEach((col,i)=>{
      col.y+=col.speed;
      if(col.y>canvas.height+320){ col.y=-Math.random()*200; col.chars=col.chars.map(()=>Math.random()<.5?'1':'0'); }
      col.chars.forEach((ch,j)=>{
        const fy=col.y+j*16;
        if(fy<0||fy>canvas.height) return;
        ctx.globalAlpha=col.alpha*(1-j/col.chars.length);
        ctx.fillStyle=NEON; ctx.fillText(ch,i*COL_W+4,fy);
      });
    });

    /* particles */
    particles.forEach(p=>{
      p.x+=p.vx; p.y+=p.vy; p.pulse+=.02;
      if(p.x<0)p.x=canvas.width; if(p.x>canvas.width)p.x=0;
      if(p.y<0)p.y=canvas.height; if(p.y>canvas.height)p.y=0;
      ctx.globalAlpha=p.alpha*(.7+.3*Math.sin(p.pulse));
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=p.color; ctx.fill();
    });

    /* particle connections */
    ctx.lineWidth=.6; ctx.strokeStyle=NEON; ctx.setLineDash([]);
    for(let i=0;i<particles.length;i++){
      for(let j=i+1;j<particles.length;j++){
        const dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
        const d2=dx*dx+dy*dy;
        if(d2<145*145){
          const d=Math.sqrt(d2);
          ctx.globalAlpha=(1-d/145)*.14;
          ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y); ctx.stroke();
        }
      }
    }

    /* data nodes */
    nodes.forEach(nd=>{
      nd.x+=nd.vx; nd.y+=nd.vy; nd.pulse+=.018;
      if(nd.x<0)nd.x=canvas.width; if(nd.x>canvas.width)nd.x=0;
      if(nd.y<0)nd.y=canvas.height; if(nd.y>canvas.height)nd.y=0;
      const pr=nd.r*(1+.22*Math.sin(nd.pulse));
      const g=ctx.createRadialGradient(nd.x,nd.y,0,nd.x,nd.y,pr*5);
      g.addColorStop(0,'rgba(0,245,196,.24)'); g.addColorStop(1,'rgba(0,245,196,0)');
      ctx.globalAlpha=nd.alpha;
      ctx.beginPath(); ctx.arc(nd.x,nd.y,pr*5,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
      ctx.globalAlpha=nd.alpha+.32;
      ctx.beginPath(); ctx.arc(nd.x,nd.y,pr,0,Math.PI*2);
      ctx.fillStyle=NEON; ctx.fill();
    });

    /* node connections */
    ctx.setLineDash([4,7]); ctx.lineWidth=1;
    for(let i=0;i<nodes.length;i++){
      for(let j=i+1;j<nodes.length;j++){
        const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y;
        const d=Math.sqrt(dx*dx+dy*dy);
        if(d<290){
          ctx.globalAlpha=(1-d/290)*.3; ctx.strokeStyle=NEON;
          ctx.beginPath(); ctx.moveTo(nodes[i].x,nodes[i].y);
          ctx.lineTo(nodes[j].x,nodes[j].y); ctx.stroke();
        }
      }
    }
    ctx.setLineDash([]); ctx.globalAlpha=1;
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>
</body>
</html>
""", height=582, scrolling=False)

# ── UPLOAD ──
st.markdown('<div class="upload-strip">', unsafe_allow_html=True)
st.markdown('<div class="us-head">— Data Input</div>', unsafe_allow_html=True)

c1 = st.container()
c2 = st.container()
c3 = st.container()

with c2:
    uploaded_file = st.file_uploader("Drop CSV here", type=["csv"])
    sample = st.checkbox("↳ use sample dataset instead", value=False if uploaded_file else True)

st.markdown('</div>', unsafe_allow_html=True)

# ── DATA ──
df = None
is_valid_data = False

if uploaded_file and not sample:
    try:
        df = pd.read_csv(uploaded_file)
        if not {'user_id','step','completed'}.issubset(df.columns):
            st.error("Missing required columns: user_id, step, completed")
        else:
            is_valid_data = True
    except Exception as e:
        st.error(f"Parse error: {e}")
elif sample:
    df = pd.DataFrame({
        'user_id':   ['U001']*3+['U002']*3+['U003']*3,
        'step':      ['Landing','Signup','OTP']*3,
        'timestamp': ['2024-01-01']*9,
        'completed': [True,True,False,True,True,True,True,False,False]
    })
    is_valid_data = True

# ── DASHBOARD ──
if is_valid_data and df is not None:
    with st.spinner("Analyzing funnel…"):
        funnel   = calculate_funnel(df)
        cohort   = calculate_cohort(df)
        insights = get_ai_insights(funnel)

    total_users = df['user_id'].nunique()
    if funnel:
        completed_users = funnel[-1]['users']
        avg_drop        = sum(x['drop_rate'] for x in funnel) / len(funnel)
        worst           = max(funnel, key=lambda x: x['drop_rate'])
        worst_name      = worst['step']
    else:
        completed_users = 0; avg_drop = 0; worst_name = "N/A"

    st.markdown('<div class="dash">', unsafe_allow_html=True)

    st.markdown('<div class="s-head"><span class="s-num">01</span><span class="s-name">Overview Metrics</span></div>', unsafe_allow_html=True)

    m1 = st.container(); m2 = st.container(); m3 = st.container(); m4 = st.container()
    with m1:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Total Users</div><div class="mc-val neon">{total_users}</div><div class="mc-bar"></div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Completed</div><div class="mc-val">{completed_users}</div><div class="mc-bar"></div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Avg Drop Rate</div><div class="mc-val hot">{round(avg_drop)}%</div><div class="mc-bar"></div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Worst Step</div><div class="mc-val gold" style="font-size:clamp(22px,2.8vw,42px);letter-spacing:0;padding-top:4px;">{worst_name}</div><div class="mc-bar"></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="s-head"><span class="s-num">02</span><span class="s-name">Funnel Breakdown</span></div>', unsafe_allow_html=True)

    BG="#060914"; GRID="#1e2d45"; NEON="#00f5c4"; HOT="#ff3d6b"; MUT="#8892a4"; WHT="#f0f6ff"

    cl = st.container(); cr = st.container()
    with cl:
        st.markdown('<div class="cc"><div class="cc-head"><span class="cc-title">Conversion Funnel</span><span class="cc-badge">USERS / STEP</span></div>', unsafe_allow_html=True)
        ff = go.Figure(go.Funnel(
            y=[x['step'] for x in funnel], x=[x['users'] for x in funnel],
            textinfo="value+percent initial",
            textfont=dict(family="Fira Code, monospace", color=WHT, size=12),
            marker=dict(color=[NEON,"#00c49b","#009e7c","#007a5f","#00573f"][:len(funnel)], line=dict(color=BG,width=2)),
            connector=dict(line=dict(color=GRID,dash="dot",width=1))
        ))
        ff.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10), height=360, font=dict(family="Fira Code",color=MUT))
        st.plotly_chart(ff, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="cc"><div class="cc-head"><span class="cc-title">Drop Rate by Step</span><span class="cc-badge">% LOST</span></div>', unsafe_allow_html=True)
        drops=[x['drop_rate'] for x in funnel]; steps=[x['step'] for x in funnel]
        bf = go.Figure(go.Bar(
            x=steps, y=drops,
            marker=dict(color=drops, colorscale=[[0,NEON],[0.5,"#ffc94d"],[1,HOT]], line=dict(color=BG,width=1.5)),
            text=[f"{v:.1f}%" for v in drops], textposition="outside",
            textfont=dict(family="Fira Code",color=WHT,size=11)
        ))
        bf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10), height=360,
            xaxis=dict(gridcolor=GRID,tickfont=dict(family="Fira Code",color=MUT,size=11),linecolor=GRID),
            yaxis=dict(gridcolor=GRID,tickfont=dict(family="Fira Code",color=MUT,size=11),ticksuffix="%",linecolor=GRID))
        st.plotly_chart(bf, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="s-head"><span class="s-num">03</span><span class="s-name">AI Recommendations</span></div>', unsafe_allow_html=True)

    if insights:
        st.markdown(f'<div class="ins-main"><div class="ins-tag">Biggest Problem Detected</div><div class="ins-body">{insights.get("biggest_problem","N/A")}</div></div>', unsafe_allow_html=True)
        for fix in insights.get('fixes',[]):
            impact=str(fix.get('impact','low')).lower().split()[0]
            effort=str(fix.get('effort','low')).lower().split()[0]
            st.markdown(f"""
<div class="fix-row" style="display:flex; flex-direction:column; gap:10px;">
  <div class="fix-step" style="border-right:none; border-bottom:1px solid #1e2d45; padding-bottom:8px;">{fix.get('step','Step')}</div>
  <div><div class="fix-issue">{fix.get('issue','')}</div><div class="fix-action">{fix.get('fix','')}</div></div>
  <div class="fix-tags" style="flex-direction:row; flex-wrap:wrap; align-items:flex-start;">
    <span class="ftag {impact}">Impact: {fix.get('impact','Low')}</span>
    <span class="ftag {effort}">Effort: {fix.get('effort','Low')}</span>
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="qw"><span class="qw-lbl">⬤ Quick Win</span><span class="qw-text">{insights.get("quick_win","N/A")}</span></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
<div class="empty">
  <div class="empty-ring"><div class="empty-inner">IQ</div></div>
  <div class="empty-h">AWAITING DATA</div>
  <div class="empty-p">Upload a CSV or enable sample dataset above</div>
</div>""", unsafe_allow_html=True)