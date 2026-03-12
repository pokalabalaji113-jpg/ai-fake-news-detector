"""
AI Fake News Detector PRO — Streamlit Frontend
Beautiful UI with all features
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io
import base64

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Fake News Detector PRO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://localhost:8000"

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #060810 0%, #0a0d18 50%, #080d1a 100%);
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #0f1629 0%, #1a1040 50%, #0f1629 100%);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 24px;
    padding: 48px 40px;
    text-align: center;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; left: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.10) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    color: rgba(255,255,255,0.55);
    font-size: 1.05rem;
    margin-top: 12px;
    font-weight: 300;
}
.hero-badges {
    margin-top: 18px;
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
}
.badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.3);
    color: #a78bfa;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
}
.badge-blue {
    background: rgba(59,130,246,0.15);
    border-color: rgba(59,130,246,0.3);
    color: #60a5fa;
}
.badge-pink {
    background: rgba(244,114,182,0.15);
    border-color: rgba(244,114,182,0.3);
    color: #f472b6;
}

/* Verdict cards */
.verdict-real {
    background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05));
    border: 2px solid rgba(16,185,129,0.5);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
    margin: 20px 0;
}
.verdict-fake {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
    border: 2px solid rgba(239,68,68,0.5);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
    margin: 20px 0;
}
.verdict-icon { font-size: 4rem; margin-bottom: 8px; }
.verdict-text-real { font-size: 2.8rem; font-weight: 800; color: #10b981; letter-spacing: 4px; }
.verdict-text-fake { font-size: 2.8rem; font-weight: 800; color: #ef4444; letter-spacing: 4px; }
.verdict-summary { color: rgba(255,255,255,0.75); font-size: 1rem; margin-top: 12px; line-height: 1.7; max-width: 600px; margin-left: auto; margin-right: auto; }

/* Metric boxes */
.metric-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    height: 100%;
}
.metric-label {
    color: rgba(255,255,255,0.4);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
}

/* Progress bar */
.prog-track {
    background: rgba(255,255,255,0.07);
    border-radius: 999px;
    height: 8px;
    margin-top: 10px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 1s ease;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
}
.card-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.35);
    margin-bottom: 14px;
}

/* List items */
.item-reason {
    background: rgba(96,165,250,0.08);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    margin: 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
    line-height: 1.5;
}
.item-flag {
    background: rgba(239,68,68,0.08);
    border-left: 3px solid #ef4444;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    margin: 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
    line-height: 1.5;
}
.item-positive {
    background: rgba(16,185,129,0.08);
    border-left: 3px solid #10b981;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    margin: 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
    line-height: 1.5;
}
.item-rec {
    background: rgba(139,92,246,0.08);
    border-left: 3px solid #8b5cf6;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
    line-height: 1.5;
}

/* Explanation box */
.explanation-box {
    background: rgba(139,92,246,0.06);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 14px;
    padding: 20px;
    color: rgba(255,255,255,0.8);
    font-size: 0.92rem;
    line-height: 1.8;
    margin: 10px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(255,255,255,0.5) !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(139,92,246,0.25) !important;
    color: #a78bfa !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060810 0%, #0a0d18 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background: #0f1629 !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    caret-color: #a78bfa !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(139,92,246,0.7) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: rgba(255,255,255,0.3) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.3) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 14px 28px !important;
    font-size: 1rem !important;
    width: 100% !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.35) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed rgba(139,92,246,0.3) !important;
    border-radius: 14px !important;
    padding: 10px !important;
}

/* History chip */
.history-chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 12px;
    margin: 6px 0;
    cursor: pointer;
}
.history-verdict-real { color: #10b981; font-size: 0.82rem; font-weight: 700; }
.history-verdict-fake { color: #ef4444; font-size: 0.82rem; font-weight: 700; }
.history-meta { color: rgba(255,255,255,0.35); font-size: 0.72rem; margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

/* Stat chip */
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0; }
.stat-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.6);
    font-family: 'JetBrains Mono', monospace;
}

/* Hide streamlit default */
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: rgba(255,255,255,0.06) !important; }
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "total_analyzed" not in st.session_state:
    st.session_state.total_analyzed = 0
if "total_fake" not in st.session_state:
    st.session_state.total_fake = 0
if "total_real" not in st.session_state:
    st.session_state.total_real = 0


# ── Helpers ───────────────────────────────────────────────────
def call_api(endpoint, **kwargs):
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", timeout=60, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend! Make sure you ran: `python run.py`")
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        st.error(f"❌ API Error: {detail}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def progress_bar(value, color):
    return f"""
    <div class="prog-track">
        <div class="prog-fill" style="width:{value}%;background:{color}"></div>
    </div>"""


def save_history(result, source_label, item_id=None, category_type=None):
    verdict = result.get("verdict", "UNKNOWN")
    st.session_state.history.insert(0, {
        "verdict": verdict,
        "confidence": result.get("confidence", 0),
        "category": result.get("category", "Unknown"),
        "summary": result.get("summary", "")[:80],
        "source": source_label,
        "time": datetime.now().strftime("%H:%M:%S"),
        "id": item_id,
        "category_type": category_type,
        "get_link": f"/analyze/{category_type}/{item_id}" if item_id and category_type else None,
        "delete_link": f"/analyze/{category_type}/{item_id}" if item_id and category_type else None,
    })
    st.session_state.history = st.session_state.history[:15]
    st.session_state.total_analyzed += 1
    if verdict == "FAKE":
        st.session_state.total_fake += 1
    else:
        st.session_state.total_real += 1


def generate_pdf_report(result, source_label):
    """Generate a simple text-based PDF report."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('title', parent=styles['Title'],
                                     fontSize=22, textColor=colors.HexColor('#7c3aed'),
                                     spaceAfter=6, alignment=TA_CENTER)
        story.append(Paragraph("🔍 AI Fake News Detector PRO", title_style))

        sub_style = ParagraphStyle('sub', parent=styles['Normal'],
                                   fontSize=10, textColor=colors.HexColor('#666666'),
                                   spaceAfter=4, alignment=TA_CENTER)
        story.append(Paragraph(f"Analysis Report — {datetime.now().strftime('%B %d, %Y %H:%M')}", sub_style))
        story.append(Paragraph(f"Source: {source_label}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 0.2*inch))

        # Verdict
        verdict = result.get("verdict", "UNKNOWN")
        verdict_color = colors.HexColor('#10b981') if verdict == "REAL" else colors.HexColor('#ef4444')
        verdict_style = ParagraphStyle('verdict', parent=styles['Title'],
                                       fontSize=28, textColor=verdict_color,
                                       spaceAfter=6, alignment=TA_CENTER)
        icon = "✅" if verdict == "REAL" else "🚫"
        story.append(Paragraph(f"{icon} {verdict}", verdict_style))

        # Scores table
        data = [
            ['Metric', 'Score'],
            ['Confidence', f"{result.get('confidence', 0)}%"],
            ['Credibility Score', f"{result.get('credibility_score', 0)}/100"],
            ['Category', result.get('category', 'Unknown')],
            ['Language Tone', result.get('language_tone', 'Unknown')],
            ['Clickbait Score', f"{result.get('clickbait_score', 0)}/100"],
            ['Source Credibility', result.get('source_credibility', 'Unknown')],
        ]
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))

        # Summary
        h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=13,
                             textColor=colors.HexColor('#1f2937'), spaceAfter=6)
        body = ParagraphStyle('body', parent=styles['Normal'], fontSize=10,
                               textColor=colors.HexColor('#374151'), spaceAfter=4, leading=16)

        story.append(Paragraph("Summary", h2))
        story.append(Paragraph(result.get("summary", ""), body))
        story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph("Detailed Explanation", h2))
        story.append(Paragraph(result.get("detailed_explanation", ""), body))
        story.append(Spacer(1, 0.1*inch))

        # Reasons
        if result.get("reasons"):
            story.append(Paragraph("Key Reasons", h2))
            for r in result.get("reasons", []):
                story.append(Paragraph(f"• {r}", body))
            story.append(Spacer(1, 0.1*inch))

        # Red flags
        if result.get("red_flags"):
            story.append(Paragraph("Red Flags", h2))
            for f in result.get("red_flags", []):
                story.append(Paragraph(f"⚠ {f}", body))
            story.append(Spacer(1, 0.1*inch))

        # Positive signals
        if result.get("positive_signals"):
            story.append(Paragraph("Positive Signals", h2))
            for p in result.get("positive_signals", []):
                story.append(Paragraph(f"✓ {p}", body))
            story.append(Spacer(1, 0.1*inch))

        # Recommendation
        story.append(Paragraph("Recommendation", h2))
        story.append(Paragraph(result.get("recommendation", ""), body))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        footer = ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                                textColor=colors.HexColor('#9ca3af'), alignment=TA_CENTER)
        story.append(Paragraph("Generated by AI Fake News Detector PRO · Powered by Google Gemini AI", footer))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
        return None


