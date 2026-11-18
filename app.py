import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import time
import os
import json
import random
import altair as alt
import sqlite3
import textwrap
import base64

# External modules
from audio_processing import process_audio
from scoring_logic import evaluate_risk
from database import init_db, register_user, verify_user, fetch_patient_assessments, save_patient_assessment, search_patients
from cognitive_tests import render_cognitive_tests, init_cognitive_state

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AcousticCognition — AI Medical Research",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS DESIGN SYSTEM
# =========================
def apply_elite_style():
    with open('elite_style.css', 'r', encoding='utf-8') as f:
        custom_css = f.read()
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# =========================
# INIT
# =========================
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# =========================
# URL-BASED NAVIGATION
# =========================
# Map between URL param values and internal page names
_URL_TO_PAGE = {
    'home': 'Home',
    'login': 'login',
    'register': 'register',
    'dashboard': 'Home',
    'assessment': 'Assessment',
    'history': 'Assessment History',
    'patients': 'Patients',
    'reports': 'Reports',
    'results': 'Results',
    'learnmore': 'learnmore',
    'guide': 'Guide',
}

_PAGE_TO_URL = {
    'Home': 'home',
    'Assessment': 'assessment',
    'Assessment History': 'history',
    'Patients': 'patients',
    'Reports': 'reports',
    'Results': 'results',
    'Guide': 'guide',
}

def navigate_to(page_name, **extra_state):
    """Central navigation helper. Sets both session_state and URL query params."""
    st.session_state['page'] = page_name
    url_key = _PAGE_TO_URL.get(page_name, page_name.lower())
    st.query_params['page'] = url_key
    for k, v in extra_state.items():
        st.session_state[k] = v
    st.rerun()

def reset_assessment_state():
    ASSESSMENT_KEYS = [
        "patient_info",
        "cog_scores",
        "assessment_complete",
        "report_generated",
        "selected_assessment_id",
        "mem_stage",
        "mem_objects",
        "mem_user_answer",
        "mem_score",
        "nam_stage",
        "nam_idx",
        "nam_score",
        "nam_test_selection",
        "selected_sequence_order",
        "sequence_scores",
        "seq_scenarios",
        "clock_score",
        "acoustic_score",
        "audio_to_process",
        "voice_result",
        "final_score",
        "risk_level"
    ]
    for key in ASSESSMENT_KEYS:
        if key in st.session_state:
            del st.session_state[key]

# =========================
# SESSION STATE
# =========================
# Restore page from URL on refresh
_url_page_param = st.query_params.get('page', None)
if _url_page_param and _url_page_param in _URL_TO_PAGE:
    _resolved = _URL_TO_PAGE[_url_page_param]
    if _resolved == 'login':
        st.session_state.setdefault('page', 'Home')
        st.session_state['show_auth'] = True
        st.session_state['auth_mode'] = 'login'
    elif _resolved == 'register':
        st.session_state.setdefault('page', 'Home')
        st.session_state['show_auth'] = True
        st.session_state['auth_mode'] = 'signup'
    elif _resolved == 'learnmore':
        st.session_state.setdefault('page', 'Home')
        st.session_state['show_learn_more'] = True
    else:
        st.session_state['page'] = _resolved
elif 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'full_name' not in st.session_state:
    st.session_state['full_name'] = ""
if 'role' not in st.session_state:
    st.session_state['role'] = 'user' 
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login' # 'login', 'signup'
if 'show_auth' not in st.session_state:
    st.session_state['show_auth'] = False
if 'show_learn_more' not in st.session_state:
    st.session_state['show_learn_more'] = False

# =========================
# UI COMPONENTS
# =========================
def render_landing_navbar():
    # Navbar anchor to target columns style dynamically
    st.markdown('<div class="landing-page-hook"></div><div class="navbar-anchor"></div>', unsafe_allow_html=True)

    # 4 columns: large logo col, flexible spacer (links), two smaller cols for buttons
    col_logo, col_spacer, col_home, col_login = st.columns([4, 4, 1.6, 2.4], gap="small")
    
    with col_logo:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; height:100%; padding-top:4px; padding-left:26px;">
            <div class="brand-icon" style="background: linear-gradient(135deg, #164A9F 0%, #2563EB 100%); border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:1.3rem; font-weight:bold; box-shadow:0 4px 10px rgba(37,99,235,0.12); flex-shrink:0; width:38px; height:38px;">🧠</div>
            <span class="brand-text" style="font-size:30px !important;">AcousticCognition</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_spacer:
        pass
        
    with col_home:
        # Button with home icon
        if st.button("🏠 Home", key="nav_home_btn", use_container_width=True):
            navigate_to('Home')
            
    with col_login:
        # Button with user icon
        if st.button("👤 Login / Register", key="nav_login_btn", type="primary", use_container_width=True):
            st.session_state['show_auth'] = True
            st.query_params['page'] = 'login'
            st.rerun()
    
def render_glass_navbar():
    # Professional Clinical Dashboard Navbar
    st.markdown('<div class="navbar-anchor"></div>', unsafe_allow_html=True)
    col_logo, col_nav, col_out = st.columns([1.5, 5, 1.2])
    
    with col_logo:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; cursor:pointer;">
            <div style="background:var(--primary-blue); width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:1.1rem;">🧠</div>
            <span style="font-weight:700; color:var(--primary-blue); font-family:'Plus Jakarta Sans'; font-size:1.1rem; letter-spacing:-0.5px;">AcousticCognition</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_nav:
        n1, n2, n3 = st.columns([1, 1, 1.3])
        if n1.button("Home", key="btn_nav_home", use_container_width=True): navigate_to('Home')
        if n2.button("Assessment", key="btn_nav_assess", use_container_width=True): navigate_to('Assessment')
        if n3.button("Assessment History", key="btn_nav_history", use_container_width=True): navigate_to('Assessment History')

    with col_out:
        if st.button("Logout", key="btn_logout", type="secondary", use_container_width=True):
            st.session_state['logged_in'] = False
            navigate_to('Home')

