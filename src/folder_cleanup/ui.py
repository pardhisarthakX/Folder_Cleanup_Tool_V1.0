"""
ui.py
Premium Streamlit front-end for the Folder Cleanup Tool.
"Claude x Wattenberger" design fusion: editorial serif elegance + playful data-viz.

This file only calls functions from the other modules - it does not contain
any cleanup logic itself. It provides a guided, visual-first experience:

  1. Start   - folder picker + validation
  2. Scan    - scan preview with rich data visualization
  3. Run     - configure + run (dry-run default, safety gates)
  4. Results - summary dashboard + undo

Run with:  streamlit run src/folder_cleanup/ui.py
"""

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from folder_cleanup import main as pipeline
from folder_cleanup import scanner, undo
from folder_cleanup.config import load_config
from folder_cleanup.logger import setup_logging

load_dotenv()
setup_logging(log_file=None)

st.set_page_config(
    page_title="Folder Cleanup",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CLAUDE x WATTENBERGER DESIGN SYSTEM
# ============================================================
DESIGN_SYSTEM_CSS = """
<style>
/* ============ DESIGN TOKENS ============ */
:root {
    --bg: #0d0d0d;
    --surface: #151515;
    --surface-2: #1c1c1c;
    --surface-3: #242424;
    --border: rgba(255, 255, 255, 0.07);
    --border-strong: rgba(255, 255, 255, 0.14);
    --text: #f7f5f2;
    --text-muted: #a8a29e;
    --serif: Georgia, 'Times New Roman', 'Iowan Old Style', serif;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --coral: #ff6b6b;
    --coral-soft: rgba(255, 107, 107, 0.12);
    --amber: #ffd93d;
    --amber-soft: rgba(255, 217, 61, 0.12);
    --teal: #6bcb77;
    --teal-soft: rgba(107, 203, 119, 0.12);
    --violet: #a78bfa;
    --violet-soft: rgba(167, 139, 250, 0.12);
    --blue: #4d96ff;
    --blue-soft: rgba(77, 150, 255, 0.12);
    --radius: 14px;
    --radius-lg: 20px;
    --radius-pill: 999px;
    --shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
    --shadow-hover: 0 16px 50px rgba(0, 0, 0, 0.55);
    --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
    --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ============ GLOBAL ============ */
html, body, [class*="css"] {
    font-family: var(--sans);
    color: var(--text);
    background: var(--bg);
}
.stApp {
    background:
        radial-gradient(900px 500px at 90% -5%, rgba(255, 107, 107, 0.06), transparent 60%),
        radial-gradient(700px 400px at -5% 5%, rgba(167, 139, 250, 0.05), transparent 55%),
        radial-gradient(500px 300px at 50% 110%, rgba(77, 150, 255, 0.04), transparent 60%),
        var(--bg);
}
#MainMenu, footer, header { visibility: hidden; height: 0; }

/* ============ ANIMATED BACKGROUND BLOBS ============ */
.blob-bg { position: relative; }
.blob-bg::before, .blob-bg::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    z-index: 0;
    pointer-events: none;
    animation: blobFloat 18s ease-in-out infinite alternate;
}
.blob-bg::before {
    width: 420px; height: 420px;
    background: radial-gradient(circle, var(--coral), transparent 70%);
    top: -120px; right: -120px;
}
.blob-bg::after {
    width: 360px; height: 360px;
    background: radial-gradient(circle, var(--violet), transparent 70%);
    bottom: -100px; left: -100px;
    animation-delay: -9s;
}
@keyframes blobFloat {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(40px, 30px) scale(1.1); }
    100% { transform: translate(-20px, -20px) scale(0.95); }
}

/* ============ TYPOGRAPHY ============ */
h1, h2, h3, h4 {
    font-family: var(--serif);
    color: var(--text);
    letter-spacing: -0.02em;
    font-weight: 600;
}

/* ============ PAGE-LOAD CASCADE ANIMATIONS ============ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.94); }
    to   { opacity: 1; transform: scale(1); }
}
.anim-fade-up   { animation: fadeUp 0.6s var(--ease-out) both; }
.anim-fade-up-1 { animation: fadeUp 0.6s var(--ease-out) 0.12s both; }
.anim-fade-up-2 { animation: fadeUp 0.6s var(--ease-out) 0.24s both; }
.anim-fade-up-3 { animation: fadeUp 0.6s var(--ease-out) 0.36s both; }
.anim-fade-up-4 { animation: fadeUp 0.6s var(--ease-out) 0.48s both; }
.anim-fade-in   { animation: fadeIn 0.8s ease both; }
.anim-scale-in  { animation: scaleIn 0.5s var(--spring) both; }

/* ============ HERO ============ */
.hero {
    text-align: center;
    padding: 56px 24px 36px;
    position: relative;
    z-index: 1;
}
.hero .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, var(--coral-soft), var(--violet-soft));
    color: var(--text);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-pill);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 8px 18px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.hero .badge .dot-glow {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--coral);
    box-shadow: 0 0 10px var(--coral);
    animation: pulseDot 2s ease-in-out infinite;
}
@keyframes pulseDot {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%      { transform: scale(1.4); opacity: 0.6; }
}
.hero h1 {
    font-family: var(--serif);
    font-size: 3.4rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 16px;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 40%, #a8a29e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero .sub {
    font-family: var(--sans);
    color: var(--text-muted);
    font-size: 1.12rem;
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Hand-drawn wavy underline */
.wavy-underline {
    position: relative;
    display: inline-block;
}
.wavy-underline svg {
    position: absolute;
    bottom: -6px;
    left: 0;
    width: 100%;
    height: 10px;
    overflow: visible;
}
.wavy-underline svg path {
    stroke: var(--coral);
    stroke-width: 2.5;
    fill: none;
    stroke-linecap: round;
    stroke-dasharray: 60;
    stroke-dashoffset: 60;
    animation: drawUnderline 1.2s 0.5s var(--ease-out) forwards;
}
@keyframes drawUnderline {
    to { stroke-dashoffset: 0; }
}

/* ============ CARDS / SURFACES ============ */
.glass-card {
    background: linear-gradient(160deg, rgba(255,255,255,0.045), rgba(255,255,255,0.012));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: var(--shadow);
    transition: transform 0.35s var(--spring), border-color 0.3s ease, box-shadow 0.35s ease;
    margin-bottom: 18px;
    position: relative;
    z-index: 1;
}
.glass-card:hover {
    transform: translateY(-3px) rotate(-0.3deg);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-hover);
}

/* ============ STATUS PILL ============ */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px;
    border-radius: var(--radius-pill);
    font-size: 0.82rem;
    font-weight: 600;
    border: 1px solid var(--border-strong);
    background: rgba(255,255,255,0.03);
}
.status-pill .dot {
    width: 9px; height: 9px; border-radius: 50%;
    display: inline-block;
    position: relative;
}
.status-pill .dot::after {
    content: '';
    position: absolute;
    inset: -5px;
    border-radius: 50%;
    animation: ripple 2s ease-out infinite;
    border: 2px solid currentColor;
}
.status-pill.dry { color: var(--text); border-color: rgba(107, 203, 119, 0.3); }
.status-pill.dry .dot { background: var(--teal); box-shadow: 0 0 12px var(--teal); color: var(--teal); }
.status-pill.real { color: var(--text); border-color: rgba(255, 107, 107, 0.35); }
.status-pill.real .dot { background: var(--coral); box-shadow: 0 0 12px var(--coral); color: var(--coral); }
@keyframes ripple {
    0%   { transform: scale(0.6); opacity: 0.6; }
    100% { transform: scale(2.2); opacity: 0; }
}

/* ============ STEP TRACKER ============ */
.step-tracker {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 28px 0 12px;
    padding: 18px 24px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    flex-wrap: wrap;
    z-index: 1;
    position: relative;
}
.step-item {
    display: flex; align-items: center; gap: 10px;
    color: var(--text-muted);
    font-size: 0.86rem;
    font-weight: 500;
    transition: color 0.3s ease;
}
.step-item .num {
    width: 26px; height: 26px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 700;
    border: 1px solid var(--border-strong);
    background: rgba(255,255,255,0.03);
    color: var(--text-muted);
    transition: all 0.3s ease;
}
.step-item.active { color: var(--text); }
.step-item.active .num {
    background: linear-gradient(135deg, var(--coral), var(--violet));
    border-color: transparent;
    color: #fff;
    box-shadow: 0 0 16px rgba(255,107,107,0.35);
    animation: scaleIn 0.4s var(--spring);
}
.step-item.done { color: var(--teal); }
.step-item.done .num { border-color: var(--teal); color: var(--teal); background: var(--teal-soft); }
.step-arrow { color: var(--border-strong); font-size: 0.85rem; }

/* ============ BUTTONS ============ */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-family: var(--sans);
    border: 1px solid var(--border-strong);
    background: rgba(255,255,255,0.04);
    color: var(--text);
    padding: 11px 20px;
    transition: all 0.2s var(--ease-out);
    width: 100%;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 0; height: 0;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
    transform: translate(-50%, -50%);
    transition: width 0.5s ease, height 0.5s ease;
}
.stButton > button:active::after { width: 300px; height: 300px; }
.stButton > button:hover {
    border-color: var(--coral);
    background: var(--coral-soft);
    color: #fff;
    box-shadow: 0 0 20px rgba(255,107,107,0.15);
    transform: translateY(-1px);
}
.stButton > button:active { transform: scale(0.97); }
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, var(--coral) 0%, var(--violet) 100%);
    border: none;
    color: #fff;
    box-shadow: 0 6px 24px rgba(255,107,107,0.35);
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 32px rgba(255,107,107,0.5);
    filter: brightness(1.12);
    transform: translateY(-2px) scale(1.01);
}
.stButton > button[kind="secondary"][data-danger="true"] {
    border-color: rgba(255,107,107,0.4);
    color: var(--coral);
}
.stButton > button[kind="secondary"][data-danger="true"]:hover {
    background: rgba(255,107,107,0.12);
    border-color: var(--coral);
}

/* ============ INPUTS ============ */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: var(--sans);
}
.stTextInput input:focus {
    border-color: var(--violet);
    box-shadow: 0 0 0 3px rgba(167,139,250,0.15);
}

/* ============ METRICS ============ */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 22px;
    transition: transform 0.3s var(--spring), border-color 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: var(--border-strong);
    box-shadow: var(--shadow-hover);
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--coral), var(--violet), var(--blue));
    opacity: 0;
    transition: opacity 0.3s ease;
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetric"] label {
    color: var(--text-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: var(--sans);
}
[data-testid="stMetricValue"] {
    font-family: var(--serif);
    color: var(--text);
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* ============ CUSTOM ANIMATED BAR CHART ============ */
.watten-chart { width: 100%; padding: 12px 4px; }
.watten-bar {
    transition: transform 0.3s var(--spring), filter 0.3s ease;
    transform-origin: bottom;
    cursor: pointer;
}
.watten-bar:hover { transform: scaleY(1.06); filter: brightness(1.2); }
.watten-bar-label { font-family: var(--sans); font-size: 11px; fill: var(--text-muted); }
.watten-bar-value { font-family: var(--serif); font-size: 13px; fill: var(--text); font-weight: 700; }

/* ============ CATEGORY CHIPS ============ */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: var(--radius-pill);
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid transparent;
    transition: transform 0.2s var(--spring);
}
.chip:hover { transform: scale(1.08); }
.chip-coral   { background: var(--coral-soft);  color: var(--coral);  border-color: rgba(255,107,107,0.25); }
.chip-amber   { background: var(--amber-soft);  color: var(--amber);  border-color: rgba(255,217,61,0.25); }
.chip-teal    { background: var(--teal-soft);   color: var(--teal);   border-color: rgba(107,203,119,0.25); }
.chip-violet  { background: var(--violet-soft); color: var(--violet); border-color: rgba(167,139,250,0.25); }
.chip-blue    { background: var(--blue-soft);   color: var(--blue);   border-color: rgba(77,150,255,0.25); }

/* ============ DATAFRAME ============ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}
[data-testid="stDataFrame"] [role="columnheader"] {
    background: var(--surface-2);
    color: var(--text-muted);
    font-weight: 600;
    font-family: var(--sans);
}

/* ============ EXPANDER ============ */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}
[data-testid="stExpander"] summary { color: var(--text); font-family: var(--sans); font-weight: 500; }

/* ============ TABS ============ */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    padding: 8px 16px;
    border-radius: 8px 8px 0 0;
    color: var(--text-muted);
    font-family: var(--sans);
}
.stTabs [aria-selected="true"] {
    color: var(--text);
    border-bottom: 2px solid var(--coral);
    background: var(--coral-soft);
}

/* ============ ALERTS ============ */
.stAlert { border-radius: var(--radius); border: 1px solid var(--border); }
[data-testid="stAlert"][data-baseweb="notification"] { background: rgba(255,255,255,0.03); }

/* ============ SIDEBAR ============ */
[data-testid="stSidebar"] {
    background: #101010;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container { padding-top: 32px; }

/* ============ PROGRESS — shimmer ============ */
[data-testid="stProgress"] { z-index: 1; position: relative; }
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--coral), var(--violet), var(--blue), var(--coral));
    background-size: 300% 100%;
    animation: shimmer 2.5s linear infinite;
}
@keyframes shimmer {
    0%   { background-position: 0% 0; }
    100% { background-position: 300% 0; }
}

/* ============ HAND-DRAWN DOODLE EMPTY STATE ============ */
.doodle-empty {
    text-align: center;
    padding: 40px 20px;
    opacity: 0.9;
}
.doodle-empty svg { max-width: 160px; margin: 0 auto 16px; }
.doodle-empty .doodle-title { font-family: var(--serif); font-size: 1.3rem; color: var(--text); margin-bottom: 6px; }
.doodle-empty .doodle-sub { font-family: var(--sans); color: var(--text-muted); font-size: 0.92rem; }

/* ============ TOOLTIP ============ */
.tooltip { position: relative; display: inline-block; cursor: help; }
.tooltip .tip {
    visibility: hidden;
    width: 190px;
    background: var(--surface-3);
    color: var(--text);
    text-align: center;
    border-radius: 10px;
    border: 1px solid var(--border-strong);
    padding: 10px 14px;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%) translateY(4px);
    font-size: 0.78rem;
    z-index: 100;
    opacity: 0;
    transition: opacity 0.25s ease, transform 0.25s ease;
    font-family: var(--sans);
}
.tooltip:hover .tip { visibility: visible; opacity: 1; transform: translateX(-50%) translateY(0); }

/* ============ BACK NAV ============ */
.back-nav {
    display: inline-flex; align-items: center; gap: 6px;
    color: var(--text-muted);
    font-size: 0.86rem;
    cursor: pointer;
    padding: 6px 0;
    transition: color 0.2s, transform 0.2s;
    border: none;
    background: none;
    font-family: var(--sans);
}
.back-nav:hover { color: var(--text); transform: translateX(-3px); }

/* ============ TOGGLE ============ */
.stToggle > label { font-family: var(--sans); color: var(--text); }
.stToggle [data-baseweb="switch"] > div {
    background: linear-gradient(135deg, var(--coral), var(--violet));
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
    .hero h1 { font-size: 2.3rem; }
    .hero { padding: 36px 12px 24px; }
    .glass-card { padding: 20px 18px; }
}
</style>
"""

st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)