def render_result(data, source_label, category_type=None):
    result = data.get("result", {})
    item_id = data.get("id", None)
    verdict        = result.get("verdict", "UNKNOWN")
    confidence     = result.get("confidence", 0)
    credibility    = result.get("credibility_score", 0)
    summary        = result.get("summary", "")
    explanation    = result.get("detailed_explanation", "")
    reasons        = result.get("reasons", [])
    red_flags      = result.get("red_flags", [])
    positives      = result.get("positive_signals", [])
    category       = result.get("category", "Unknown")
    recommendation = result.get("recommendation", "")
    ml_score       = result.get("ml_score", None)
    lang_tone      = result.get("language_tone", "Unknown")
    clickbait      = result.get("clickbait_score", 0)
    src_cred       = result.get("source_credibility", "Unknown")

    is_real    = verdict == "REAL"
    v_class    = "real" if is_real else "fake"
    v_icon     = "✅" if is_real else "🚫"
    v_color    = "#10b981" if is_real else "#ef4444"
    prog_color = "#10b981" if is_real else "#ef4444"

    # Save history
    save_history(result, source_label, item_id=item_id, category_type=category_type)

    # ── ID Banner ──
    if item_id and category_type:
        st.markdown(f"""
        <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.25);
        border-radius:12px;padding:12px 20px;margin-bottom:16px;
        display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:rgba(255,255,255,0.6)">
                💾 Analysis saved to backend
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
                <span style="background:rgba(139,92,246,0.2);border:1px solid rgba(139,92,246,0.4);
                color:#a78bfa;padding:4px 12px;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.82rem">
                    🆔 ID: {item_id}
                </span>
                <span style="background:rgba(96,165,250,0.1);border:1px solid rgba(96,165,250,0.3);
                color:#60a5fa;padding:4px 12px;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.75rem">
                    GET /analyze/{category_type}/{item_id}
                </span>
                <span style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                color:#ef4444;padding:4px 12px;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.75rem">
                    DELETE /analyze/{category_type}/{item_id}
                </span>
                <span style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
                color:#10b981;padding:4px 12px;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.75rem">
                    PUT /analyze/{category_type}/{item_id}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Verdict Banner ──
    st.markdown(f"""
    <div class="verdict-{v_class}">
        <div class="verdict-icon">{v_icon}</div>
        <div class="verdict-text-{v_class}">{verdict}</div>
        <div style="margin-top:8px">
            <span style="background:rgba(255,255,255,0.1);border-radius:20px;padding:4px 14px;
            font-size:0.82rem;color:rgba(255,255,255,0.6)">📂 {category}</span>
        </div>
        <div class="verdict-summary">{summary}</div>
    </div>""", unsafe_allow_html=True)

    # ── Metrics Row ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">AI Confidence</div>
            <div class="metric-value" style="color:{v_color}">{confidence}%</div>
            {progress_bar(confidence, prog_color)}
            <div class="metric-sub">Gemini AI score</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        c_color = "#10b981" if credibility >= 60 else "#ef4444" if credibility < 40 else "#f59e0b"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Credibility</div>
            <div class="metric-value" style="color:{c_color}">{credibility}</div>
            {progress_bar(credibility, c_color)}
            <div class="metric-sub">out of 100</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        cb_color = "#ef4444" if clickbait >= 60 else "#f59e0b" if clickbait >= 30 else "#10b981"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Clickbait Score</div>
            <div class="metric-value" style="color:{cb_color}">{clickbait}</div>
            {progress_bar(clickbait, cb_color)}
            <div class="metric-sub">ML detected</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        ml_display = f"{int(ml_score*100)}" if ml_score is not None else "N/A"
        ml_color = "#ef4444" if (ml_score or 0) >= 0.6 else "#f59e0b" if (ml_score or 0) >= 0.3 else "#10b981"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">ML Fake Score</div>
            <div class="metric-value" style="color:{ml_color}">{ml_display}</div>
            {progress_bar(int((ml_score or 0)*100), ml_color)}
            <div class="metric-sub">heuristic analysis</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Extra signals row ──
    tone_color = "#ef4444" if lang_tone == "Sensational" else "#f59e0b" if lang_tone == "Biased" else "#10b981"
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-chip">🗣 Tone: <span style="color:{tone_color}">{lang_tone}</span></div>
        <div class="stat-chip">🌐 Source: {src_cred}</div>
        <div class="stat-chip">📂 Category: {category}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed Explanation ──
    if explanation:
        st.markdown('<div class="card"><div class="card-title">🧠 Detailed AI Explanation</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="explanation-box">{explanation}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Reasons + Flags ──
    col_a, col_b = st.columns(2)

    with col_a:
        if reasons:
            st.markdown('<div class="card"><div class="card-title">🔎 Key Reasons</div>', unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f'<div class="item-reason">📌 {r}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if recommendation:
            st.markdown('<div class="card"><div class="card-title">💡 Recommendation</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="item-rec">💬 {recommendation}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        if red_flags:
            st.markdown('<div class="card"><div class="card-title">⚠️ Red Flags</div>', unsafe_allow_html=True)
            for f in red_flags:
                st.markdown(f'<div class="item-flag">🚩 {f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if positives:
            st.markdown('<div class="card"><div class="card-title">✅ Positive Signals</div>', unsafe_allow_html=True)
            for p in positives:
                st.markdown(f'<div class="item-positive">✔ {p}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Gauge Chart ──
    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence,
        title={'text': "AI Confidence Score", 'font': {'color': 'white', 'size': 16}},
        number={'suffix': "%", 'font': {'color': v_color, 'size': 36}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'rgba(255,255,255,0.3)'},
            'bar': {'color': v_color, 'thickness': 0.25},
            'bgcolor': 'rgba(255,255,255,0.05)',
            'bordercolor': 'rgba(255,255,255,0.1)',
            'steps': [
                {'range': [0, 40],  'color': 'rgba(239,68,68,0.15)'},
                {'range': [40, 70], 'color': 'rgba(245,158,11,0.15)'},
                {'range': [70, 100],'color': 'rgba(16,185,129,0.15)'}
            ],
            'threshold': {
                'line': {'color': v_color, 'width': 3},
                'thickness': 0.8,
                'value': confidence
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=280,
        margin=dict(l=30, r=30, t=40, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── PDF Export ──
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(result, source_label)
    if pdf_bytes:
        st.download_button(
            label="📄 Download Full PDF Report",
            data=pdf_bytes,
            file_name=f"fake_news_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:24px 0 16px">
        <div style="font-size:3rem">🔍</div>
        <div style="font-weight:700;font-size:1.1rem;color:white;margin-top:8px">Fake News Detector</div>
        <div style="color:rgba(255,255,255,0.35);font-size:0.78rem;margin-top:4px">PRO · Powered by Gemini AI</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    # API Status
    st.markdown('<div style="color:rgba(255,255,255,0.35);font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px">System Status</div>', unsafe_allow_html=True)
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=3)
        h = resp.json()
        gem_ok = h.get("gemini_configured", False)
        st.markdown(f'<div style="color:#10b981;font-size:0.85rem;margin:4px 0">● Backend: Online</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{"#10b981" if gem_ok else "#ef4444"};font-size:0.85rem;margin:4px 0">● Gemini: {"Connected" if gem_ok else "Not configured"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#60a5fa;font-size:0.85rem;margin:4px 0">● Model: gemini-2.0-flash</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div style="color:#ef4444;font-size:0.85rem">● Backend: Offline</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:rgba(255,255,255,0.4);font-size:0.78rem;margin-top:6px">Run: python run.py</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div style="color:rgba(255,255,255,0.35);font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Session Stats</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f'<div style="text-align:center"><div style="font-size:1.4rem;font-weight:700;color:white">{st.session_state.total_analyzed}</div><div style="font-size:0.65rem;color:rgba(255,255,255,0.35)">Total</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div style="text-align:center"><div style="font-size:1.4rem;font-weight:700;color:#10b981">{st.session_state.total_real}</div><div style="font-size:0.65rem;color:rgba(255,255,255,0.35)">Real</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div style="text-align:center"><div style="font-size:1.4rem;font-weight:700;color:#ef4444">{st.session_state.total_fake}</div><div style="font-size:0.65rem;color:rgba(255,255,255,0.35)">Fake</div></div>', unsafe_allow_html=True)

    # Analytics mini chart
    if st.session_state.total_analyzed > 0:
        fig2 = go.Figure(go.Pie(
            labels=["Real", "Fake"],
            values=[st.session_state.total_real, st.session_state.total_fake],
            hole=0.6,
            marker=dict(colors=["#10b981", "#ef4444"]),
            textinfo='none'
        ))
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=120,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # History
    if st.session_state.history:
        st.markdown('<div style="color:rgba(255,255,255,0.35);font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Recent History</div>', unsafe_allow_html=True)
        for item in st.session_state.history[:6]:
            icon = "✅" if item["verdict"] == "REAL" else "🚫"
            color = "#10b981" if item["verdict"] == "REAL" else "#ef4444"
            id_badge = f'<span style="background:rgba(139,92,246,0.2);border:1px solid rgba(139,92,246,0.3);color:#a78bfa;padding:2px 8px;border-radius:6px;font-size:0.68rem;font-family:JetBrains Mono,monospace">ID:{item.get("id","?")}</span>' if item.get("id") else ""
            api_link = f'<div style="color:rgba(96,165,250,0.6);font-size:0.68rem;font-family:JetBrains Mono,monospace;margin-top:3px">GET /analyze/{item.get("category_type","")}/{item.get("id","")}</div>' if item.get("id") else ""
            st.markdown(f"""
            <div class="history-chip">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                    <span style="color:{color};font-size:0.82rem;font-weight:700">{icon} {item['verdict']}</span>
                    {id_badge}
                </div>
                <div class="history-meta">{item.get('time','')} · {item.get('confidence',0)}% · {item.get('category_type','').upper()}</div>
                {api_link}
                <div style="color:rgba(255,255,255,0.4);font-size:0.72rem;margin-top:3px">{item.get('summary','')[:55]}…</div>
            </div>""", unsafe_allow_html=True)


# ── Main Page ─────────────────────────────────────────────────

# Hero Banner
st.markdown("""
<div class="hero">
    <h1 class="hero-title">🔍 AI Fake News Detector PRO</h1>
    <p class="hero-sub">Detect misinformation, deepfakes & fake news instantly using Google Gemini AI + ML</p>
    <div class="hero-badges">
        <span class="badge">gemini-2.0-flash</span>
        <span class="badge badge-blue">fastapi</span>
        <span class="badge badge-pink">streamlit</span>
        <span class="badge">ml-heuristics</span>
        <span class="badge badge-blue">deepfake-detection</span>
        <span class="badge badge-pink">pdf-export</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Tabs ────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝  Paste Text",
    "🔗  Enter URL",
    "📁  Upload File",
    "🖼️  Image / Deepfake",
    "📊  Analytics"
])