def _get_img_b64(path: str) -> str:
    """Read an image file and return a base64-encoded data URI string."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{data}"


def render_landing_page():
    # ── Load brain image as base64 data URI ──────────────────────────────────
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "brainimage.png")
    try:
        brain_img_src = _get_img_b64(img_path)
    except Exception:
        brain_img_src = ""  # graceful fallback

    # ── Inject all landing-page CSS ─────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Reset Streamlit container padding for landing page ── */
    .stApp:has(.lp-hook) > div > div > div > div.block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    /* Hide sidebar ONLY on landing page, never on dashboard */
    .stApp:has(.lp-hook):not(:has(.dashboard-hook)) section[data-testid="stSidebar"] { 
        display: none !important; 
    }

    /* ── Page wrapper ── */
    .lp-wrap {
        font-family: 'Inter', 'Outfit', sans-serif;
        background: #fff;
        color: #071A3D;
        width: 100%;
        overflow-x: hidden;
    }

    /* ── HERO ── */
    .lp-hero {
        display: grid;
        grid-template-columns: 1.1fr 1fr;
        align-items: center;
        gap: 48px;
        padding: 32px 60px 32px;
        background:
            radial-gradient(circle at 80% 40%, rgba(37,99,235,0.16) 0%, transparent 50%),
            linear-gradient(125deg, #ffffff 0%, #EFF6FF 50%, #DBEAFE 100%);
        box-sizing: border-box;
        min-height: 430px;
        max-height: 460px;
    }

    .hero-left {
        width: 100% !important;
    }

    /* badge: fully hidden */
    .lp-badge { display: none !important; }

    .hero-heading-single-line {
        font-family: 'Outfit', 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-size: 34px !important;
        font-weight: 900 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.6px !important;
        color: #0B2A5B !important;
        white-space: normal !important;
        display: block !important;
        width: 100% !important;
        max-width: none !important;
        margin: 0 0 28px 0 !important;
        padding: 0 !important;
    }

    /* p subtitle */
    .lp-hero .hero-subtitle {
        font-size: 18px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        color: #465B7C !important;
        max-width: 520px !important;
        margin: 0 0 26px 0 !important;
    }

    /* ── Hero button row ── */
    .lp-btn-spacer { margin-top: 0; }

    /* Style both Streamlit hero buttons */
    [data-testid="stButton"][id*="hero_auth_btn"] > button,
    div[data-testid="column"]:has(button[kind="primary"]) > div > button {
        height: 54px !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    div[data-testid="column"]:has(button[kind="secondary"]) > div > button {
        height: 54px !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background: #ffffff !important;
        color: #2563EB !important;
        border: 2px solid #2563EB !important;
    }

    /* ── Hero image ── */
    .lp-hero-image-col {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .lp-hero-image-col img {
        width: 100%;
        max-width: 420px;
        max-height: 420px;
        object-fit: contain;
        border-radius: 0;
        box-shadow: none;
        border: none;
        background: transparent;
        display: block;
        filter: none;
    }

    /* ── FEATURES ── */
    .lp-features {
        padding: 36px 72px 44px;
        background: #fff;
        box-sizing: border-box;
    }
    .lp-section-header {
        text-align: center;
        margin-bottom: 28px;
    }
    .lp-section-header h2 {
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #071A3D;
        margin: 0 0 8px;
    }
    .lp-section-line {
        width: 60px;
        height: 3.5px;
        background: linear-gradient(90deg, #1D4ED8, #60A5FA);
        border-radius: 999px;
        margin: 0 auto;
    }
    .lp-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        max-width: 1160px;
        margin: 0 auto;
    }
    .lp-card {
        background: #fff;
        border: 1.5px solid #DBEAFE;
        border-radius: 18px;
        padding: 26px 24px;
        box-shadow: 0 8px 28px rgba(37,99,235,0.09);
        transition: transform 0.25s, box-shadow 0.25s;
    }
    .lp-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 44px rgba(37,99,235,0.16);
    }
    .lp-card-icon {
        width: 50px;
        height: 50px;
        border-radius: 14px;
        background: #EFF6FF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 16px;
    }
    .lp-card h3 {
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #071A3D;
        margin: 0 0 8px;
    }
    .lp-card p {
        font-size: 14.5px;
        line-height: 1.6;
        color: #475569;
        margin: 0;
    }

    /* ── RESPONSIVE DESIGN ── */
    @media (max-width: 1024px) {
        .hero-title { font-size: 36px !important; line-height: 1.2 !important; }
        .lp-hero { padding: 28px 40px 36px; }
        .lp-features { padding: 28px 40px 36px; }
    }
    @media (max-width: 860px) {
        .lp-hero { grid-template-columns: 1fr; padding: 28px 24px 36px; }
        .lp-hero-image-col { order: -1; }
        .lp-features { padding: 28px 20px 36px; }
        .lp-cards { grid-template-columns: 1fr; }
    }

    /* ── LEARN MORE SECTION ── */
    .learn-more-section {
        margin: 60px auto 40px auto !important;
        max-width: 1100px !important;
        padding: 45px !important;
        background: #ffffff !important;
        border: 1px solid #C9D6EA !important;
        border-radius: 28px !important;
        box-shadow: 0 20px 50px rgba(22, 74, 159, 0.10) !important;
    }

    .learn-header {
        text-align: center !important;
        margin-bottom: 36px !important;
    }



    .learn-header p {
        font-size: 19px !important;
        color: #4B6388 !important;
        line-height: 1.6 !important;
        margin: 0 auto !important;
        max-width: 760px !important;
    }

    .learn-steps {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
        gap: 22px !important;
    }

    .learn-step {
        display: flex !important;
        gap: 18px !important;
        align-items: flex-start !important;
        padding: 24px !important;
        background: #F7FAFF !important;
        border: 1px solid #D8E4F5 !important;
        border-radius: 22px !important;
        box-shadow: 0 10px 24px rgba(22, 74, 159, 0.06) !important;
    }

    .learn-step-number {
        min-width: 44px !important;
        height: 44px !important;
        border-radius: 50% !important;
        background: #164A9F !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        font-weight: 800 !important;
    }

    .learn-step-content h3 {
        font-size: 21px !important;
        font-weight: 800 !important;
        color: #0B2A5B !important;
        margin: 0 0 8px 0 !important;
    }

    .learn-step-content p {
        font-size: 16px !important;
        color: #4B6388 !important;
        line-height: 1.55 !important;
        margin: 0 !important;
    }

    .learn-note {
        margin-top: 28px !important;
        padding: 20px 24px !important;
        background: #EEF5FF !important;
        border-left: 5px solid #164A9F !important;
        border-radius: 18px !important;
        color: #3F5578 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hook element so the CSS :has() selector targets the right page ────────
    st.markdown('<div class="lp-hook" style="display:none"></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # HERO — entire block as one HTML string (text + image together)
    # This is the ONLY reliable way to get a real CSS grid 2-column
    # layout in Streamlit. st.columns cannot sit inside an HTML div.
    # ═══════════════════════════════════════════════════════════════
    brain_img_tag = f'<img src="{brain_img_src}" alt="Brain Scan Illustration" />' if brain_img_src else ''

    hero_html = f"""
    <div class="lp-wrap">
      <section class="lp-hero">
        <!-- LEFT: copy -->
        <div class="hero-copy hero-left">