# ---------- Helpers ----------
def inject_css(css: str) -> None:
    """Inject additional CSS into the app."""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def format_bytes(num: float) -> str:
    """Format a byte count into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def get_config() -> dict[str, Any]:
    """Load config with caching to avoid re-reading on every rerun."""
    if "config" not in st.session_state:
        st.session_state["config"] = load_config()
    return st.session_state["config"]


# ---------- SVG doodle / chart helpers ----------
def render_wavy_underline(text: str, color: str = "#ff6b6b") -> str:
    """Render a heading with a hand-drawn wavy underline animation."""
    return (
        f'<span class="wavy-underline">{text}'
        f'<svg viewBox="0 0 100 10" preserveAspectRatio="none">'
        f'<path d="M2,6 Q15,2 25,6 T50,6 T75,6 T98,6" stroke="{color}" fill="none" '
        f'stroke-width="2.5" stroke-linecap="round"/></svg></span>'
    )


def render_empty_state(emoji: str, title: str, sub: str) -> None:
    """Render a hand-drawn-style empty state."""
    st.markdown(
        f"""
        <div class="doodle-empty anim-scale-in">
            <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="60" cy="60" r="48" stroke="#ff6b6b" stroke-width="2.5"
                        stroke-dasharray="8 6" stroke-linecap="round" fill="none"/>
                <circle cx="60" cy="60" r="38" stroke="#a78bfa" stroke-width="2"
                        stroke-dasharray="4 8" stroke-linecap="round" fill="none" opacity="0.6"/>
                <text x="60" y="72" text-anchor="middle" font-size="32">{emoji}</text>
                <path d="M20,100 Q40,92 60,100 T100,100" stroke="#ffd93d" stroke-width="2.5"
                      stroke-linecap="round" fill="none" opacity="0.5"/>
            </svg>
            <div class="doodle-title">{title}</div>
            <div class="doodle-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_watten_bar_chart(data: list[dict], x_key: str, y_key: str) -> None:
    """
    Render a custom Wattenberger-style animated bar chart using inline SVG.

    Args:
        data: List of dicts with x_key and y_key.
        x_key: Key for category labels.
        y_key: Key for numeric values.
    """
    if not data:
        return

    max_val = max(d[y_key] for d in data) or 1
    n = len(data)
    bar_height = 220
    bar_width = 44
    gap = (820 - n * bar_width) / (n + 1) if n * bar_width < 820 else 18
    total_width = n * bar_width + (n + 1) * gap

    colors = [
        "#ff6b6b",
        "#ffd93d",
        "#6bcb77",
        "#a78bfa",
        "#4d96ff",
        "#ff9f43",
        "#00d2d3",
        "#fd79a8",
    ]

    bars = []
    for i, d in enumerate(data):
        h = max(4, (d[y_key] / max_val) * bar_height)
        x = gap + i * (bar_width + gap)
        y = bar_height - h + 30
        color = colors[i % len(colors)]
        bars.append(
            f"""
            <g class="watten-bar">
                <rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{h:.1f}"
                      rx="8" fill="{color}" opacity="0.9">
                    <animate attributeName="height" from="0" to="{h:.1f}"
                             dur="0.8s" begin="{i * 0.1}s" fill="freeze"/>
                    <animate attributeName="y" from="{bar_height + 30}" to="{y:.1f}"
                             dur="0.8s" begin="{i * 0.1}s" fill="freeze"/>
                </rect>
                <text class="watten-bar-value" x="{x + bar_width / 2:.1f}"
                      y="{y - 8:.1f}" text-anchor="middle">{d[y_key]}</text>
                <text class="watten-bar-label" x="{x + bar_width / 2:.1f}"
                      y="{bar_height + 48}" text-anchor="middle">{d[x_key]}</text>
            </g>
            """
        )

    svg = (
        f'<svg class="watten-chart" viewBox="0 0 {total_width:.0f} {bar_height + 60}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>'
    )
    st.markdown(svg, unsafe_allow_html=True)