# ── Tab 1: Paste Text ─────────────────────────────────────────
with tab1:
    st.markdown('<div style="color:rgba(255,255,255,0.45);margin-bottom:14px;font-size:0.9rem">Paste any news article text below for instant AI analysis</div>', unsafe_allow_html=True)
    article_text = st.text_area("", placeholder="Paste your news article here…\n\nFor best results, include the full article with headline and body text.\nMinimum 50 characters required.", height=280, label_visibility="collapsed", key="text_input")
    chars = len(article_text)
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f'<div style="color:rgba(255,255,255,0.25);font-size:0.75rem;text-align:right;padding-top:8px">{chars} chars</div>', unsafe_allow_html=True)
    if st.button("🔍 Analyze with Gemini AI", key="btn_text"):
        if chars < 50:
            st.warning("⚠️ Please paste at least 50 characters of article text.")
        else:
            with st.spinner("🤖 Gemini AI is analyzing the article…"):
                data = call_api("/analyze/text", json={"text": article_text})
            if data:
                st.markdown("---")
                render_result(data, "Pasted Text", category_type="text")

# ── Tab 2: URL ────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="color:rgba(255,255,255,0.45);margin-bottom:14px;font-size:0.9rem">Enter any news article URL — the AI will fetch and analyze it automatically</div>', unsafe_allow_html=True)
    url_input = st.text_input("", placeholder="https://www.bbc.com/news/article...", label_visibility="collapsed", key="url_input")
    st.markdown("""
    <div style="background:rgba(96,165,250,0.06);border:1px solid rgba(96,165,250,0.15);
    border-radius:10px;padding:10px 14px;margin:10px 0;font-size:0.82rem;color:rgba(96,165,250,0.8)">
        ℹ️ Works with BBC, Reuters, AP News, The Guardian, and most news websites
    </div>""", unsafe_allow_html=True)
    if st.button("🌐 Fetch & Analyze", key="btn_url"):
        if not url_input.startswith("http"):
            st.warning("⚠️ Please enter a valid URL starting with https://")
        else:
            with st.spinner("🌐 Fetching article and analyzing with Gemini AI…"):
                data = call_api("/analyze/url", json={"url": url_input})
            if data:
                st.markdown("---")
                render_result(data, url_input, category_type="url")