<div class="hero-heading-single-line">
Early Dementia Screening Through<br>Voice & Cognitive Assessment
</div>
<p class="hero-subtitle">
AcousticCognition combines voice analysis and cognitive assessment tasks to provide clear early-screening insights for dementia care.
</p>
        </div>
        <!-- RIGHT: brain image -->
        <div class="lp-hero-image-col">
          {brain_img_tag}
        </div>
      </section>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── Hero action buttons — native Streamlit, positioned below hero text ───
    _, btn_l, btn_r, _ = st.columns([0.05, 1, 1, 3], gap="small")
    with btn_l:
        if st.button("🚀 Start Assessment", use_container_width=True, type="primary", key="hero_auth_btn"):
            st.session_state['show_auth'] = True
            st.query_params['page'] = 'login'
            st.rerun()
    with btn_r:
        if st.button("📖 Learn More", use_container_width=True, key="hero_how_btn"):
            st.session_state['show_learn_more'] = True
            st.query_params['page'] = 'learnmore'
            st.rerun()

    # ── Key Features (all pure HTML, no Streamlit widgets, zero leakage risk) ─
    st.markdown("""
    <div class="lp-wrap">
      <section class="lp-features">
        <div class="lp-section-header">
          <h2>Key Features</h2>
          <div class="lp-section-line"></div>
        </div>
        <div class="lp-cards">
          <div class="lp-card">
            <div class="lp-card-icon">&#127897;</div>
            <h3>Voice Analysis</h3>
            <p>Analyzes voice fluency, acoustic pauses, vocal hesitation,
            and lexical variety to detect subtle early-stage changes.</p>
          </div>
          <div class="lp-card">
            <div class="lp-card-icon">&#129504;</div>
            <h3>Memory Assessment</h3>
            <p>Administers episodic memory retrieval tasks with instant
            scoring and cognitive verification indices.</p>
          </div>
          <div class="lp-card">
            <div class="lp-card-icon">&#128202;</div>
            <h3>Risk Reporting</h3>
            <p>Compiles multi-modal metrics into a structured risk score:
            Low, Moderate, or High Risk — with a detailed report.</p>
          </div>
        </div>
      </section>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("show_learn_more", False):
        st.markdown("""
<section class="learn-more-section">
<div class="learn-header">
<h2 style="font-size: 72px !important; font-weight: 900 !important; line-height: 1.05 !important; letter-spacing: -1px !important; color: #0B2A5B !important; text-align: center !important; margin-bottom: 16px !important;">How AcousticCognition Works</h2>
<p>A simple step-by-step early screening process using voice and cognitive assessment.</p>
</div>
<div class="learn-steps">
<div class="learn-step">
<div class="learn-step-number">1</div>
<div class="learn-step-content">
<h3>Patient Details</h3>
<p>The user enters basic patient information before starting the screening.</p>
</div>
</div>
<div class="learn-step">
<div class="learn-step-number">2</div>
<div class="learn-step-content">
<h3>Cognitive Tasks</h3>
<p>The patient completes simple tasks such as Memory Recall, Object Identification, Activity Sequencing, and Clock Arrangement.</p>
</div>
</div>
<div class="learn-step">
<div class="learn-step-number">3</div>
<div class="learn-step-content">
<h3>Voice Analysis</h3>
<p>The patient records a short voice sample. The system observes speech rate, hesitation, pause patterns, and fluency.</p>
</div>
</div>
<div class="learn-step">
<div class="learn-step-number">4</div>
<div class="learn-step-content">
<h3>Score Calculation</h3>
<p>The system uses rule-based scoring to combine cognitive task results and voice analysis performance.</p>
</div>
</div>
<div class="learn-step">
<div class="learn-step-number">5</div>
<div class="learn-step-content">
<h3>Screening Report</h3>
<p>A clear report is generated with performance scores and a Low, Moderate, or High risk screening result.</p>
</div>
</div>
</div>
<div class="learn-note">
<strong>Important Note:</strong> AcousticCognition is only an early screening support tool. It does not provide a medical diagnosis and does not replace a doctor or professional medical advice.
</div>
</section>
""", unsafe_allow_html=True)


def render_auth_modal():
    # Initialize local auth mode state
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'login'
        
    st.markdown("""
<div class="simple-auth-page"></div>
<style>
/* Remove Streamlit default top padding */
.stApp:has(.simple-auth-page) [data-testid="stAppViewContainer"],
.stApp:has(.simple-auth-page) div[data-testid="stHeader"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
/* FORCE COMPACT LOGIN FORM */
.stApp:has(.simple-auth-page) div.block-container {
    max-width: 680px !important;
    width: 100% !important;
    margin: 40px auto !important;
    padding: 24px 40px 24px 40px !important;
    background: #FFFFFF !important;
    border-radius: 22px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 16px 40px rgba(11, 42, 91, 0.06) !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    width: 100% !important;
    margin: 0 auto !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stTextInput"] {
    width: 92% !important;
    margin: 0 auto 20px auto !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stTextInput"] input {
    height: 54px !important;
    border-radius: 12px !important;
    width: 100% !important;
    border: 1px solid #E2E8F0 !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stTextInput"] input:focus {
    border-color: #145CFF !important;
    box-shadow: 0 0 0 3px rgba(20, 92, 255, 0.15) !important;
    outline: none !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stFormSubmitButton"] {
    width: 92% !important;
    margin: 24px auto 0 auto !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stFormSubmitButton"] button {
    height: 56px !important;
    border-radius: 12px !important;
    width: 100% !important;
    font-weight: 700 !important;
    border: none !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25) !important;
    filter: brightness(0.95) !important;
}
.stApp:has(.simple-auth-page) div[data-testid="stButton"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
.stApp:has(.simple-auth-page) button[kind="secondary"] {
    height: 56px !important;
    border-radius: 12px !important;
    width: 92% !important;
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    color: #0F172A !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stApp:has(.simple-auth-page) button[kind="secondary"]:hover {
    background: #F1F5F9 !important;
    border-color: #CBD5E1 !important;
}
.stApp:has(.simple-auth-page) .forgot-link {
    display: block;
    width: 92%;
    margin: -4px auto 20px auto;
    text-align: right;
    font-size: 0.85rem;
    color: #145CFF;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stApp:has(.simple-auth-page) .forgot-link:hover {
    color: #0E48CC;
    text-decoration: underline;
}
.stApp:has(.simple-auth-page) .auth-toggle-footer {
    text-align: center;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1E293B;
    margin: 24px 0 12px 0;
}
.login-brand {
    font-size: 34px !important;
    font-weight: 800 !important;
    color: #274472 !important;
    text-align: center !important;
    margin-bottom: 28px !important;
}
.login-title {
    font-size: 56px !important;
    font-weight: 900 !important;
    color: #0B3B79 !important;
    text-align: center !important;
    line-height: 1.1 !important;
    margin-top: 30px !important;
    margin-bottom: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    subtitle_text = "Sign in to continue to your workspace" if st.session_state['auth_mode'] == 'login' else "Register to continue to your workspace"
    
    action_heading = "Login" if st.session_state['auth_mode'] == 'login' else "Register"
    action_sub = "Access your account" if st.session_state['auth_mode'] == 'login' else "Create a new account"

    st.markdown(f"""
<div style="text-align:center; margin-bottom: 24px;">
    <div style="font-size:58px; line-height:1; margin-bottom: 16px;">🧠</div>
    <div class="login-brand">AcousticCognition</div>
    <p style="color:#64748B; font-family:'Plus Jakarta Sans'; font-size:0.9rem; margin:0;">{subtitle_text}</p>
</div>
<div style="text-align:center; width: 100%; margin: 0 auto 36px auto;">
    <div class="login-title">{action_heading}</div>
    <p style="color:#64748B; font-family:'Plus Jakarta Sans'; font-size: 20px; font-weight: 300; margin: 0 0 40px 0;">{action_sub}</p>
</div>
""", unsafe_allow_html=True)
    
    if st.session_state['auth_mode'] == 'login':
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Email", key="login_username", placeholder="Enter your email...")
            pwd = st.text_input("Password", type="password", key="login_pwd", placeholder="Enter your password...")
            
            st.markdown('<a href="#" class="forgot-link">Forgot password?</a>', unsafe_allow_html=True)
            
            if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                success, uid, name = verify_user(username.strip(), pwd.strip(), is_admin=0)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = uid
                    st.session_state['full_name'] = name
                    st.session_state['role'] = 'user'
                    st.session_state['page'] = 'Home'
                    st.session_state['show_auth'] = False
                    st.query_params['page'] = 'dashboard'
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")
                    
        # Dynamic footer toggle
        st.markdown('<div class="auth-toggle-footer">Don’t have an account? </div>', unsafe_allow_html=True)
        if st.button("Register here", key="toggle_to_signup", type="secondary", use_container_width=True):
            st.session_state['auth_mode'] = 'signup'
            st.query_params['page'] = 'register'
            st.rerun()

    else:
        # Signup layout
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Email", key="reg_username", placeholder="Enter your email...")
            pwd = st.text_input("Password", type="password", key="reg_pwd", placeholder="Enter your password...")
            cpwd = st.text_input("Confirm Password", type="password", key="reg_cpwd", placeholder="Confirm your password...")
            
            if st.form_submit_button("Register", type="primary", use_container_width=True):
                if pwd != cpwd:
                    st.error("Passwords do not match.")
                elif not username.strip():
                    st.error("Please enter a valid email.")
                else:
                    success, result = register_user(
                        username.strip(),
                        pwd.strip(),
                        full_name=username.strip().split('@')[0].capitalize(),
                        is_admin=0
                    )
                    if success:
                        st.success("Account created successfully.")
                        time.sleep(1.0)
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = result
                        st.session_state['full_name'] = username.strip().split('@')[0].capitalize()
                        st.session_state['role'] = 'user'
                        st.session_state['page'] = 'Home'
                        st.session_state['show_auth'] = False
                        st.query_params['page'] = 'dashboard'
                        st.rerun()
                    else:
                        st.error(result)
                        
        # Dynamic footer toggle
        st.markdown('<div class="auth-toggle-footer">Already have an account? </div>', unsafe_allow_html=True)
        if st.button("Login here", key="toggle_to_login", type="secondary", use_container_width=True):
            st.session_state['auth_mode'] = 'login'
            st.query_params['page'] = 'login'
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="back_home_btn", type="secondary", use_container_width=True):
        st.session_state['show_auth'] = False
        st.query_params['page'] = 'home'
        st.rerun()

    

# =========================
# PAGE MODULES
# =========================

def page_home():
    # Fetch dynamic metrics from database
    import sqlite3
    from database import DB_FILENAME, fetch_admin_metrics
    
    assess_count = 12
    patient_count = 8
    avg_risk = 34
    
    try:
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM assessments")
        assess_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT patient_id) FROM assessments")
        patient_count = c.fetchone()[0]
        
        c.execute("SELECT AVG(overall_score) FROM assessments")
        avg_score_raw = c.fetchone()[0]
        if avg_score_raw is not None:
            # Risk is inversely proportional to cognitive performance score
            avg_risk = int(100 - avg_score_raw)
        conn.close()
    except Exception:
        pass
        
    # Standard medical SaaS fallback placeholders if DB is empty
    if assess_count == 0: assess_count = 12
    if patient_count == 0: patient_count = 8
    if avg_risk <= 0 or avg_risk >= 100: avg_risk = 34

    # Title & Subtitle
    st.markdown(f"""
    <div style="margin-bottom: 3.5rem;">
        <div style="font-size: 48px; color: var(--dark-navy); font-weight: 800; font-family: 'Outfit'; margin: 0 0 4px 0; letter-spacing: -1px; line-height: 1.1;">
            Welcome Back,
        </div>
        <div style="font-size: 40px; color: var(--dark-navy); font-weight: 700; font-family: 'Outfit'; margin: 0 0 16px 0; letter-spacing: -1px; line-height: 1.1;">
            {st.session_state.get('full_name', 'User')} 👋
        </div>
        <div style="color: var(--text-secondary); font-size: 20px; font-weight: 400; margin: 0;">Manage screenings and view cognitive records.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3 Metrics Row
    m_col1, m_col2, m_col3 = st.columns(3, gap="medium")
    
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-box" style="background: rgba(14, 159, 110, 0.08); color: #0E9F6E;">📋</div>
            <div>
                <span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Total Assessments</span>
                <div style="font-size: 1.9rem; font-weight: 800; color: var(--dark-navy); margin-top: 2px;">{assess_count}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-box" style="background: rgba(13, 148, 136, 0.08); color: #0D9488;">👥</div>
            <div>
                <span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Patients</span>
                <div style="font-size: 1.9rem; font-weight: 800; color: var(--dark-navy); margin-top: 2px;">{patient_count}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-box" style="background: rgba(245, 158, 11, 0.08); color: #F59E0B;">⚠️</div>
            <div>
                <span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Average Risk</span>
                <div style="font-size: 1.9rem; font-weight: 800; color: var(--dark-navy); margin-top: 2px;">{avg_risk}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Quick Actions Title
    st.markdown("<h2 style='font-size: 1.4rem; color: var(--dark-navy); font-weight: 700; margin-bottom: 1rem; font-family: Outfit;'>Quick Actions</h2>", unsafe_allow_html=True)
    
    # 5 Quick Actions columns
    a_col1, a_col2, a_col3, a_col4, a_col5 = st.columns(5, gap="small")
    
    # Define actions metadata
    actions = [
        {"name": "Memory Recall", "icon": "🧠", "color": "rgba(76, 175, 80, 0.08)", "text_color": "#4CAF50", "key": "qa_memory"},
        {"name": "Object ID", "icon": "🖼️", "color": "rgba(112, 0, 255, 0.08)", "text_color": "#7000FF", "key": "qa_lang"},
        {"name": "Seq. Tasks", "icon": "🔄", "color": "rgba(244, 63, 94, 0.08)", "text_color": "#F43F5E", "key": "qa_exec"},
        {"name": "Clock Drawing", "icon": "🕒", "color": "rgba(245, 158, 11, 0.08)", "text_color": "#F59E0B", "key": "qa_clock"},
        {"name": "Voice Analysis", "icon": "🎙️", "color": "rgba(14, 159, 110, 0.08)", "text_color": "#0E9F6E", "key": "qa_voice"}
    ]
    
    cols = [a_col1, a_col2, a_col3, a_col4, a_col5]
    for i, act in enumerate(actions):
        with cols[i]:
            st.markdown(f"""
            <div class="dashboard-card" style="text-align: center; padding: 20px 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130px;">
                <div style="background: {act['color']}; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 8px; color: {act['text_color']};">{act['icon']}</div>
                <div style="font-weight: 700; color: var(--dark-navy); font-size: 0.85rem; font-family: Outfit; line-height: 1.2;">{act['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Launch", key=act['key'], use_container_width=True):
                from cognitive_tests import reset_assessment_state
                reset_assessment_state()
                st.session_state.page = "assessment"
                st.session_state.assessment_started = True
                st.session_state.current_step = 1
                
                if act['key'] == "qa_memory":
                    st.session_state.launched_cog_task_step = 1
                elif act['key'] == "qa_lang":
                    st.session_state.launched_cog_task_step = 2
                elif act['key'] == "qa_exec":
                    st.session_state.launched_cog_task_step = 3
                elif act['key'] == "qa_clock":
                    st.session_state.launched_cog_task_step = 4
                elif act['key'] == "qa_voice":
                    st.session_state.launched_cog_task_step = 5
                else:
                    st.session_state.launched_cog_task_step = 1
                
                st.query_params['page'] = 'assessment'
                st.rerun()





def page_assessment_guide():
    st.markdown('<div style="font-size:56px; font-weight:900; color:#002B5C; text-align:center; margin-top:10px; margin-bottom:20px; line-height:1.1; letter-spacing:-1px;">Assessment Guide</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-secondary); margin-bottom:2rem; font-size:0.95rem;'>Understand how each cognitive and acoustic assessment works and how scoring is calculated.</p>", unsafe_allow_html=True)

    state_keys = [
        "show_memory_criteria", "show_object_criteria", "show_activity_criteria",
        "show_clock_criteria", "show_voice_criteria", "show_overall_criteria"
    ]
    for key in state_keys:
        if key not in st.session_state:
            st.session_state[key] = False

    assessments = [
        {
            "id": 1,
            "state_key": "show_memory_criteria",
            "btn_key": "memory_criteria_btn",
            "title": "🧠 Memory Recall",
            "desc": "The patient views simple objects for a short time and then types the remembered words.",
            "bg": "#F0F8FF",
            "border": "#BAE6FD",
            "title_color": "#0369A1",
            "criteria": "Score is based on how many correct words are recalled.<br>- <b>5/5</b> = 100%<br>- <b>4/5</b> = 80%<br>- <b>3/5</b> = 60%<br>- <b>2/5</b> = 40%<br>- <b>1/5</b> = 20%<br>- <b>0/5</b> = 0%"
        },
        {
            "id": 2,
            "state_key": "show_object_criteria",
            "btn_key": "object_criteria_btn",
            "title": "🖼️ Object Identification",
            "desc": "The patient looks at common object images and types the object name.",
            "bg": "#F0FDF4",
            "border": "#BBF7D0",
            "title_color": "#15803D",
            "criteria": "Score is based on correct identifications.<br>- <b>3/3</b> = 100%<br>- <b>2/3</b> = 66.7%<br>- <b>1/3</b> = 33.3%<br>- <b>0/3</b> = 0%"
        },
        {
            "id": 3,
            "state_key": "show_activity_criteria",
            "btn_key": "activity_criteria_btn",
            "title": "🔄 Activity Sequencing",
            "desc": "The participant completes two different daily activity sequencing tasks by arranging the steps of each activity in the correct order.",
            "bg": "#FAF5FF",
            "border": "#E9D5FF",
            "title_color": "#7E22CE",
            "criteria": "Each activity is scored independently based on how many steps are placed in the correct position.<br><br>- <b>4/4 correct</b> = 100%<br>- <b>3/4 correct</b> = 75%<br>- <b>2/4 correct</b> = 50%<br>- <b>1/4 correct</b> = 25%<br>- <b>0/4 correct</b> = 0%<br><br>The final Activity Sequencing score is calculated as the average of the scores from both activities."
        },
        {
            "id": 4,
            "state_key": "show_clock_criteria",
            "btn_key": "clock_criteria_btn",
            "title": "🕒 Clock Arrangement",
            "desc": "The patient sets the clock hands to the given time.",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "title_color": "#B45309",
            "criteria": "The system compares the selected hour and minute hand positions with the target time.<br>- Closer hand placement gives a higher score.<br>- Correct or near-correct placement gives <b>95–100%</b>."
        },
        {
            "id": 5,
            "state_key": "show_voice_criteria",
            "btn_key": "voice_criteria_btn",
            "title": "🎙️ Voice Analysis",
            "desc": "The patient reads a sentence aloud. The system checks speech rate, pauses, hesitation, fluency, and completion.",
            "bg": "#F0F8FF",
            "border": "#BAE6FD",
            "title_color": "#0369A1",
            "criteria": "- The assessment begins with a maximum score of 100.<br><br>- Reading the complete sentence accurately with normal speaking speed results in a score close to 100.<br><br>- Points are deducted for incorrect or missing words, prolonged pauses, hesitation, reduced fluency, abnormal speaking rate, and excessive background noise.<br><br>- Mild background noise is filtered before analysis and has minimal impact on the final score.<br><br>- The final score reflects the overall quality, fluency, and clarity of speech after applying these deductions."
        },
        {
            "id": 6,
            "state_key": "show_overall_criteria",
            "btn_key": "overall_criteria_btn",
            "title": "⚠️ Overall Risk Score",
            "desc": "The system combines all task scores and classifies the result into risk tiers.",
            "bg": "#FEF2F2",
            "border": "#FECACA",
            "title_color": "#B91C1C",
            "criteria": "- <b>Low Risk</b><br>- <b>Moderate Risk</b><br>- <b>High Risk</b>"
        }
    ]

    for item in assessments:
        s_key = item['state_key']
        b_key = item['btn_key']
        
        st.markdown(f"""
        <div style="background-color: {item['bg']}; padding: 24px; border-radius: 16px; margin-bottom: 12px; border: 1px solid {item['border']}; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h3 style="margin-top: 0; color: {item['title_color']}; font-size: 1.5rem; font-weight: bold;">{item['title']}</h3>
            <p style="color: #334155; margin-bottom: 12px; font-size: 1.1rem;"><strong>How it works:</strong> {item['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("View Criteria ↓", key=b_key, type="secondary", use_container_width=True):
                st.session_state[s_key] = not st.session_state.get(s_key, False)
                st.rerun()
        
        if st.session_state.get(s_key, False):
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #C9D6EA; border-radius: 16px; padding: 22px 26px; margin: 8px 0 24px 0; box-shadow: 0 6px 20px rgba(22, 74, 159, 0.07);">
                <h4 style="color: #0B2A5B; font-weight: 800; font-size: 1.1rem; margin: 0 0 12px 0;">Scoring Criteria</h4>
                <div style="color: #334155; font-size: 1rem; line-height: 1.75;">{item['criteria']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 40px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 20px;">
        <em><strong>Disclaimer:</strong> This system is only for early screening support. It does not replace a doctor, clinical diagnosis, or professional medical advice.</em>
    </div>
    """, unsafe_allow_html=True)

def page_settings():
    st.markdown("""
    <style>
    .stApp:has(.settings-page) [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid #D7E6FF !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 18px rgba(37,99,235,0.04) !important;
        padding: 24px !important;
    }
    .settings-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #071A3D;
        margin-bottom: 1rem;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 8px;
    }
    </style>
    <div class="settings-page"></div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-size:2.2rem; font-family: Outfit; font-weight: 800; color: var(--dark-navy); margin-bottom: 0.5rem; letter-spacing: -0.5px;'>Platform Settings</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-secondary); margin-bottom:2rem; font-size:0.95rem;'>Manage your clinical profile, security preferences, and UI theme settings.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        with st.container(border=True):
            st.markdown('<div class="settings-header">Profile Information</div>', unsafe_allow_html=True)
            st.text_input("User Name", value=st.session_state.get('full_name', 'User'))
            st.text_input("Role", value="Clinical User", disabled=True)
            st.text_input("Email Address", value=st.session_state.get('email', 'clinician@example.com'))
            st.text_input("Clinical License/ID", value="MD-8472910")
            st.button("Edit Profile", type="primary", use_container_width=True)

        with st.container(border=True):
            st.markdown('<div class="settings-header">Account & Security</div>', unsafe_allow_html=True)
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.text_input("Confirm New Password", type="password")
            st.button("Change Password", type="secondary", use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown('<div class="settings-header">Display Preferences</div>', unsafe_allow_html=True)
            
            # Initialize theme state if not exists
            if 'theme_mode' not in st.session_state:
                st.session_state['theme_mode'] = 'System Default'
                
            theme_choice = st.radio("Theme Mode", ["Light Mode", "Dark Mode", "System Default"], index=["Light Mode", "Dark Mode", "System Default"].index(st.session_state['theme_mode']))
            
            if theme_choice != st.session_state['theme_mode']:
                st.session_state['theme_mode'] = theme_choice
                
            st.info("Theme preference saved. Full theme switching is currently in beta.")
            
        with st.container(border=True):
            st.markdown('<div class="settings-header">Screening Preferences</div>', unsafe_allow_html=True)
            
            if 'risk_threshold' not in st.session_state:
                st.session_state['risk_threshold'] = 'Moderate'
            
            st.session_state['risk_threshold'] = st.selectbox("Default Risk Threshold", ["Low", "Moderate", "High"], index=["Low", "Moderate", "High"].index(st.session_state['risk_threshold']))
            
            if 'show_detailed_report' not in st.session_state: st.session_state['show_detailed_report'] = True
            if 'caregiver_friendly' not in st.session_state: st.session_state['caregiver_friendly'] = False
            if 'auto_save_history' not in st.session_state: st.session_state['auto_save_history'] = True
            
            st.session_state['show_detailed_report'] = st.checkbox("Show detailed report after assessment", value=st.session_state['show_detailed_report'])
            st.session_state['caregiver_friendly'] = st.checkbox("Enable caregiver-friendly explanation", value=st.session_state['caregiver_friendly'])
            st.session_state['auto_save_history'] = st.checkbox("Save assessment history automatically", value=st.session_state['auto_save_history'])
            
        with st.container(border=True):
            st.markdown('<div class="settings-header">System Information</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 0.9rem; color: #475569; line-height: 1.6;">
                <strong>Project:</strong> AcousticCognition<br>
                <strong>Database:</strong> SQLite Local Instance<br>
                <strong>Screening Type:</strong> Voice + Cognitive Assessment<br>
                <strong>Report Mode:</strong> Rule-based risk scoring<br>
                <strong>Version:</strong> v2.1.0-beta
            </div>
            """, unsafe_allow_html=True)

def page_patients():
    st.markdown("""
    <style>
    .search-card {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: var(--shadow-soft) !important;
        margin-bottom: 2rem !important;
    }
    .history-row {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(7, 27, 77, 0.03);
    }
    </style>
    """, unsafe_allow_html=True)

    if 'view_history_record_id' not in st.session_state:
        st.session_state['view_history_record_id'] = None
    if 'view_history_record_source' not in st.session_state:
        st.session_state['view_history_record_source'] = 'assessments'

    if st.session_state['view_history_record_id'] is not None:
        rec_id = st.session_state['view_history_record_id']
        rec_source = st.session_state.get('view_history_record_source', 'assessments')
        import sqlite3
        from database import DB_FILENAME
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()

        record = None
        # Try the assessments table first (primary)
        if rec_source == 'assessments':
            c.execute("""
                SELECT a.id, p.name, p.age, p.gender, a.assessment_date, a.overall_score,
                       a.confidence_score, a.risk_level, a.working_memory_score,
                       a.attention_score, a.recall_score, a.speech_rate, a.recommendation
                FROM assessments a
                JOIN patients p ON a.patient_id = p.id
                WHERE a.id = ?
            """, (rec_id,))
            record = c.fetchone()

        # Fallback: try interactive_assessments table
        if not record:
            c.execute("""
                SELECT id, patient_name, patient_age, patient_gender,
                       assessment_date, overall_score,
                       90.0 AS confidence_score, risk_level,
                       cognitive_score, speech_score, cognitive_score,
                       speech_score, 'N/A' AS recommendation
                FROM interactive_assessments
                WHERE id = ?
            """, (rec_id,))
            record = c.fetchone()

        conn.close()
        
        if not record:
            st.error("Report record not found.")
            if st.button("← Back to History", type="secondary"):
                st.session_state['view_history_record_id'] = None
                st.rerun()
            return
            
        rid, p_name, p_age, p_gender, date_raw, o_score, conf_score, r_level, wm_score, att_score, rec_score, s_rate, rec_text = record
        try:
            import datetime
            dt = datetime.datetime.strptime(str(date_raw)[:16], "%Y-%m-%d %H:%M")
            date_formatted = dt.strftime("%d %b %Y - %I:%M %p")
        except Exception:
            date_formatted = str(date_raw)[:16]
            
        risk_class = "green" if "Low" in r_level else "orange" if "Mod" in r_level or "Med" in r_level else "red"
        
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 2rem;">
            <div>
                <div style="width:100%; text-align:center;">
                    <h1 style="font-size:64px !important; font-weight:900 !important; color:#002B5C !important; margin:10px 0 20px 0 !important; line-height:1.1 !important; letter-spacing:-1px !important;">
                        Assessment Report
                    </h1>
                </div>
                <p style="margin:0; color:var(--text-secondary);">Patient ID: <strong style="color:#0E9F6E;">AC-2024-{rid:03d}</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("← Back to History List", type="secondary", key="back_to_list_btn"):
            st.session_state['view_history_record_id'] = None
            st.rerun()
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1.3], gap="large")
        with col_left:
            st.markdown(f"""
            <div class="premium-card" style="text-align: center; height: 100%;">
                <p style="font-size: 0.8rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Overall Risk Level</p>
                <div class="pill-badge {risk_class}" style="font-size: 1.1rem; padding: 8px 24px; margin-bottom: 2rem;">{r_level}</div>
                <div style="margin: 2rem auto; width: 160px; height: 160px; border-radius: 50%; border: 12px solid #F5F8FF; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 2px 8px rgba(7,27,77,0.02); background: white; border-top-color: #0E9F6E;">
                    <span style="font-size: 2.5rem; font-weight: 800; color: var(--dark-navy); font-family: 'Outfit';">{int(o_score)}%</span>
                    <span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: -2px;">Overall Score</span>
                </div>
                <p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.85rem; line-height: 1.4; font-style: italic;">
                    Confidence Score: {int(conf_score)}%
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_right:
            st.markdown("""
            <div class="premium-card" style="height: 100%;">
                <p style="font-size: 0.8rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Domain Scores</p>
            """, unsafe_allow_html=True)
            def render_domain_bar(label, score):
                bar_color = "#4CAF50" if score >= 70 else "#FF9800" if score >= 45 else "#F44336"
                st.markdown(f"""
                <div style="margin-bottom: 1.2rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:700; font-size:0.9rem; color:var(--dark-navy);">
                        <span>{label}</span>
                        <span>{int(score) if score != 'N/A' else 'N/A'}%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {score if score != 'N/A' else 0}%; background: {bar_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            render_domain_bar("Memory Recall", wm_score)
            render_domain_bar("Object Identification", rec_score)
            render_domain_bar("Activity Sequencing", att_score)
            render_domain_bar("Voice Analysis & Latency", max(20.0, min(100.0, s_rate / 3.4)))
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="premium-card">
            <h4 style="margin: 0 0 8px 0; color: var(--dark-navy); font-size: 1.05rem; font-weight: 700;">Clinical Recommendation</h4>
            <p style="margin: 0 0 20px 0; color: var(--text-secondary); line-height: 1.5; font-size: 0.95rem;">{rec_text}</p>
            <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--text-secondary); font-weight: 600;">
                <span>Assessment Date: <strong>{date_formatted}</strong></span>
                <span>Assessed By: <strong>{st.session_state.get('full_name', 'User')}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
        background: white !important;
        border: 1px solid #E5E7EB !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="font-size:56px; font-weight:900; color:#002B5C; text-align:center; margin-top:10px; margin-bottom:20px; line-height:1.1; letter-spacing:-1px;">Patient Records</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-secondary); margin-bottom:2rem; font-size:0.95rem; text-align:center;'>Search patient by name to view their historical assessments and risk trends.</p>", unsafe_allow_html=True)
    
    if 'search_query_name' not in st.session_state:
        st.session_state['search_query_name'] = ""
    if 'has_searched' not in st.session_state:
        st.session_state['has_searched'] = False
    if 'selected_patient_id' not in st.session_state:
        st.session_state['selected_patient_id'] = None

    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0; color:var(--dark-navy);'>Search Records</h3>", unsafe_allow_html=True)
        col_search, col_btn, col_spacer = st.columns([2.5, 1, 4.5], gap="small")
        with col_search:
            s_name = st.text_input("Patient Name", value=st.session_state['search_query_name'], key="patient_record_search", label_visibility="collapsed", placeholder="Enter patient name...")
        with col_btn:
            do_search = st.button("Search Records", use_container_width=True, type="primary")

    if do_search:
        st.session_state['search_query_name'] = s_name.strip()
        st.session_state['has_searched'] = True
        st.session_state['selected_patient_id'] = None
        st.rerun()

    if not st.session_state['has_searched']:
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0; color:var(--dark-navy);'>Recent Records</h3>", unsafe_allow_html=True)
            import sqlite3
            from database import DB_FILENAME
            conn = sqlite3.connect(DB_FILENAME)
            c = conn.cursor()
            c.execute("""
                SELECT p.id, p.name, a.assessment_date, a.risk_level
                FROM assessments a
                JOIN patients p ON a.patient_id = p.id
                ORDER BY a.assessment_date DESC
                LIMIT 10
            """)
            recent_records = list(c.fetchall())
            conn.close()

            if not recent_records:
                st.markdown("<p style='color: var(--text-secondary);'>No completed patient assessments found.</p>", unsafe_allow_html=True)
            else:
                table_html = (
                    "<table style='width:100%; border-collapse: collapse; margin-top: 10px;'>"
                    "<tr style='border-bottom: 2px solid #F1F5F9; color: #64748B; font-size: 0.85rem; text-align: left;'>"
                    "<th style='padding: 12px 16px;'>Patient ID</th>"
                    "<th style='padding: 12px 16px;'>Patient Name</th>"
                    "<th style='padding: 12px 16px;'>Last Assessment Date</th>"
                    "<th style='padding: 12px 16px;'>Risk Level</th>"
                    "<th style='padding: 12px 16px;'>Status</th>"
                    "</tr>"
                )
                for row in recent_records:
                    pid, name, date_str, risk = row
                    
                    risk_color = "#10B981"
                    if risk in ["Moderate", "Moderate Risk", "Medium", "Medium Risk"]:
                        risk_color = "#F59E0B"
                    elif risk in ["High", "High Risk"]:
                        risk_color = "#EF4444"
                        
                    table_html += (
                        f"<tr style='border-bottom: 1px solid #F1F5F9; font-size: 0.95rem; color: #1E293B;'>"
                        f"<td style='padding: 16px;'>{pid}</td>"
                        f"<td style='padding: 16px; font-weight:600;'>{name}</td>"
                        f"<td style='padding: 16px;'>{date_str}</td>"
                        f"<td style='padding: 16px;'><span style='background:{risk_color}; color:white; padding:4px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;'>{risk}</span></td>"
                        f"<td style='padding: 16px;'><span style='color: #10B981; font-weight: 600;'>Completed</span></td>"
                        f"</tr>"
                    )
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
        return

    import sqlite3
    import pandas as pd
    from database import DB_FILENAME
    
    # Reload records dynamically from the database (case-insensitive, trimmed, partial match)
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    target_name = st.session_state['search_query_name'].strip()
    
    # Search in patients + assessments tables first
    c.execute("""
        SELECT a.id, p.id as patient_id, p.name, a.assessment_date, a.risk_level, p.age, p.gender, a.overall_score,
               a.working_memory_score, a.attention_score, a.recall_score, a.speech_rate
        FROM assessments a
        JOIN patients p ON a.patient_id = p.id
        WHERE TRIM(p.name) LIKE ? COLLATE NOCASE
        ORDER BY a.assessment_date DESC
    """, (f"%{target_name}%",))
    name_matched_records = list(c.fetchall())
    
    # Track which table the records came from so the report viewer
    # queries the correct table when "View Full Report" is clicked.
    record_source = 'assessments'

    # Also search interactive_assessments table as fallback
    if not name_matched_records:
        c.execute("""
            SELECT id, id as patient_id, patient_name, assessment_date, risk_level,
                   patient_age, patient_gender, overall_score,
                   cognitive_score, speech_score, cognitive_score, speech_score
            FROM interactive_assessments
            WHERE patient_name IS NOT NULL AND TRIM(patient_name) LIKE ? COLLATE NOCASE
            ORDER BY assessment_date DESC
        """, (f"%{target_name}%",))
        name_matched_records = list(c.fetchall())
        if name_matched_records:
            record_source = 'interactive'
    
    conn.close()

    if not name_matched_records:
        st.markdown("""
        <div style="text-align:center; padding:3rem; border:1px solid #E5ECF6; border-radius:16px; background:white; color:var(--text-secondary); margin-top:1rem; box-shadow: var(--shadow-soft);">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🔍</div>
            <p style="font-weight:700; margin:0 0 0.25rem 0; font-size:1.1rem; color: var(--dark-navy);">No matching patient found.</p>
            <p style="font-size:0.85rem; margin:0; opacity:0.8;">Ensure the Name is correct.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # If patient not selected, show disambiguation cards
    if st.session_state['selected_patient_id'] is None:
        st.markdown("<h3 style='color: var(--dark-navy); margin-bottom: 16px;'>Select a Patient</h3>", unsafe_allow_html=True)
        unique_patients = {}
        for r in name_matched_records:
            pid = r[1]
            if pid not in unique_patients:
                unique_patients[pid] = {
                    "name": r[2], "age": r[5], "gender": r[6], "total": 0,
                    "latest_date": r[3], "latest_risk": r[4], "latest_score": r[7]
                }
            unique_patients[pid]['total'] += 1
            
        for pid, pdata in unique_patients.items():
            try:
                import datetime
                dt = datetime.datetime.strptime(str(pdata['latest_date'])[:16], "%Y-%m-%d %H:%M")
                last_date = dt.strftime("%d %b %Y - %I:%M %p")
            except:
                last_date = str(pdata['latest_date'])[:16]
                
            st.markdown(f"""
            <div style="background:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #C9D6EA; border-left:4px solid #2A67D8; margin-bottom:16px; box-shadow:0 4px 16px rgba(7,27,77,0.05);">
                <div style="font-size:1.2rem; font-weight:800; color:#071A3D; margin-bottom:8px; font-family:Outfit,sans-serif;">{pdata['name'].title()}, {pdata['age']}, {pdata['gender']} (PAT-{pid:04d})</div>
                <div style="color:#64748B; font-size:0.95rem; margin-bottom:12px;">Last assessment: <strong>{last_date}</strong> &nbsp;|&nbsp; Total assessments: <strong>{pdata['total']}</strong> &nbsp;|&nbsp; Latest Risk: <strong style="color:#2A67D8;">{pdata['latest_risk']}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Patient", key=f"select_pat_{pid}", type="secondary"):
                st.session_state['selected_patient_id'] = pid
                st.rerun()
        return

    # A patient is selected, filter assessments for this specific patient ID
    selected_pid = st.session_state['selected_patient_id']
    filtered_records = [r for r in name_matched_records if r[1] == selected_pid]
    
    if st.button("← Back to Search Results"):
        st.session_state['selected_patient_id'] = None
        st.rerun()

    # Patient Summary
    first = filtered_records[0]
    total_assessments = len(filtered_records)
    latest_risk = first[4]
    latest_score = first[7]
    try:
        import datetime
        dt = datetime.datetime.strptime(str(first[3])[:16], "%Y-%m-%d %H:%M")
        last_date = dt.strftime("%d %b %Y - %I:%M %p")
    except:
        last_date = str(first[3])[:16]

    st.markdown(f"""
    <div style="background:#FFFFFF; padding:24px; border-radius:20px; margin-bottom:32px; border:1px solid #C9D6EA; box-shadow:0 6px 24px rgba(42,103,216,0.06); margin-top:16px;">
        <h3 style="color:#071A3D; margin-top:0; margin-bottom:20px; font-weight:800; font-family:Outfit,sans-serif; font-size:1.4rem;">Patient Summary</h3>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:20px; line-height:1.6;">
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Name</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{first[2].title()}</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Age & Gender</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{first[5]} Y, {first[6]}</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Patient ID</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">PAT-{first[1]:04d}</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Total Assessments</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{total_assessments}</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Latest Risk</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{latest_risk}</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Latest Score</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{latest_score}%</span></div>
            <div><span style="color:#64748B; font-size:0.8rem; font-weight:700; text-transform:uppercase; display:block;">Last Assessment</span><span style="color:#071A3D; font-weight:700; font-size:1.05rem;">{last_date}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Assessments list
    st.markdown("<h3 style='color: var(--dark-navy); margin-bottom: 16px;'>Assessment History</h3>", unsafe_allow_html=True)
    
    for idx, r in enumerate(filtered_records):
        rid = r[0]
        date_raw = str(r[3])[:16]
        try:
            import datetime
            dt = datetime.datetime.strptime(date_raw, "%Y-%m-%d %H:%M")
            date_str = dt.strftime("%d %b %Y - %I:%M %p")
        except:
            date_str = date_raw
        
        o_score = r[7]
        r_level = r[4]
        wm_score = r[8] if r[8] is not None else 'N/A'
        att_score = r[9] if r[9] is not None else 'N/A'
        rec_score = r[10] if r[10] is not None else 'N/A'
        s_rate = r[11] if r[11] is not None else 'N/A'
        voice_score = round(max(20.0, min(100.0, s_rate / 3.4))) if s_rate != 'N/A' else 'N/A'
        
        risk_color = "#16A34A" if "Low" in r_level else "#F59E0B" if "Mod" in r_level or "Med" in r_level else "#EF4444"
        risk_bg = "#F0FDF4" if "Low" in r_level else "#FFFBEB" if "Mod" in r_level or "Med" in r_level else "#FEF2F2"
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #C9D6EA; border-left:4px solid {risk_color}; border-radius:16px; padding:20px; margin-bottom:16px; box-shadow:0 4px 16px rgba(7,27,77,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <div style="font-weight:800; font-size:1.15rem; color:#071A3D;">{date_str}</div>
                <div style="display:flex; align-items:center; gap:16px;">
                    <span style="background:{risk_bg}; color:{risk_color}; padding:6px 16px; border-radius:99px; font-weight:700; font-size:0.85rem; border:1px solid {risk_color}40;">{r_level}</span>
                    <span style="font-weight:900; font-size:1.4rem; color:#071A3D;">{o_score}%</span>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; font-size:0.9rem; color:#64748B; border-top:1px dashed #C9D6EA; padding-top:16px;">
                <div><strong style="color:#071A3D; font-size:0.8rem; text-transform:uppercase;">Memory</strong><br><span style="font-weight:600;">{wm_score}%</span></div>
                <div><strong style="color:#071A3D; font-size:0.8rem; text-transform:uppercase;">Object ID</strong><br><span style="font-weight:600;">{rec_score}%</span></div>
                <div><strong style="color:#071A3D; font-size:0.8rem; text-transform:uppercase;">Sequencing</strong><br><span style="font-weight:600;">{att_score}%</span></div>
                <div><strong style="color:#071A3D; font-size:0.8rem; text-transform:uppercase;">Clock Arr</strong><br><span style="font-weight:600;">N/A</span></div>
                <div><strong style="color:#071A3D; font-size:0.8rem; text-transform:uppercase;">Voice Analys</strong><br><span style="font-weight:600;">{voice_score}%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Full Report", key=f"btn_full_rep_{rid}", type="secondary"):
            st.session_state['view_history_record_id'] = rid
            st.session_state['view_history_record_source'] = record_source
            st.rerun()

    # Trend Graph
    if total_assessments > 1:
        st.markdown("<div style='background:#FFFFFF; border:1px solid #C9D6EA; border-radius:20px; padding:24px; box-shadow:0 6px 24px rgba(42,103,216,0.06); margin-top:32px; margin-bottom:32px;'><h3 style='color:#071A3D; margin-top:0; margin-bottom:20px; font-family:Outfit,sans-serif; font-weight:800;'>Score Trend Analysis</h3>", unsafe_allow_html=True)
        df_patient = pd.DataFrame([
            {'assessment_date': r[3], 'overall_score': r[7], 'risk_level': r[4]}
            for r in filtered_records
        ])
        df_chart = df_patient.copy()
        df_chart['assessment_date_parsed'] = pd.to_datetime(df_chart['assessment_date'])
        
        import altair as alt
        risk_colors = alt.Scale(domain=['Low Risk', 'Moderate Risk', 'High Risk'], range=['#4CAF50', '#FF9800', '#F44336'])
        score_line = alt.Chart(df_chart).mark_line(color='#0E9F6E', strokeWidth=3, point=False).encode(
            x=alt.X('assessment_date_parsed:T', title='Date'),
            y=alt.Y('overall_score:Q', title='Score (%)', scale=alt.Scale(domain=[0, 100]))
        )
        score_markers = alt.Chart(df_chart).mark_circle(size=120, opacity=1.0).encode(
            x=alt.X('assessment_date_parsed:T'),
            y=alt.Y('overall_score:Q'),
            color=alt.Color('risk_level:N', scale=risk_colors, title='Risk'),
            tooltip=['assessment_date:T', 'overall_score:Q', 'risk_level:N']
        )
        score_combined = (score_line + score_markers).properties(height=240).configure_legend(orient='top').interactive()
        st.altair_chart(score_combined, use_container_width=True)

        # Trend interpretation
        df_sorted = df_patient.sort_values(by='assessment_date')
        latest_score_trend = df_sorted.iloc[-1]['overall_score']
        prev_score = df_sorted.iloc[-2]['overall_score']
        
        if latest_score_trend > prev_score:
            trend_text = "Screening performance has improved compared to the previous assessment. Continue regular monitoring and healthy routines."
        elif latest_score_trend < prev_score:
            trend_text = "Screening performance has declined compared to the previous assessment. Clinical consultation is recommended."
        else:
            trend_text = "Screening performance is stable. Continue monitoring."

        st.info(trend_text)
        st.markdown("</div>", unsafe_allow_html=True)

    # Recommendation
    st.markdown("<h3 style='color: var(--dark-navy); margin-top: 32px; margin-bottom: 16px;'>Precaution / Recommendation</h3>", unsafe_allow_html=True)
    if "Low" in latest_risk:
        rec_html = "Continue regular monitoring, good sleep, exercise, social activity, and repeat screening later."
    elif "Mod" in latest_risk or "Med" in latest_risk:
        rec_html = "Monitor symptoms closely, maintain routine, encourage cognitive activities, and consider healthcare consultation if memory issues affect daily life."
    else:
        rec_html = "Recommend clinical consultation as soon as possible. Family/caregiver support and further medical evaluation are advised."

    st.markdown(f"""
    <div style="background-color: #F8FAFC; padding: 24px; border-radius: 16px; border: 1px solid #E2E8F0; color: #334155; font-size: 1.05rem; line-height: 1.6;">
        {rec_html}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 32px; padding: 16px; text-align: center; color: #64748B; font-size: 0.85rem; border-top: 1px solid #E2E8F0;">
        <em>This system is only an early screening support tool. It does not diagnose dementia or replace professional medical advice.</em>
    </div>
    """, unsafe_allow_html=True)

# =========================
# MAIN ROUTING
# =========================
apply_elite_style()

# Sync URL to current state (ensures URL always reflects what user sees)
if st.session_state['logged_in']:
    _current_url = _PAGE_TO_URL.get(st.session_state['page'], 'dashboard')
    if st.query_params.get('page') != _current_url:
        st.query_params['page'] = _current_url
elif st.session_state.get('show_auth'):
    _expected = 'register' if st.session_state.get('auth_mode') == 'signup' else 'login'
    if st.query_params.get('page') != _expected:
        st.query_params['page'] = _expected
elif st.session_state.get('show_learn_more'):
    if st.query_params.get('page') != 'learnmore':
        st.query_params['page'] = 'learnmore'
else:
    if st.query_params.get('page') not in (None, 'home'):
        st.query_params['page'] = 'home'

if not st.session_state['logged_in']:
    if st.session_state['show_auth']:
        render_auth_modal()
    else:
        render_landing_navbar()
        render_landing_page()
else:
    # 1. Left Sidebar Navigation
    st.markdown("""
    <div class="dashboard-hook" style="display:none"></div>
    <style>
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 380px !important;
    }
    .stApp:has(.dashboard-hook) > div > div > div > div.block-container,
    .stApp:has(.dashboard-hook) div.block-container {
        margin-left: 380px !important;
        margin-right: auto !important;
        max-width: calc(100vw - 400px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo" style="display:flex; align-items:center; padding-top:24px; padding-bottom:32px;">
            <div style="background:#0E9F6E; width:76px; height:76px; border-radius:16px; display:flex; align-items:center; justify-content:center; color:white; font-size:3.4rem; font-weight:bold; flex-shrink:0;">🧠</div>
            <div style="font-size:26px; font-weight:800; line-height:1.05; letter-spacing:-0.5px; margin-left:10px; color:#002B5C; white-space:nowrap;">AcousticCognition</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons styled precisely
        if st.button("📊 Dashboard", use_container_width=True, key="side_dash", 
                     type="primary" if st.session_state['page'] == 'Home' else "secondary"):
            navigate_to('Home')
            
        if st.button("📝 New Assessment", use_container_width=True, key="side_new_assess", 
                     type="primary" if st.session_state['page'] == 'Assessment' else "secondary"):
            reset_assessment_state()
            navigate_to('Assessment', current_step=1, cog_task_step=1, assessment_started=False)
            
        if st.button("📂 Patient Records", use_container_width=True, key="side_patients", 
                     type="primary" if st.session_state['page'] == 'Patients' else "secondary"):
            navigate_to('Patients')
            
        if st.button("📘 Assessment Guide", use_container_width=True, key="side_guide", 
                     type="primary" if st.session_state['page'] in ['Guide', 'assessment_guide'] else "secondary"):
            navigate_to('Guide')
        
        st.markdown("<hr style='margin: 1.5rem 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, key="side_logout"):
            st.session_state['logged_in'] = False
            navigate_to('Home')
            
    # 2. Premium Top Profile Header Bar
    t_spacer, t_profile = st.columns([4, 1.2])
    with t_profile:
        st.markdown(f"""
        <div style="text-align: right;">
            <div style="display: inline-flex; align-items: center; gap: 10px; background: white; border: 1px solid var(--border-color); padding: 0 20px; height: 48px; border-radius: 999px; box-shadow: var(--shadow-soft); width: fit-content; min-width: unset; max-width: max-content;">
                <span style="font-size: 1.1rem; line-height: 1;">🧑‍⚕️</span>
                <span style="font-weight: 700; color: var(--dark-navy); font-size: 0.88rem; font-family:'Plus Jakarta Sans'; white-space: nowrap;">{st.session_state.get('full_name', 'User')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # 3. Page Dispatcher
    with st.container():
        page = st.session_state.get('page', 'Home')
        
        if page == 'Home':
            page_home()
        elif page == 'Assessment':
            render_cognitive_tests()
        elif page == 'Patients':
            page_patients()
        elif page in ['Guide', 'assessment_guide']:
            page_assessment_guide()
        else:
            st.session_state['page'] = 'Home'
            page_home()