def render_status_pill() -> None:
    """Render the current mode status pill (dry-run vs real)."""
    real = st.session_state.get("real_mode", False)
    label = "Real Mode" if real else "Dry-run Mode"
    klass = "real" if real else "dry"
    st.markdown(
        f'<span class="status-pill {klass}"><span class="dot"></span>{label}</span>',
        unsafe_allow_html=True,
    )


def render_step_tracker(steps: list[tuple[str, bool]]) -> None:
    """
    Render a horizontal step tracker.

    Args:
        steps: List of (label, is_done) tuples. The first not-done step
               (with False) is highlighted as active.
    """
    html = ['<div class="step-tracker anim-fade-in">']
    active_seen = False
    for i, (label, done) in enumerate(steps):
        if done:
            cls = "done"
        elif not active_seen:
            cls = "active"
            active_seen = True
        else:
            cls = ""
        html.append(f'<span class="step-item {cls}"><span class="num">{i + 1}</span>{label}</span>')
        if i < len(steps) - 1:
            html.append('<span class="step-arrow">›</span>')
    html.append("</div>")
    st.markdown(" ".join(html), unsafe_allow_html=True)


def set_step(step: int) -> None:
    """Set the current wizard step in session state."""
    st.session_state["step"] = step


def render_back_button(target_step: int) -> None:
    """Render a subtle back navigation button."""
    st.markdown(
        f'<button class="back-nav" onclick="window.streamlit.setComponentValue'
        f'({{step: {target_step}}})">← Back</button>',
        unsafe_allow_html=True,
    )