# ── Tab 3: File Upload ────────────────────────────────────────
with tab3:
    st.markdown('<div style="color:rgba(255,255,255,0.45);margin-bottom:14px;font-size:0.9rem">Upload a .txt or .pdf news article file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["txt", "pdf"], label_visibility="collapsed", key="file_input")
    if uploaded_file:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">File Name</div><div style="color:white;font-weight:600;font-size:0.85rem">{uploaded_file.name}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">File Size</div><div style="color:white;font-weight:600;font-size:0.85rem">{uploaded_file.size/1024:.1f} KB</div></div>', unsafe_allow_html=True)
        with c3:
            ftype = "PDF Document" if uploaded_file.name.endswith(".pdf") else "Text File"
            st.markdown(f'<div class="metric-box"><div class="metric-label">File Type</div><div style="color:white;font-weight:600;font-size:0.85rem">{ftype}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Analyze File", key="btn_file"):
            with st.spinner("📄 Reading and analyzing file with Gemini AI…"):
                data = call_api("/analyze/file", files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)})
            if data:
                st.markdown("---")
                render_result(data, uploaded_file.name, category_type="file")

# ── Tab 4: Image / Deepfake ───────────────────────────────────
with tab4:
    st.markdown('<div style="color:rgba(255,255,255,0.45);margin-bottom:8px;font-size:0.9rem">Upload an image to detect manipulation, deepfakes, or AI-generated content</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(244,114,182,0.06);border:1px solid rgba(244,114,182,0.15);
    border-radius:10px;padding:10px 14px;margin-bottom:14px;font-size:0.82rem;color:rgba(244,114,182,0.8)">
        🖼️ Supported: .jpg .jpeg .png .webp — Detects deepfakes, AI-generated images, photo manipulation
    </div>""", unsafe_allow_html=True)

    uploaded_img = st.file_uploader("", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed", key="img_input")
    if uploaded_img:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box" style="margin-top:10px">
                <div class="metric-label">File Name</div>
                <div style="color:white;font-weight:600;font-size:0.85rem">{uploaded_img.name}</div>
            </div>
            <div class="metric-box" style="margin-top:10px">
                <div class="metric-label">File Size</div>
                <div style="color:white;font-weight:600;font-size:0.85rem">{uploaded_img.size/1024:.1f} KB</div>
            </div>""", unsafe_allow_html=True)
            if st.button("🖼️ Analyze Image", key="btn_img"):
                with st.spinner("🤖 Gemini Vision AI is analyzing the image…"):
                    data = call_api("/analyze/image", files={"file": (uploaded_img.name, uploaded_img.getvalue(), uploaded_img.type)})
                if data:
                    st.markdown("---")
                    render_result(data, uploaded_img.name, category_type="image")