def check_auth() -> bool:
    """
    Check if the user is authenticated (if auth is enabled).
    Returns True if authenticated (or auth disabled), False otherwise.
    """
    auth_enabled = os.getenv("FOLDER_CLEANUP_AUTH_ENABLED", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "y",
    )
    if not auth_enabled:
        return True

    if st.session_state.get("authenticated", False):
        return True

    st.markdown("### 🔒 Login Required")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            expected_user = os.getenv("FOLDER_CLEANUP_AUTH_USERNAME", "admin")
            expected_pass = os.getenv("FOLDER_CLEANUP_AUTH_PASSWORD", "change-me-please")
            if username == expected_user and password == expected_pass:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
    return False


# ---------- Blob background wrapper ----------
st.markdown('<div class="blob-bg">', unsafe_allow_html=True)

# ---------- Auth gate ----------
if not check_auth():
    st.stop()


# ---------- Wizard state ----------
if "step" not in st.session_state:
    st.session_state["step"] = 1


# ============================================================
# STEP 1 — START (Hero + Folder Picker)
# ============================================================
def render_step_start() -> None:
    """Render the hero + folder picker step."""
    st.markdown(
        f"""
        <div class="hero anim-fade-up">
            <span class="badge"><span class="dot-glow"></span>Folder Cleanup Tool</span>
            <h1>{render_wavy_underline("Clean your folder. Effortlessly.")}</h1>
            <p class="sub">Scan, deduplicate, rename, organize, and archive files — safely, with a full preview and instant undo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_status_pill()

    st.markdown('<div class="anim-fade-up-1">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📁 Choose a folder")
        st.caption("Enter the full path to the folder you want to clean up.")

        folder_path = st.text_input("Folder path", placeholder="C:\\Users\\you\\Downloads\\messy")

        recursive = st.checkbox("Include subfolders", value=False)

        if folder_path:
            if os.path.isdir(folder_path):
                st.success(f"✅ Folder found: `{folder_path}`")
                st.session_state["folder_path"] = folder_path
                st.session_state["recursive"] = recursive

                if st.button("Continue → Scan Folder", type="primary", use_container_width=True):
                    set_step(2)
                    st.rerun()
            else:
                st.error("That folder path doesn't exist. Please check it and try again.")
        else:
            render_empty_state("📂", "Pick a folder to begin", "Enter a path above to get started.")

        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# STEP 2 — SCAN & PREVIEW
# ============================================================
def render_step_scan() -> None:
    """Render the scan + preview step with data visualization."""
    folder_path = st.session_state.get("folder_path", "")
    recursive = st.session_state.get("recursive", False)

    st.markdown(
        f"""
        <div class="hero anim-fade-up" style="padding: 24px 0 16px;">
            <h1 style="font-size: 2rem;">{render_wavy_underline("Scan Preview")}</h1>
            <p class="sub">Here's what's in <code>{folder_path}</code></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_step_tracker([("Start", True), ("Scan", True), ("Run", False), ("Results", False)])

    # Scan button
    if st.button("🔍 (Re)Scan Folder", use_container_width=True):
        with st.spinner("Scanning..."):
            file_list = scanner.scan_folder(folder_path, recursive=recursive)
        st.session_state["file_list"] = file_list
        st.session_state["scan_done"] = True

    if not st.session_state.get("scan_done"):
        render_empty_state(
            "🔍", "Ready to scan", "Click **Scan Folder** to analyze the folder contents."
        )
        return

    file_list: list[dict] = st.session_state["file_list"]

    if not file_list:
        render_empty_state("🎉", "Nothing to clean", "No files found in this folder.")
        return

    # ---- Summary metrics ----
    total_size = sum(f["size_bytes"] for f in file_list)
    config = get_config()
    categories = config.get("categories", {})

    # Simple category count
    cat_counts: dict[str, int] = {}
    for f in file_list:
        ext = f["extension"]
        cat = "Other"
        for c, exts in categories.items():
            if ext in exts:
                cat = c
                break
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Files", len(file_list))
    col2.metric("Total Size", format_bytes(total_size))
    col3.metric("Categories", len(cat_counts))
    col4.metric("Subfolders", "Yes" if recursive else "No")

    st.markdown('<div class="anim-fade-up-2">', unsafe_allow_html=True)

    # ---- Category breakdown ----
    st.markdown("#### 📊 Files by category")
    if cat_counts:
        chart_data = [
            {"Category": k, "Files": v} for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])
        ]
        render_watten_bar_chart(chart_data, "Category", "Files")

    # ---- File preview table ----
    st.markdown("#### 🗂️ File preview")
    preview_rows = [
        {
            "Name": f["name"],
            "Category": next(
                (c for c, exts in categories.items() if f["extension"] in exts),
                "Other",
            ),
            "Size": format_bytes(f["size_bytes"]),
            "Modified": f["modified_date"].strftime("%Y-%m-%d"),
        }
        for f in file_list[:100]
    ]
    st.dataframe(preview_rows, use_container_width=True)
    if len(file_list) > 100:
        st.caption(f"Showing first 100 of {len(file_list)} files.")

    # ---- Lazy: show duplicate potential ----
    st.markdown("#### 🔁 Duplicate check")
    if st.button("Check for duplicates", use_container_width=True):
        with st.spinner("Hashing files..."):
            from folder_cleanup.deduplicator import find_duplicates

            dupes = find_duplicates(file_list)
        if dupes:
            st.warning(f"Found **{len(dupes)}** duplicate groups.")
            st.session_state["dupe_groups"] = dupes
        else:
            st.success("No duplicates found. 🎉")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Navigation ----
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            set_step(1)
            st.rerun()
    with col2:
        if st.button("Continue → Configure & Run", type="primary", use_container_width=True):
            set_step(3)
            st.rerun()


# ============================================================
# STEP 3 — CONFIGURE & RUN
# ============================================================
def render_step_run() -> None:
    """Render the configure + run step with safety gates."""
    folder_path = st.session_state.get("folder_path", "")
    recursive = st.session_state.get("recursive", False)
    config = get_config()

    st.markdown(
        """
        <div class="hero anim-fade-up" style="padding: 24px 0 16px;">
            <h1 style="font-size: 2rem;">Configure & Run</h1>
            <p class="sub">Tune the cleanup, then run it — safely.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_step_tracker([("Start", True), ("Scan", True), ("Run", True), ("Results", False)])

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="anim-fade-up-1">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Cleanup settings")

        # Dry-run / real mode toggle
        st.markdown("##### Mode")
        real_mode = st.toggle(
            "Real mode (moves files)",
            value=st.session_state.get("real_mode", False),
            help="Dry-run only previews. Real mode actually moves files.",
        )
        st.session_state["real_mode"] = real_mode
        render_status_pill()

        if real_mode:
            st.warning(
                "⚠️ **Real mode is ON.** Files will actually be moved. An undo log will be saved."
            )

        st.markdown("---")

        # Rename pattern with live preview
        st.markdown("##### Rename pattern")
        pattern = st.text_input(
            "Pattern",
            value=config.get("rename_pattern", "{name}{ext}"),
            help="Supported: {name}, {ext}, {date}",
        )
        preview_name = pattern.format(name="report", ext=".pdf", date="2025-01-01")
        st.caption(f"Preview: `{preview_name}`")

        # Archive age
        st.markdown("##### Archive age")
        age_days = st.slider(
            "Archive files older than (days)",
            min_value=0,
            max_value=730,
            value=int(config.get("archive_age_days", 180)),
            step=30,
        )
        st.caption(f"Files older than **{age_days}** days will be archived.")

        st.markdown("---")

        # Advanced settings
        with st.expander("Advanced settings"):
            st.caption("These are persisted to config.json on save.")
            categories = config.get("categories", {})
            st.write("**Categories:**")
            for cat, exts in list(categories.items())[:6]:
                st.text_input(
                    f"{cat} extensions",
                    value=", ".join(exts),
                    key=f"cat_{cat}",
                )
            st.caption("Note: Advanced category edits are applied on save.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="anim-fade-up-2">', unsafe_allow_html=True)
        st.markdown("#### 📁 Target")
        st.code(folder_path, language=None)
        st.caption(f"Recursive: {'Yes' if recursive else 'No'}")

        st.markdown("#### 🚀 Run")
        if st.button(
            "Run Cleanup",
            type="primary",
            use_container_width=True,
            disabled=False,
        ):
            # Safety gate for real mode
            if real_mode:
                st.session_state["confirm_real"] = True
                st.rerun()
            else:
                run_pipeline_with_progress(folder_path, config, dry_run=True, recursive=recursive)
                set_step(4)
                st.rerun()

        if st.session_state.get("confirm_real"):
            st.warning(
                "⚠️ **Confirm real run:** This will actually move files. An undo log will be saved and can be used to reverse."
            )
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("Yes, run for real", use_container_width=True):
                    st.session_state["confirm_real"] = False
                    run_pipeline_with_progress(
                        folder_path, config, dry_run=False, recursive=recursive
                    )
                    set_step(4)
                    st.rerun()
            with col_c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["confirm_real"] = False
                    st.rerun()

        st.markdown("---")
        if st.button("← Back to Scan", use_container_width=True):
            set_step(2)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def run_pipeline_with_progress(
    folder_path: str,
    config: dict[str, Any],
    dry_run: bool,
    recursive: bool,
) -> None:
    """
    Run the cleanup pipeline with a staged progress bar.

    Args:
        folder_path: Folder to clean.
        config: Config dict.
        dry_run: Whether to run in dry-run mode.
        recursive: Whether to scan subfolders.
    """
    progress = st.progress(0)
    status = st.empty()

    steps = ["Scanning", "Deduplicating", "Renaming", "Organizing", "Archiving"]

    def report(step_idx: int, msg: str) -> None:
        progress.progress((step_idx + 1) / len(steps))
        status.info(f"**{steps[step_idx]}...** {msg}")

    # Run the pipeline with the progress callback wired to the UI
    summary = pipeline.run_pipeline(
        folder_path,
        config,
        dry_run=dry_run,
        recursive=recursive,
        progress_callback=report,
    )

    progress.progress(1.0)
    status.success("Cleanup complete!")
    st.session_state["last_summary"] = summary


# ============================================================
# STEP 4 — RESULTS & UNDO
# ============================================================
def render_step_results() -> None:
    """Render the results dashboard + undo."""
    summary = st.session_state.get("last_summary")

    st.markdown(
        """
        <div class="hero anim-fade-up" style="padding: 24px 0 16px;">
            <h1 style="font-size: 2rem;">Results</h1>
            <p class="sub">Here's what happened.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_step_tracker([("Start", True), ("Scan", True), ("Run", True), ("Results", True)])

    if not summary:
        render_empty_state(
            "📊", "No results yet", "Run the cleanup from the previous step to see results."
        )
        return

    # ---- Summary dashboard ----
    st.markdown("#### 📋 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Files scanned", summary.get("files_scanned", 0))
    col2.metric("Duplicates", summary.get("duplicates_found", 0))
    col3.metric("Renamed", summary.get("files_renamed", 0))
    col4.metric("Organized", summary.get("files_organized", 0))

    col5, col6, col7 = st.columns(3)
    col5.metric("Archived", summary.get("files_archived", 0))
    col6.metric("Mode", "Dry" if summary.get("dry_run", True) else "Real")

    # ---- Charts ----
    st.markdown('<div class="anim-fade-up-2">', unsafe_allow_html=True)
    st.markdown("#### 📊 Breakdown")
    chart_data = [
        {"Action": "Renamed", "Count": summary.get("files_renamed", 0)},
        {"Action": "Organized", "Count": summary.get("files_organized", 0)},
        {"Action": "Archived", "Count": summary.get("files_archived", 0)},
        {"Action": "Duplicates", "Count": summary.get("duplicates_found", 0)},
    ]
    render_watten_bar_chart(chart_data, "Action", "Count")

    # ---- Undo ----
    st.markdown("---")
    st.markdown("#### ↩️ Undo Last Real Run")
    st.caption("This reverses the most recent real (non dry-run) cleanup.")

    if st.button("Undo Last Run", use_container_width=True):
        with st.spinner("Undoing..."):
            undone = undo.undo_actions()
        if undone > 0:
            st.success(f"Undo complete. {undone} actions reversed.")
        else:
            st.info("Nothing to undo.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Navigation ----
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Run", use_container_width=True):
            set_step(3)
            st.rerun()
    with col2:
        if st.button("Start Over", use_container_width=True):
            for key in [
                "step",
                "folder_path",
                "file_list",
                "scan_done",
                "last_summary",
                "confirm_real",
            ]:
                st.session_state.pop(key, None)
            st.rerun()


# ============================================================
# MAIN ROUTER
# ============================================================
def main() -> None:
    """Render the current wizard step."""

    # Sidebar: app info + step tracker
    with st.sidebar:
        st.markdown("### ✨ Folder Cleanup")
        st.caption("A safe, guided folder organizer.")
        st.markdown("---")
        st.markdown("**Current run:**")
        if st.session_state.get("folder_path"):
            st.code(st.session_state["folder_path"], language=None)
        else:
            st.caption("No folder selected yet.")
        st.markdown("---")
        st.caption("Built with Streamlit · Claude × Wattenberger design")

    # Router
    step = st.session_state.get("step", 1)
    if step == 1:
        render_step_start()
    elif step == 2:
        render_step_scan()
    elif step == 3:
        render_step_run()
    elif step == 4:
        render_step_results()

    # Close blob-bg wrapper
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