# ── Tab 5: Analytics ──────────────────────────────────────────
with tab5:
    st.markdown('<div style="color:rgba(255,255,255,0.45);margin-bottom:20px;font-size:0.9rem">Session analytics — summary of all analyses done this session</div>', unsafe_allow_html=True)

    if st.session_state.total_analyzed == 0:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:rgba(255,255,255,0.3)">
            <div style="font-size:3rem">📊</div>
            <div style="margin-top:12px;font-size:1rem">No analyses yet!</div>
            <div style="font-size:0.85rem;margin-top:8px">Go to any tab and analyze an article to see stats here.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Summary row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Total Analyzed</div><div class="metric-value" style="color:#a78bfa">{st.session_state.total_analyzed}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Real Articles</div><div class="metric-value" style="color:#10b981">{st.session_state.total_real}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Fake Articles</div><div class="metric-value" style="color:#ef4444">{st.session_state.total_fake}</div></div>', unsafe_allow_html=True)
        with m4:
            fake_pct = int((st.session_state.total_fake / st.session_state.total_analyzed) * 100) if st.session_state.total_analyzed > 0 else 0
            st.markdown(f'<div class="metric-box"><div class="metric-label">Fake Rate</div><div class="metric-value" style="color:#f59e0b">{fake_pct}%</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if len(st.session_state.history) >= 2:
            # Bar chart of confidence scores
            df = pd.DataFrame(st.session_state.history)
            colors_list = ["#10b981" if v == "REAL" else "#ef4444" for v in df["verdict"]]

            fig3 = go.Figure(go.Bar(
                x=[f"#{i+1}" for i in range(len(df))],
                y=df["confidence"].tolist(),
                marker_color=colors_list,
                text=df["verdict"].tolist(),
                textposition='outside',
            ))
            fig3.update_layout(
                title=dict(text="Confidence Scores per Analysis", font=dict(color='white', size=14)),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.6)'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Analysis #"),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Confidence %", range=[0, 110]),
                height=320,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig3, use_container_width=True)

        # History table
        if st.session_state.history:
            st.markdown('<div style="color:rgba(255,255,255,0.35);font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;margin:20px 0 10px">Analysis History</div>', unsafe_allow_html=True)
            df_display = pd.DataFrame(st.session_state.history)[["time", "verdict", "confidence", "category", "source"]]
            df_display.columns = ["Time", "Verdict", "Confidence %", "Category", "Source"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:48px 0 24px;color:rgba(255,255,255,0.18);font-size:0.8rem">
    Built with ❤️ using <span style="color:rgba(139,92,246,0.6)">Streamlit</span> ·
    <span style="color:rgba(59,130,246,0.6)">FastAPI</span> ·
    <span style="color:rgba(244,114,182,0.6)">Google Gemini AI</span> ·
    <span style="color:rgba(16,185,129,0.6)">ML Heuristics</span><br>
    <span style="font-family:'JetBrains Mono',monospace;margin-top:6px;display:inline-block">v2.0.0 PRO</span>
</div>
""", unsafe_allow_html=True)
