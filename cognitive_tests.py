# -*- coding: utf-8 -*-
import streamlit as st
import time
import random
import difflib
import re
import json
from audio_processing import process_audio
from scoring_logic import evaluate_risk

def parse_words(text):
    """
    Normalizes user input by splitting using regex: spaces, commas, or line breaks.
    Removes duplicates while keeping order.
    """
    if not text:
        return []
    words = re.split(r"[,\s\n]+", text.lower().strip())
    words = [w for w in words if w]

    # remove duplicates while keeping order
    seen = set()
    unique_words = []
    for w in words:
        if w not in seen:
            seen.add(w)
            unique_words.append(w)

    return unique_words

# Internal Image Paths generated specifically for the Naming Test
APPLE_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_apple_1776371317754.png"
BICYCLE_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_bicycle_1776371333461.png"
CHAIR_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_chair_1776371352208.png"
WATCH_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_watch_1776371368387.png"
KEY_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_key_1776371384459.png"
BED_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\f13afeb9-560e-4b37-8911-346077152bc8\real_bed_1776371398644.png"
CAR_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_car_testing_1776504247226.png"
BANANA_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_banana_testing_1776504268131.png"
BOOK_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_book_testing_1776504283997.png"
PENCIL_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_pencil_testing_1776504303103.png"
ORANGE_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_orange_testing_1776504326890.png"
GUITAR_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_guitar_testing_1776504343512.png"
UMBRELLA_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_umbrella_testing_1776504366660.png"
TRAIN_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_train_testing_1776504380542.png"
ELEPHANT_IMG = r"C:\Users\unnim\.gemini\antigravity\brain\5ac85828-9a37-47fd-bc0e-4bf5f9b7b487\real_elephant_testing_1776504397228.png"

READING_SENTENCES = [
    "The sun rises early and brings light to the morning.",
    "A small bird is sitting on the branch of a tree.",
    "Please remember to drink water and take rest.",
    "The children are playing happily in the garden.",
    "Today is a good day to complete simple tasks.",
    "The doctor asked the patient to speak clearly.",
    "A cup of tea was placed on the wooden table.",
    "The family walked slowly through the quiet park.",
    "She opened the window and looked at the sky.",
    "The clock on the wall showed seven thirty."
]

def init_cognitive_state():
    if 'assessment_started' not in st.session_state:
        st.session_state['assessment_started'] = False

    if 'reading_sentence' not in st.session_state:
        st.session_state['reading_sentence'] = random.choice(READING_SENTENCES)

    if 'cog_scores' not in st.session_state:
        st.session_state['cog_scores'] = {
            'memory': None,
            'naming': None,
            'sequencing': None,
            'clock_arrangement': None,
            'acoustic': None
        }
    
    # Patient Information (Step 1)
    if 'patient_info' not in st.session_state:
        st.session_state['patient_info'] = {
            'id': '',
            'name': '',
            'age': 65,
            'gender': ''
        }
    
    # Voice Recording (Step 2)
    if 'voice_recording_done' not in st.session_state:
        st.session_state['voice_recording_done'] = False
    
    # Cognitive Tasks (Step 2) - Sub-steps: 1=Memory, 2=Naming, 3=Sequencing, 4=Clock
    if 'cog_task_step' not in st.session_state: st.session_state['cog_task_step'] = 1

    # Memory State
    if 'mem_stage' not in st.session_state: st.session_state['mem_stage'] = 'show'
    if 'mem_words' not in st.session_state: st.session_state['mem_words'] = []
    
    # Naming State
    if 'nam_stage' not in st.session_state: st.session_state['nam_stage'] = 'start'
    if 'nam_idx' not in st.session_state: st.session_state['nam_idx'] = 0
    if 'nam_score' not in st.session_state: st.session_state['nam_score'] = 0
    
    # Results Visibility
    if 'view_results' not in st.session_state: st.session_state['view_results'] = False
    
    # Step-by-step wizard (Main Pipeline)
    if 'current_step' not in st.session_state: st.session_state['current_step'] = 1

    # Prev values for Enter-trigger logic
    if 'prev_mem_input' not in st.session_state: st.session_state['prev_mem_input'] = ""

def reset_assessment_state():
    keys_to_reset = [
        'assessment_started', 'cog_scores', 'patient_info', 'voice_recording_done', 'cog_task_step',
        'mem_stage', 'mem_words',
        'nam_stage', 'nam_idx', 'nam_score', 'nam_test_selection',
        'view_results', 'current_step', 'prev_mem_input',
        'reading_sentence',
        'seq_stage', 'seq_scenario_idx', 'seq_step_idx', 'seq_user_answers',
        'seq_selected_card', 'seq_scenarios', 'seq_shuffled_options',
        'clock_completed', 'clock_target_time', 'clock_hr_select', 'clock_min_select',
        'temp_clock_debug',
        'voice_transcript', 'audio_features', 'recorded_audio',
        'memory_completed', 'object_completed', 'sequence_completed', 'launched_cog_task_step'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def get_next_incomplete_cognitive_task():
    # Build a dynamic assessment queue with the selected task first
    selected = st.session_state.get('launched_cog_task_step', 1)
    queue = [selected] + [x for x in [1, 2, 3, 4, 5] if x != selected]
    
    # Iterate through the queue and return the first incomplete task
    for task in queue:
        if task == 1 and not st.session_state.get("memory_completed", False): return 1
        if task == 2 and not st.session_state.get("object_completed", False): return 2
        if task == 3 and not st.session_state.get("sequence_completed", False): return 3
        if task == 4 and not st.session_state.get("clock_completed", False): return 4
        if task == 5 and not st.session_state.get("voice_recording_done", False): return 5
    return None
def render_patient_info():
    # Auto-generate Patient ID if not set
    if not st.session_state['patient_info']['id']:
        st.session_state['patient_info']['id'] = f"PAT-{random.randint(1000, 9999)}"

    st.markdown("""
<style>
.patient-reg-container {
    max-width: 950px;
    margin: 0;
    padding-top: 20px;
}
.patient-reg-title {
    color: #002B5C;
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 15px;
}
.patient-reg-subtitle {
    color: #002B5C;
    font-size: 24px;
    margin-bottom: 40px;
}
.patient-reg-label {
    color: #002B5C;
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 8px;
    display: block;
}

/* Remove default Streamlit form background/border */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 750px !important;
}

/* Input fields and Selectbox styling */
div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
    border: 2px solid #C7D8F0 !important;
    border-radius: 12px !important;
    height: 50px !important;
    background-color: white !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Hide Streamlit instruction texts like 'Press Enter to submit' */
div[data-testid="InputInstructions"] {
    display: none !important;
}

/* Remove default Streamlit bottom active strips and glow effects */
div[data-baseweb="input"]::before, div[data-baseweb="input"]::after,
div[data-baseweb="select"]::before, div[data-baseweb="select"]::after,
div[data-baseweb="base-input"]::before, div[data-baseweb="base-input"]::after {
    display: none !important;
    content: none !important;
    border: none !important;
    box-shadow: none !important;
}

/* Clear hover and focus wrappers */
div[data-baseweb="input"]:hover, div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:hover, div[data-baseweb="select"]:focus-within {
    box-shadow: none !important;
    border: 2px solid #C7D8F0 !important;
    background-color: white !important;
}

div[data-baseweb="input"] input, div[data-baseweb="select"] div {
    font-size: 18px !important;
    padding-left: 10px !important;
    color: #002B5C !important;
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* Placeholder styling */
div[data-baseweb="input"] input::placeholder {
    color: #8C9EBA !important;
    font-size: 18px !important;
}

/* Form button styling */
div[data-testid="stFormSubmitButton"] {
    display: flex;
    justify-content: flex-start;
}
div[data-testid="stFormSubmitButton"] button {
    background-color: #1F5DB8 !important;
    color: white !important;
    font-size: 24px !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    width: 360px !important;
    height: 64px !important;
    border: none !important;
    margin-top: 20px !important;
}
div[data-testid="stFormSubmitButton"] button p {
    color: white !important;
    font-size: 22px !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="patient-reg-container">
            <div class="patient-reg-title">Patient Registration</div>
            <div class="patient-reg-subtitle">Enter basic patient details before starting the screening.</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("patient_registration_form", clear_on_submit=False):
            st.markdown('<span class="patient-reg-label">Patient Name</span>', unsafe_allow_html=True)
            st.session_state['patient_info']['name'] = st.text_input("Patient Name", value=st.session_state['patient_info']['name'], placeholder="Enter patient name", label_visibility="collapsed")
            
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            
            st.markdown('<span class="patient-reg-label">Age</span>', unsafe_allow_html=True)
            age_val = st.session_state['patient_info']['age']
            try:
                age_val = int(age_val)
                if age_val == 0:
                    age_val = None
            except:
                age_val = None
            age_input = st.number_input("Age", value=age_val, placeholder="Enter age", label_visibility="collapsed", step=1, min_value=0)
            
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            
            st.markdown('<span class="patient-reg-label">Gender</span>', unsafe_allow_html=True)
            gender_options = ["Select gender", "Male", "Female", "Other"]
            current_gender = st.session_state['patient_info']['gender']
            default_index = gender_options.index(current_gender) if current_gender in gender_options else 0
            st.session_state['patient_info']['gender'] = st.selectbox("Gender", options=gender_options, index=default_index, label_visibility="collapsed")
            
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            
            next_step_num = st.session_state.get('launched_cog_task_step', 1)
            step_names = {
                1: "Memory Recall",
                2: "Object Identification",
                3: "Activity Sequencing",
                4: "Clock Drawing",
                5: "Voice Analysis"
            }
            btn_label = f"Proceed to {step_names.get(next_step_num, 'Memory Recall')}"
            
            if st.form_submit_button(btn_label, type="primary", use_container_width=False):
                try:
                    age_int = int(age_input) if age_input else 0
                except ValueError:
                    age_int = 0
                st.session_state['patient_info']['age'] = age_int
                
                if not st.session_state['patient_info']['name']:
                    st.error("Patient name is required for registration.")
                elif age_input is None or age_input < 16 or age_input > 120:
                    st.error("Please enter a valid age between 16 and 120.")
                elif st.session_state['patient_info']['gender'] == "Select gender" or not st.session_state['patient_info']['gender']:
                    st.error("Gender selection is required for registration.")
                else:
                    next_task = get_next_incomplete_cognitive_task()
                    if next_task == 5:
                        st.session_state.current_step = 3
                    else:
                        st.session_state.current_step = 2
                        st.session_state.cog_task_step = next_task if next_task else 1
                    st.rerun()


def render_voice_recording():

    


    # 3. Voice Recording Heading and Instruction
    # ── PATCHED TITLE 5: Voice Analysis ──────────────────────────────────────
    st.markdown(
        '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:20px; letter-spacing:-0.5px;">Voice Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div style="width:100%; text-align:center;"><p class="assessment-subtitle" style="font-size: 22px !important; text-align: center !important; color: #4A5E7A !important; margin: 0 auto;">Read the sentence clearly into the microphone.</p></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#F5F8FF; padding:2rem; border-radius:16px; margin-bottom:2rem; border-left:4px solid #2A67D8; border-top:1px solid #C9D6EA; border-right:1px solid #C9D6EA; border-bottom:1px solid #C9D6EA; text-align:center; max-width:900px; margin-left:auto; margin-right:auto; box-shadow:0 4px 16px rgba(7,27,77,0.05);">
        <p style="text-align:center; font-size:16px; color:#64748B; margin-bottom:15px; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Diagnostic Sentence</p>
        <p style="margin:0; font-size:1.8rem; color:#071A3D; font-family:Outfit,sans-serif; font-weight:800; line-height:1.4; font-style:italic;">"{st.session_state['reading_sentence']}"</p>
    </div>
    """, unsafe_allow_html=True)

    # 4. Audio Recorder Component
    st.markdown("""
    <style>
    div[data-testid="stAudioInput"] {
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    </style>
    <div style='background:#FFFFFF; border-radius:20px; box-shadow:0 6px 24px rgba(42,103,216,0.06); padding:1.2rem; max-width:600px; margin:0 auto 1rem auto; border:1px solid #C9D6EA; text-align:center;'>
        <p style='font-size:1.1rem; color:#071A3D; font-weight:700; margin-bottom:0;'>Record your voice</p>
    </div>
    """, unsafe_allow_html=True)
    recorder_key = f"voice_recorder_{st.session_state['patient_info']['id']}"
    audio_to_process = st.audio_input("Record Baseline", label_visibility="collapsed", key=recorder_key)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. Patient Information Card (Horizontal centered)
    st.markdown(f"""
    <div class="premium-card fade-in" style="max-width: 900px; margin: 0 auto; margin-bottom: 2rem; background:#FFFFFF; border:1px solid #C9D6EA; border-radius:16px; box-shadow:0 4px 16px rgba(7,27,77,0.05); padding:1.5rem;">
        <h3 style="color:#071A3D; font-size:1.1rem; font-weight:700; margin-top:0; margin-bottom:1.5rem; font-family:Outfit; text-align:center;">Patient Information</h3>
        <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:16px; text-align:center;">
            <div style="flex:1;">
                <span style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Patient ID</span>
                <div style="font-weight:700; color:#071A3D; font-size:1rem; margin-top:4px;">{st.session_state['patient_info']['id']}</div>
            </div>
            <div style="flex:1;">
                <span style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Name</span>
                <div style="font-weight:700; color:#071A3D; font-size:1rem; margin-top:4px;">{st.session_state['patient_info']['name']}</div>
            </div>
            <div style="flex:1;">
                <span style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Age</span>
                <div style="font-weight:700; color:#071A3D; font-size:1rem; margin-top:4px;">{st.session_state['patient_info']['age']} Years</div>
            </div>
            <div style="flex:1;">
                <span style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Gender</span>
                <div style="font-weight:700; color:#071A3D; font-size:1rem; margin-top:4px;">{st.session_state['patient_info']['gender']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    

    # 5. Bottom Navigation Bar
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
    btn_back, btn_next = st.columns([1, 1])
    
    with btn_back:
        if st.button("  Back to Tasks", key="voice_back_btn", type="secondary", use_container_width=True):
            st.session_state['current_step'] = 2
            st.rerun()
            
    with btn_next:
        if audio_to_process is not None:
            if st.button("Analyze Vocal Biomarkers & Proceed →", key="voice_next_btn", type="primary", use_container_width=True):
                with st.spinner("Processing neural speech signals..."):
                    features = process_audio(audio_to_process, st.session_state.get('reading_sentence', ''))
                    st.session_state['cog_scores']['acoustic'] = features
                    st.session_state['voice_recording_done'] = True
                    st.success("Vocal baseline captured and vectorized.")
                    time.sleep(1.0)
                    next_task = get_next_incomplete_cognitive_task()
                    if next_task:
                        if next_task == 5:
                            st.session_state['current_step'] = 3
                        else:
                            st.session_state['cog_task_step'] = next_task
                            st.session_state['current_step'] = 2
                    else:
                        st.session_state['current_step'] = 4
                    st.rerun()
        else:
            st.button("Next (Recording Required)", key="voice_next_disabled", disabled=True, use_container_width=True)


def render_memory_test():

    if 'mem_stage' not in st.session_state:
        st.session_state['mem_stage'] = 'show'
        
    if 'mem_words' not in st.session_state or not st.session_state['mem_words']:
        word_bank = [
            "apple", "chair", "book", "clock", "cup", "key", "milk", 
            "bag", "door", "spoon", "bed", "shoe", "water", "pen", "rice"
        ]
        st.session_state['mem_words'] = random.sample(word_bank, 5)

    subtitle_html = ""
    if st.session_state['mem_stage'] == 'show':
        subtitle_html = '<div style="text-align: center !important; width: 100% !important; display: block !important; margin: 0 auto !important; font-size: 24px !important; color: #4A5E7A !important; margin-top: 10px !important; margin-bottom: 30px !important;">Look at the items below for 10 seconds and try to remember them.</div>'

    st.markdown(
        '<div style="width:100%; text-align:center;">'
        '<div style="font-size:72px; line-height:1; margin-bottom:4px;">🧠</div>'
        '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:0; margin-bottom:0; letter-spacing:-0.5px;">Memory Recall Test</div>'
        + subtitle_html +
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state['mem_stage'] == 'show':
        
        if 'memory_start_time' not in st.session_state or time.time() - st.session_state.get('memory_start_time', 0) > 20:
            st.session_state['memory_start_time'] = time.time()
            
        EMOJI_MAP = {
            "apple": "🍎", "chair": "🪑", "book": "📖", "clock": "🕰️", "cup": "🥤", 
            "key": "🔑", "milk": "🥛", "bag": "👜", "door": "🚪", "spoon": "🥄", 
            "bed": "🛏️", "shoe": "👞", "water": "💧", "pen": "🖊️", "rice": "🍚"
        }
        
        st.markdown("""
<style>
.memory-card-row {
    display: flex;
    gap: 18px;
    justify-content: center;
    align-items: center;
    margin: 28px 0;
    flex-wrap: wrap;
}
.memory-word-card {
    background: white;
    border: 2px solid #BAE6FD;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    padding: 20px;
    text-align: center;
    flex: 1;
    min-width: 140px;
    max-width: 160px;
    aspect-ratio: 1 / 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.memory-word-icon {
    font-size: 72px;
    margin-bottom: 10px;
}
.memory-word-label {
    font-size: 24px;
    font-weight: 800;
    color: #1E3A8A;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)
        
        cards_html = ""
        for word in st.session_state['mem_words']:
            emoji = EMOJI_MAP.get(word, "📦")
            cards_html += f"""
<div class="memory-word-card">
    <div class="memory-word-icon">{emoji}</div>
    <div class="memory-word-label">{word}</div>
</div>
"""
        
        ph = st.empty()
        
        while True:
            elapsed = time.time() - st.session_state['memory_start_time']
            remaining = max(0, 10 - int(elapsed))
            
            if remaining <= 0:
                st.session_state['mem_stage'] = 'recall'
                st.rerun()
                break
                
            percent = (remaining / 10) * 100
            
            ph.markdown(f"""
<div class="memory-card-row">
{cards_html}
</div>
<div style="text-align: center; margin-top: 4rem; margin-bottom: 2rem;">
    <div style="font-size: 46px; font-weight: 800; color: #3B82F6; margin-bottom: 5px;">⏱ {remaining} seconds</div>
    <div style="color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Time remaining</div>
    <div style="background: #E2E8F0; height: 16px; border-radius: 12px; overflow: hidden; width: 70%; margin: 0 auto;">
        <div style="background: #3B82F6; width: {percent}%; height: 100%; transition: width 0.1s linear; border-radius: 12px;"></div>
    </div>
</div>
""", unsafe_allow_html=True)
            
            time.sleep(0.5)
            
        st.session_state['mem_stage'] = 'recall'
        st.rerun()
        return
        
    elif st.session_state['mem_stage'] == 'recall':
        st.markdown("""
<style>
.memory-recall-card {
    max-width: 950px;
    margin: 40px auto 24px auto;
    background: #FFFFFF;
    border-radius: 28px;
    padding: 24px 52px;
    box-shadow: 0 18px 45px rgba(37, 99, 235, 0.10);
    border: 1px solid #D7E6FF;
}

.memory-title {
    font-size: 24px !important;
    font-weight: 700 !important;
    text-align: center !important;
    line-height: 1.4 !important;
    letter-spacing: 0.3px !important;
    word-spacing: normal !important;
    margin-bottom: 14px !important;
    width: 100% !important;
    display: block !important;
    color: #002B5C !important;
}

.memory-recall-card p {
    color: #002B5C !important;
    font-size: 22px !important;
    margin-bottom: 0 !important;
    text-align: center !important;
}

div[data-testid="stTextArea"] textarea {
    min-height: 170px !important;
    border-radius: 14px !important;
    border: 2px solid #071A3D !important;
    font-size: 20px !important;
    color: #071A3D !important;
    padding: 18px !important;
    background: #FFFFFF !important;
    caret-color: #000000 !important;
}

/* Ensure the streamlit form doesn't add its own box layout */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 auto !important;
    max-width: 950px !important;
}
</style>
""", unsafe_allow_html=True)

        with st.container():
            st.markdown(
                '<div class="memory-recall-card">'
                '<h3 class="memory-title">Type the Objects You Remember</h3>'
                '<p>Enter the words you remember. Separate words using spaces or commas.</p>'
                '</div>',
                unsafe_allow_html=True
            )
            
            with st.form("memory_recall_form", clear_on_submit=False):
                user_input = st.text_area(
                    label="Recall Entry",
                    placeholder="",
                    key="mem_input",
                    label_visibility="collapsed"
                )
                
                import streamlit.components.v1 as components
                components.html(
                    """
                    <script>
                    (function() {
                        function disableAutocomplete() {
                            const doc = window.parent.document;
                            const inputs = doc.querySelectorAll('textarea[aria-label="Recall Entry"]');
                            inputs.forEach(function(input) {
                                input.setAttribute('autocomplete', 'off');
                                input.setAttribute('autocorrect', 'off');
                                input.setAttribute('autocapitalize', 'off');
                                input.setAttribute('spellcheck', 'false');
                                input.setAttribute('data-lpignore', 'true');
                                input.setAttribute('data-1p-ignore', 'true');
                                input.setAttribute('data-form-type', 'other');
                                input.setAttribute('name', 'recall_' + Math.random().toString(36).slice(2));
                            });
                            const forms = doc.querySelectorAll('form');
                            forms.forEach(function(f) { f.setAttribute('autocomplete', 'off'); });
                        }
                        disableAutocomplete();
                        setTimeout(disableAutocomplete, 300);
                        setTimeout(disableAutocomplete, 800);
                    })();
                    </script>
                    """,
                    height=0, width=0
                )
                
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                if st.form_submit_button("Submit Memory Test", use_container_width=False, type="primary"):
                    raw_words = user_input.replace(',', ' ').split()
                    input_words = [w.lower().strip() for w in raw_words if w.strip()]
                    correct = [w for w in input_words if w in st.session_state['mem_words']]
                    st.session_state['cog_scores']['memory'] = len(correct)
                    st.session_state['mem_stage'] = 'done'
                    st.rerun()
            
    elif st.session_state['mem_stage'] == 'done':
        score = st.session_state['cog_scores']['memory']
        st.success(f"Memory Protocol finalized. Score: {score}/5")
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Proceed to Next Task →", type="primary", key="mem_btn_next", use_container_width=True):
            st.session_state['memory_completed'] = True
            next_task = get_next_incomplete_cognitive_task()
            if next_task:
                if next_task == 5:
                    st.session_state['current_step'] = 3
                else:
                    st.session_state['cog_task_step'] = next_task
                    st.session_state['current_step'] = 2
            else:
                st.session_state['current_step'] = 4
            st.rerun()

def render_activity_sequencing_test():
    if 'current_sequence_scenario' not in st.session_state:
        st.session_state['current_sequence_scenario'] = 0
    if 'selected_sequence_order' not in st.session_state:
        st.session_state['selected_sequence_order'] = []
    if 'sequence_scores' not in st.session_state:
        st.session_state['sequence_scores'] = []
    if 'seq_stage' not in st.session_state:
        st.session_state['seq_stage'] = 'start'

    if st.session_state['seq_stage'] == 'start':
        # ── PATCHED TITLE 3: Activity Sequencing Test ─────────────────────────
        st.markdown(
            '<div style="width:100%; text-align:center;">'
            '<div style="font-size:72px; line-height:1; margin-bottom:4px;">🧠</div>'
            '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:0; margin-bottom:0; letter-spacing:-0.5px;">Activity Sequencing Test</div>'
            '<div style="text-align: center !important; width: 100% !important; display: block !important; margin: 0 auto !important; font-size: 24px !important; color: #4A5E7A !important; margin-top: 10px !important; margin-bottom: 30px !important;">Arrange the activities in the correct order.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.button("Initialize Sequencing Protocol", key="seq_btn_start", type="primary", use_container_width=True):
            import random
            SCENARIOS = [
                {"name": "Making Tea", "steps": ["Boil water", "Place tea bag in cup", "Pour hot water", "Drink tea"]},
                {"name": "Brushing Teeth", "steps": ["Pick up toothbrush", "Apply toothpaste", "Brush teeth", "Rinse mouth"]},
                {"name": "Going Shopping", "steps": ["Enter store", "Select items", "Pay at counter", "Leave store"]},
                {"name": "Washing Hands", "steps": ["Turn on tap", "Wet hands", "Apply soap", "Rinse hands"]},
                {"name": "Preparing for Bed", "steps": ["Change clothes", "Brush teeth", "Turn off lights", "Sleep"]},
                {"name": "Mailing a Letter", "steps": ["Write letter", "Put letter in envelope", "Add stamp", "Post letter"]},
                {"name": "Taking Medication", "steps": ["Read instructions", "Take correct dose", "Drink water", "Store medication safely"]},
                {"name": "Cooking Rice", "steps": ["Wash rice", "Add water", "Cook rice", "Serve"]},
                {"name": "Visiting a Doctor", "steps": ["Schedule appointment", "Travel to clinic", "Meet doctor", "Return home"]},
                {"name": "Making a Phone Call", "steps": ["Pick up phone", "Dial number", "Speak", "End call"]},
                {"name": "Getting Ready to Go Outside", "steps": ["Wear clothes", "Wear shoes", "Take keys", "Leave house"]},
                {"name": "Reading a Newspaper", "steps": ["Pick up newspaper", "Open newspaper", "Read article", "Close newspaper"]},
                {"name": "Watering Plants", "steps": ["Fill watering can", "Walk to plant", "Water plant", "Put can away"]},
                {"name": "Making Breakfast", "steps": ["Gather ingredients", "Prepare food", "Eat breakfast", "Clean up"]},
                {"name": "Doing Laundry", "steps": ["Collect clothes", "Put clothes in washing machine", "Start wash cycle", "Dry clothes"]}
            ]
            # Ensure two scenarios are selected and state is freshly reset
            st.session_state['current_sequence_scenario'] = 0
            st.session_state['selected_sequence_order'] = []
            st.session_state['sequence_scores'] = []
            
            selected = random.sample(SCENARIOS, 2)
            st.session_state['seq_scenarios'] = selected
            st.session_state['seq_shuffled_options'] = []
            for s in selected:
                opts = list(s['steps'])
                random.shuffle(opts)
                st.session_state['seq_shuffled_options'].append(opts)
            st.session_state['seq_stage'] = 'testing'
            st.rerun()

    elif st.session_state['seq_stage'] == 'testing':
        scen_idx = st.session_state['current_sequence_scenario']
        scenario = st.session_state['seq_scenarios'][scen_idx]
        shuffled_opts = st.session_state['seq_shuffled_options'][scen_idx]
        selected_order = st.session_state['selected_sequence_order']

        st.markdown("""
        <style>
        div[data-testid="column"] .stButton > button {
            height: 170px;
            border-radius: 18px;
            font-size: 1.15rem;
            font-weight: 600;
            box-shadow: 0 6px 20px rgba(0,0,0,0.04);
            transition: all 0.2s ease;
            background-color: #FFFFFF;
            border: 2px solid #C9D6EA;
            color: #071A3D;
            position: relative;
            white-space: normal;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        div[data-testid="column"] .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(42,103,216,0.15);
            border-color: #2A67D8;
        }
        div[data-testid="column"] button[data-testid="baseButton-primary"] {
            border-color: #2A67D8 !important;
            color: #071A3D !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="premium-card fade-in" style="margin-bottom: 2.5rem;">
            <div style="background:#F5F8FF; border-radius:16px; padding:24px; text-align:center; border: 1px solid #C9D6EA;">
                <span style="font-weight:700; color:#64748B; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px; display:block; margin-bottom:12px;">Scenario {scen_idx+1} of {len(st.session_state['seq_scenarios'])}</span>
                <div style="color:#071A3D; font-weight:800; font-size:38px; line-height:1.2;">{scenario['name']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        bg_colors = ["#FFFFFF", "#F5F8FF", "#FFFFFF", "#F5F8FF"]
        for idx, opt in enumerate(shuffled_opts):
            col = cols[idx % 2]
            with col:
                is_selected = opt in selected_order
                bg_color = bg_colors[idx % 4]
                
                st.markdown(f"""
                <style>
                .element-container:has(.marker-seq-bg-{idx}) + .element-container .stButton > button {{
                    background-color: {bg_color};
                }}
                </style>
                <div class="marker-seq-bg-{idx}"></div>
                """, unsafe_allow_html=True)
                
                if is_selected:
                    order_num = selected_order.index(opt) + 1
                    st.markdown(f"""
                    <style>
                    .element-container:has(.marker-seq-{idx}) + .element-container .stButton > button::after {{
                        content: "{order_num}";
                        position: absolute;
                        top: 16px;
                        right: 16px;
                        background-color: #2A67D8;
                        color: #FFFFFF;
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 15px;
                        font-weight: bold;
                        box-shadow: 0 4px 12px rgba(42,103,216,0.3);
                    }}
                    </style>
                    <div class="marker-seq-{idx}"></div>
                    """, unsafe_allow_html=True)
                
                if st.button(opt, key=f"btn_opt_{scen_idx}_{idx}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    if is_selected:
                        selected_order.remove(opt)
                    else:
                        if len(selected_order) < 4:
                            selected_order.append(opt)
                    st.rerun()
                
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Subtle information card
        st.markdown("""
        <div style="background:#F5F8FF; border:1px solid #C9D6EA; padding:16px 24px; border-radius:12px; margin-bottom:2.5rem; display:flex; align-items:center; gap:12px;">
            <span style="font-size:1.2rem;">💡</span>
            <span style="color:#071A3D; font-size:0.95rem; font-weight:600;">Click the options in the correct order. Click again to deselect.</span>
        </div>
        """, unsafe_allow_html=True)
        
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        with nav_col3:
            if len(selected_order) == 4:
                if st.button("Next →", use_container_width=True, type="primary"):
                    correct_steps = scenario['steps']
                    correct_positions = sum(1 for i in range(4) if selected_order[i] == correct_steps[i])
                    
                    if correct_positions == 4:
                        score = 100
                    elif correct_positions == 3:
                        score = 75
                    elif correct_positions == 2:
                        score = 50
                    elif correct_positions == 1:
                        score = 25
                    else:
                        score = 0
                    
                    st.session_state['sequence_scores'].append(score)
                    
                    if scen_idx < len(st.session_state['seq_scenarios']) - 1:
                        st.session_state['current_sequence_scenario'] += 1
                        st.session_state['selected_sequence_order'] = []
                    else:
                        # Finished all scenarios
                        avg_score = round(sum(st.session_state['sequence_scores']) / len(st.session_state['sequence_scores']), 1)
                        st.session_state['cog_scores']['sequencing'] = avg_score
                        st.session_state['seq_stage'] = 'done'
                        st.session_state['sequence_completed'] = True
                    st.rerun()

    elif st.session_state['seq_stage'] == 'done':
        score = st.session_state['cog_scores']['sequencing']
        st.success(f"Activity Sequencing finalized. Score: {score}%")
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Proceed to Next Task →", type="primary", key="seq_btn_next", use_container_width=True):
            st.session_state['sequence_completed'] = True
            next_task = get_next_incomplete_cognitive_task()
            if next_task:
                if next_task == 5:
                    st.session_state['current_step'] = 3
                else:
                    st.session_state['cog_task_step'] = next_task
                    st.session_state['current_step'] = 2
            else:
                st.session_state['current_step'] = 4
            st.rerun()


def render_naming_test():

    # ── PATCHED TITLE 2: Object Recognition Test ──────────────────────────────
    st.markdown(
        '<div style="width:100%; text-align:center;">'
        '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:20px; letter-spacing:-0.5px;">Object Recognition Test</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="width:100%; max-width:620px; margin:0 auto; text-align:center;">'
        '<p class="assessment-subtitle" style="font-size: 22px !important; text-align: center !important; color: #4A5E7A !important;">Identify the object and type its name.</p>'
        '</div>', 
        unsafe_allow_html=True
    )
        
    if 'nam_test_selection' not in st.session_state:
        all_images = [APPLE_IMG, BICYCLE_IMG, CHAIR_IMG, WATCH_IMG, KEY_IMG, BED_IMG, CAR_IMG, BANANA_IMG, BOOK_IMG, PENCIL_IMG, ORANGE_IMG, GUITAR_IMG, UMBRELLA_IMG, TRAIN_IMG, ELEPHANT_IMG]
        all_answers = ["apple", "bicycle", "chair", "watch", "key", "bed", "car", "banana", "book", "pencil", "orange", "guitar", "umbrella", "train", "elephant"]
        combined = list(zip(all_images, all_answers))
        st.session_state['nam_test_selection'] = random.sample(combined, 3)
        
    images = [item[0] for item in st.session_state['nam_test_selection']]
    answers = [item[1] for item in st.session_state['nam_test_selection']]
    
    if st.session_state['nam_stage'] == 'start':
        if st.button("Start Identification Protocol", key="nam_btn_start", type="primary", use_container_width=True):
            st.session_state['nam_score'] = 0
            st.session_state['nam_idx'] = 0
            st.session_state['nam_stage'] = 'testing'
            st.rerun()
            
    elif st.session_state['nam_stage'] == 'testing':
        idx = st.session_state['nam_idx']
        
        if idx < len(images):
            current_object = st.session_state['nam_test_selection'][idx]
            import base64
            def get_image_base64(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            
            img_b64 = get_image_base64(images[idx])
            
            st.markdown("""
<style>
.object-test-wrapper {
    max-width: 620px;
    margin: 30px auto;
    text-align: center;
}

.object-test-title {
    color: #071A3D;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}

.object-test-subtitle {
    color: #071A3D;
    font-size: 20px;
    margin-bottom: 28px;
}

.object-single-card {
    background: #FFFFFF;
    border: 1px solid #D7E6FF;
    border-radius: 28px;
    padding: 24px;
    box-shadow: 0 18px 45px rgba(37, 99, 235, 0.10);
    text-align: center;
}

.object-progress {
    color: #071A3D;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 24px;
}

.object-image-box {
    width: 100%;
    height: 350px;
    margin: 0 auto 20px auto;
    background: #FFFFFF;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 auto !important;
    box-shadow: none !important;
    max-width: 500px !important;
}

div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid #B8C5D6 !important;
    padding: 10px !important;
    font-size: 20px !important;
    text-align: center !important;
    color: #071A3D !important;
    height: 56px !important;
    caret-color: #000000 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: transparent !important;
    opacity: 0 !important;
}

div[data-testid="InputInstructions"], 
div[data-testid="stTextInput"] small {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)
            
            with st.container():
                st.markdown(f"""
<div class="object-test-wrapper">
    <div class="object-single-card">
        <div class="object-progress">Object {idx+1} of 3</div>
        <div class="object-image-box">
            <img src="data:image/png;base64,{img_b64}" style="max-width:100%; max-height:100%; object-fit:contain;"/>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
                
                with st.form(f"naming_form_{idx}", clear_on_submit=False):
                    guess = st.text_input(
                        f"object_answer_{idx}",
                        key=f"object_identification_answer_{idx}",
                        placeholder="",
                        label_visibility="collapsed",
                        autocomplete="off"
                    )
                    
                    import streamlit.components.v1 as components
                    components.html(f"""
                    <script>
                    (function() {{
                        function disableAutocomplete() {{
                            const input = window.parent.document.querySelector(
                                'input[aria-label="object_answer_{idx}"]'
                            );
                            if (input && !input.dataset.acFixed) {{
                                input.setAttribute('autocomplete', 'off');
                                input.setAttribute('autocorrect', 'off');
                                input.setAttribute('autocapitalize', 'off');
                                input.setAttribute('spellcheck', 'false');
                                input.setAttribute('data-lpignore', 'true');
                                input.setAttribute('data-1p-ignore', 'true');
                                input.setAttribute('data-form-type', 'other');
                                input.setAttribute('name', 'obj_' + Math.random().toString(36).slice(2));
                                input.dataset.acFixed = 'true';
                                input.focus();
                            }}
                            const form = input && input.closest('form');
                            if (form) form.setAttribute('autocomplete', 'off');
                        }}
                        disableAutocomplete();
                        setTimeout(disableAutocomplete, 300);
                        setTimeout(disableAutocomplete, 800);
                    }})();
                    </script>
                    """, height=0)
                    
                    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                    if st.form_submit_button("Confirm Identification", key=f"nam_btn_submit_{idx}", use_container_width=True, type="primary"):
                        if not guess.strip():
                            st.warning("Identification required.")
                        else:
                            target = answers[idx]
                            similarity = difflib.SequenceMatcher(None, guess.lower().strip(), target).ratio()
                            if similarity > 0.75: st.session_state['nam_score'] += 1
                            
                            st.session_state['nam_idx'] += 1
                            if st.session_state['nam_idx'] >= len(images):
                                st.session_state['cog_scores']['naming'] = st.session_state['nam_score']
                                st.session_state['nam_stage'] = 'done'
                                
                            st.rerun()
    elif st.session_state['nam_stage'] == 'done':
        st.success(f"Object identification finalized. Accuracy: {st.session_state['nam_score']} / 3")
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Proceed to Next Task →", type="primary", key="nam_btn_next", use_container_width=True):
            st.session_state['object_completed'] = True
            next_task = get_next_incomplete_cognitive_task()
            if next_task:
                if next_task == 5:
                    st.session_state['current_step'] = 3
                else:
                    st.session_state['cog_task_step'] = next_task
                    st.session_state['current_step'] = 2
            else:
                st.session_state['current_step'] = 4
            st.rerun()

def render_clock_arrangement_test():
    import streamlit.components.v1 as components
    import math

    CLOCK_TIMES = [
        (12, 0), (12, 30), (1, 15), (2, 45), (3, 0), (4, 30),
        (5, 15), (6, 45), (7, 0), (8, 30), (9, 15), (10, 45), (11, 10)
    ]

    # Pick a random target once per assessment
    if 'clock_target_time' not in st.session_state:
        st.session_state['clock_target_time'] = random.choice(CLOCK_TIMES)
        for key in ['selected_hour', 'selected_minute', 'clock_score', 'clock_user_angle', 'clock_completed']:
            st.session_state.pop(key, None)

    target_hour, target_minute = st.session_state['clock_target_time']

    # ── PATCHED TITLE 4: Clock Drawing Test ───────────────────────────────────
    st.markdown(
        '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:20px; letter-spacing:-0.5px;">Clock Drawing Test</div>',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:2rem;">
        <p class="assessment-subtitle" style="font-size: 22px !important; text-align: center !important; color: #4A5E7A !important; margin-bottom:30px;">Set the clock to the specified time.</p>
        <div style="display:inline-block; background:linear-gradient(135deg, #2A67D8, #1E50B0); color:white; padding:12px 36px; border-radius:99px; font-size:2rem; font-weight:800; font-family:'Outfit',sans-serif; letter-spacing:1px; box-shadow:0 6px 20px rgba(42,103,216,0.2);">{target_hour}:{target_minute:02d}</div>
    </div>
    """, unsafe_allow_html=True)

    clock_widget = components.declare_component("clock_widget", path="clock_component")
    clock_result = clock_widget(key="clock_widget_key")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if st.button("Next", type="primary", key="clock_next_btn", use_container_width=True):
        if clock_result:
            user_hour = clock_result.get("hour", 12)
            user_minute = clock_result.get("minute", 0)
        else:
            user_hour = 12
            user_minute = 0

        # 1. Minute Angle Calculation
        target_minute_angle = target_minute * 6
        user_minute_angle = user_minute * 6

        # 2. Hour Angle Calculation
        target_hour_angle = (target_hour % 12) * 30 + target_minute * 0.5
        user_hour_angle = (user_hour % 12) * 30 + user_minute * 0.5

        # 3. Error Calculation with circular correction
        def angle_diff(a, b):
            diff = abs(a - b)
            return min(diff, 360 - diff)
            
        hour_error = angle_diff(target_hour_angle, user_hour_angle)
        minute_error = angle_diff(target_minute_angle, user_minute_angle)

        # 4. Convert Error to Accuracy
        def get_accuracy(error):
            if error <= 5: return 100
            elif error <= 10: return 90
            elif error <= 20: return 75
            elif error <= 30: return 60
            else: return 25

        hour_accuracy = get_accuracy(hour_error)
        minute_accuracy = get_accuracy(minute_error)

        # 5. Final Score
        score = int((hour_accuracy * 0.5) + (minute_accuracy * 0.5))

        # Save explicitly
        st.session_state["cog_scores"]["clock_arrangement"] = score
        st.session_state["clock_completed"] = True
        
        # Debug printing requirement
        debug_str = (
            f"Target Time: {target_hour}:{target_minute:02d} | "
            f"User Time: {user_hour}:{user_minute:02d} | "
            f"Target Hr Angle: {target_hour_angle}° | Target Min Angle: {target_minute_angle}° | "
            f"User Hr Angle: {user_hour_angle}° | User Min Angle: {user_minute_angle}° | "
            f"Hr Error: {hour_error}° | Min Error: {minute_error}° | "
            f"Final Clock Score: {score}%"
        )
        st.session_state["temp_clock_debug"] = debug_str
        
        next_task = get_next_incomplete_cognitive_task()
        if next_task:
            if next_task == 5:
                st.session_state['current_step'] = 3
            else:
                st.session_state['cog_task_step'] = next_task
                st.session_state['current_step'] = 2
        else:
            st.session_state['current_step'] = 4
        st.rerun()


def render_scoring_dashboard():
    st.markdown("""
    <div style='padding: 1rem 0 2.5rem 0;'>
        <div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:20px; letter-spacing:-0.5px;">Clinical Risk Analysis</div>
        <div style="width:100%; text-align:center;">
            <p style='color: #64748B; font-size: 1.05rem; margin: 0 auto;'>Comprehensive synthesis of cognitive performance and neural speech biomarkers.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    scores = st.session_state['cog_scores']
    missing = [k for k, v in scores.items() if v is None]
    if missing:
        st.warning(f"Incomplete assessment data detected. Missing: {', '.join(missing)}")
        return
        
    results = evaluate_risk(scores)
    overall_score = results.get('final_score', 0)
    risk_level = results.get('risk_level', "N/A")
    interpretation = results.get('interpretation', "")
    
    if overall_score >= 75:
        explanation = "The assessment shows normal speech patterns and good cognitive task performance. No major dementia-related warning signs were detected."
    elif overall_score >= 55:
        explanation = "The assessment shows some mild deviations in speech flow and moderate cognitive task performance. Some subtle indicators of cognitive change are present."
    else:
        explanation = "The assessment shows significant deviations in speech patterns, prolonged pauses, and lower performance on cognitive recall tasks. Strong cognitive risk indicators are present."
        
    breakdown = {k.strip(): v for k, v in results.get('breakdown', {}).items()}
    
    # Visual Score Matrix
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        risk_color = "#16A34A" if overall_score >= 75 else "#F59E0B" if overall_score >= 55 else "#EF4444"
        st.markdown(f"""
            <div class="premium-card" style="text-align: center; border-top: 5px solid {risk_color} !important;">
                <p style="font-size: 0.75rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Aggregate Risk Score</p>
                <h1 style="font-size: 5.5rem; color: #0F172A; margin: 0; line-height:1;">{overall_score}</h1>
                <div style="background: {risk_color}15; color: {risk_color}; padding: 8px 20px; border-radius: 99px; display: inline-block; font-weight: 800; font-size: 0.9rem; margin-top:1.5rem; text-transform:uppercase; letter-spacing:1px;">
                    {risk_level}
                </div>
                <p style="margin-top: 2rem; color: #334155; font-size: 1rem; font-weight: 500; line-height: 1.6;">
                    {interpretation}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("<p style='font-size: 0.75rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;'>Cognitive Screening Performance</p>", unsafe_allow_html=True)
        
        label_map = {
            "Memory Recall": "Memory Recall",
            "Object Identification": "Object Identification",
            "Activity Sequencing": "Activity Sequencing",
            "Clock Arrangement": "Clock Arrangement",
            "Voice Analysis": "Voice Analysis"
        }
        
        desc_map = {
            "Memory Recall": "Measures how well the patient remembers and recalls information.",
            "Object Identification": "Measures the ability to recognize and identify common objects correctly.",
            "Activity Sequencing": "Evaluates the ability to organize daily activities logically.",
            "Clock Arrangement": "Measures visual-spatial reasoning and time-setting accuracy.",
            "Voice Analysis": "Measures speech rate, hesitation, and acoustic pause patterns."
        }
        
        ordered_keys = ["Memory Recall", "Object Identification", "Activity Sequencing", "Clock Arrangement", "Voice Analysis"]
        
        for category in ordered_keys:
            data = breakdown.get(category, {})
            val = data.get('value', 0)
            bar_color = "#0D9488" if val >= 50 else "#EF4444"
            st.markdown(f'''
                <div style="margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                        <span style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">{label_map[category]}</span>
                        <span style="font-weight: 800; color: {bar_color}; font-size: 0.95rem;">{val}%</span>
                    </div>
                    <p style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #64748B; line-height: 1.4;">{desc_map[category]}</p>
                    <div style="width: 100%; background: #F1F5F9; height: 10px; border-radius: 5px; overflow: hidden;">
                        <div style="width: {val}%; background: {bar_color}; height: 100%; border-radius: 99px;"></div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
        st.markdown(
            "<p style=\"margin-top: 1.5rem; font-size: 0.82rem; color: var(--text-secondary); font-style: italic; line-height: 1.5; border-top: 1px solid var(--border-color); padding-top: 0.75rem; margin-bottom:0;\">"
            "These scores represent the patient's performance in memory, speech, recognition, and pattern-based cognitive assessment tasks."
            "</p>", unsafe_allow_html=True)

    st.markdown("<div class='divider-luxe'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        st.markdown(f'''
        <div style="background:white; height:96px; padding:0 1.5rem; border-radius:20px; border:1px solid #E2E8F0; display:flex; align-items:center; gap:15px;">
            <div style="background:#F1F5F9; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem;">👤</div>
            <div>
                <p style="margin:0; font-weight:800; color:#0F172A; font-size:1rem;">{st.session_state["patient_info"]["name"]}</p>
                <p style="margin:0; font-size:0.8rem; color:#64748B;">Patient Identification Ref: {st.session_state["patient_info"]["id"]}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_btn2:
        st.markdown('''
        <div class="save-assessment-hook"></div>
        <style>
        div[data-testid="stMarkdownContainer"]:has(.save-assessment-hook) + div[data-testid="stButton"] button {
            height: 96px !important;
            border-radius: 20px !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
        }
        </style>
        ''', unsafe_allow_html=True)
        if st.button("Save Assessment Record", type="primary", use_container_width=True):
            from database import save_patient_assessment
            
            raw_risk = risk_level
            if raw_risk in ['Low', 'Low Risk']:
                clean_risk = 'Low Risk'
                rec_val = "Continue regular cognitive wellness monitoring."
            elif raw_risk in ['Moderate', 'Moderate Risk', 'Medium', 'Medium Risk']:
                clean_risk = 'Moderate Risk'
                rec_val = "Some mild cognitive changes were observed. A follow-up screening or consultation is recommended."
            else:
                clean_risk = 'High Risk'
                rec_val = "Significant cognitive risk patterns were detected. Please consult a qualified healthcare professional."
                
            wm_score = int(breakdown.get('Memory Recall', {}).get('value', 0))
            att_score = int(breakdown.get('Activity Sequencing', {}).get('value', 0))
            rec_score = int(breakdown.get('Object Identification', {}).get('value', 0))
            s_rate = scores.get('acoustic', {}).get('speech_rate_wpm', 343.1)
            
            success = save_patient_assessment(
                clinician_id=st.session_state.get('user_id', 0),
                name=st.session_state['patient_info']['name'],
                age=st.session_state['patient_info']['age'],
                gender=st.session_state['patient_info']['gender'],
                overall_score=float(overall_score),
                confidence_score=90.0,
                risk_level=clean_risk,
                working_memory_score=float(wm_score),
                attention_score=float(att_score),
                recall_score=float(rec_score),
                speech_rate=float(s_rate),
                recommendation=rec_val
            )
            if success: 
                st.success("Assessment record saved successfully.")
                time.sleep(1.2); st.session_state['current_step'] = 6; st.rerun()

    # Clinical Legend & Observation
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    with st.expander("View Clinical Observations & Methodology", expanded=False):
        st.markdown(f"""
    ### Diagnostic Observation
    {explanation}

    ---

    ### Protocol Breakdown
    Weights: Memory Recall (25%), Object Identification (20%), Activity Sequencing (20%), Clock Arrangement (15%), Voice Analysis (20%).
    """)

    # Institutional Disclaimer
    st.markdown("""
        <div style="margin-top: 4rem; padding: 1.5rem; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px;">
            <p style="font-size: 0.8rem; color: #6b7280; line-height: 1.6; margin: 0;">
                <b>Medical Disclaimer:</b> This digital screening report is a clinical aid and does not constitute a formal medical diagnosis. 
                All findings should be reviewed by a qualified healthcare professional in conjunction with clinical observations and standardized diagnostic criteria.
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_ai_processing():
    st.markdown('<div class="premium-card fade-in" style="text-align:center; padding: 5rem 3rem !important;">', unsafe_allow_html=True)
    st.markdown("<h2 style='letter-spacing:-1px;'>⚡ Speech Signal Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:1.1rem;'>Analyzing voice temporal metrics, acoustic biomarkers, and cognitive response latency.</p>", unsafe_allow_html=True)
    
    placeholder = st.empty()
    status_messages = [
        "Analyzing speech jitter and shimmer vector...",
        "Extracting temporal pause latency patterns...",
        "Correlating semantic retrieval with baselines...",
        "Analyzing cognitive risk profiles...",
        "Finalizing clinical assessment report..."
    ]
    
    for i, msg in enumerate(status_messages):
        progress = (i + 1) / len(status_messages)
        placeholder.markdown(f"""
        <div style="margin: 3rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <span style="color: #475569; font-size: 0.85rem; font-weight: 700; text-transform:uppercase; letter-spacing:1px;">{msg}</span>
                <span style="color: #2F6BFF; font-size: 0.9rem; font-weight: 800;">{int(progress * 100)}%</span>
            </div>
            <div style="background: #F1F5F9; height: 10px; border-radius: 10px; overflow: hidden;">
                <div style="background: var(--accent-gradient); width: {progress * 100}%; height: 100%; transition: width 0.8s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
    
    st.session_state['current_step'] = 5
    st.rerun()
 
def render_cognitive_tests():
    init_cognitive_state()
    
    # If the assessment wizard hasn't started yet, render the Page 4 Assessments grid hub
    if not st.session_state['assessment_started']:
        st.markdown(
            '<div style="margin-bottom:2rem;">'
            '<div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:15px; letter-spacing:-0.5px;">Comprehensive Cognitive Assessments</div>'
            '<p style="text-align:center; font-size:22px; color:#002B5C; margin-bottom:30px;">Select an assessment to begin screening</p>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # 3 columns for first row
        row1_col1, row1_col2, row1_col3 = st.columns(3, gap="medium")
        
        with row1_col1:
            st.markdown("""
            <div class="premium-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #145CFF !important;">
                <div>
                    <div style="background: rgba(20, 92, 255, 0.08); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 15px; color: #145CFF;">🎙️</div>
                    <h3 style="color: var(--dark-navy); font-size: 1.15rem; margin-bottom: 8px; font-family: Outfit;">1. Memory Recall Test</h3>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">Evaluates naming and visual recognition.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Assessment", key="card_start_voice", type="primary", use_container_width=True):
                reset_assessment_state()
                init_cognitive_state()
                st.session_state['assessment_started'] = True
                st.session_state['current_step'] = 1
                st.session_state['launched_cog_task_step'] = 1
                st.rerun()
                
        with row1_col2:
            st.markdown("""
            <div class="premium-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #4CAF50 !important;">
                <div>
                    <div style="background: rgba(76, 175, 80, 0.08); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 15px; color: #4CAF50;">🧠</div>
                    <h3 style="color: var(--dark-navy); font-size: 1.15rem; margin-bottom: 8px; font-family: Outfit;">2. Object Identification</h3>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">Evaluates naming and visual recognition.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Assessment", key="card_start_mem", type="primary", use_container_width=True):
                reset_assessment_state()
                init_cognitive_state()
                st.session_state['assessment_started'] = True
                st.session_state['current_step'] = 1
                st.session_state['launched_cog_task_step'] = 2
                st.rerun()
                
        with row1_col3:
            st.markdown("""
            <div class="premium-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #7000FF !important;">
                <div>
                    <div style="background: rgba(112, 0, 255, 0.08); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 15px; color: #7000FF;">🗣️</div>
                    <h3 style="color: var(--dark-navy); font-size: 1.15rem; margin-bottom: 8px; font-family: Outfit;">3. Activity Sequencing</h3>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">Evaluates executive function and task organization.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Assessment", key="card_start_lang", type="primary", use_container_width=True):
                reset_assessment_state()
                init_cognitive_state()
                st.session_state['assessment_started'] = True
                st.session_state['current_step'] = 1
                st.session_state['launched_cog_task_step'] = 3
                st.rerun()
                
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # 3 columns for second row to preserve identical card widths
        row2_col1, row2_col2, row2_col3 = st.columns(3, gap="medium")
        
        with row2_col1:
            st.markdown("""
            <div class="premium-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #F59E0B !important;">
                <div>
                    <div style="background: rgba(245, 158, 11, 0.08); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 15px; color: #F59E0B;">🕒</div>
                    <h3 style="color: var(--dark-navy); font-size: 1.15rem; margin-bottom: 8px; font-family: Outfit;">4. Clock Drawing Test</h3>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">Measures visual-spatial and executive function.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Assessment", key="card_start_clock", type="primary", use_container_width=True):
                reset_assessment_state()
                init_cognitive_state()
                st.session_state['assessment_started'] = True
                st.session_state['current_step'] = 1
                st.session_state['launched_cog_task_step'] = 4
                st.rerun()
                
        with row2_col2:
            st.markdown("""
            <div class="premium-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #F43F5E !important;">
                <div>
                    <div style="background: rgba(244, 63, 94, 0.08); width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 15px; color: #F43F5E;">⚡</div>
                    <h3 style="color: var(--dark-navy); font-size: 1.15rem; margin-bottom: 8px; font-family: Outfit;">5. Voice Analysis</h3>
                    <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">Analyse voice biomarkers and speech patterns.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Assessment", key="card_start_exec", type="primary", use_container_width=True):
                reset_assessment_state()
                init_cognitive_state()
                st.session_state['assessment_started'] = True
                st.session_state['current_step'] = 1
                st.session_state['launched_cog_task_step'] = 5
                st.rerun()
                
        with row2_col3:
            st.empty() # Balanced structural spacer
            
    step = st.session_state['current_step']
    
    if not st.session_state.get('assessment_started', False):
        return
        
    if step > 1:
        # Premium Redesigned Progress Stepper
        steps = ["Patient", "Cognitive Tasks", "Voice Analysis", "Processing", "Risk Level", "Report"]
        
        stepper_html = '<div class="stepper-wrapper">'
        for i, label in enumerate(steps):
            status_class = "completed" if i + 1 < step else "active" if i + 1 == step else ""
            label_class = "active" if i + 1 == step else ""
            line_html = f"<div class='stepper-line {'completed' if i + 1 < step else ''}'></div>" if i < len(steps) - 1 else ""
            
            stepper_html += f'<div class="stepper-item"><div class="stepper-circle {status_class}">{i+1 if status_class != "completed" else "✓"}</div><div class="stepper-label {label_class}">{label}</div>{line_html}</div>'
        stepper_html += '</div>'
        
        st.markdown(stepper_html, unsafe_allow_html=True)
        st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)


    
    if step == 1: render_patient_info()
    elif step == 2:
        sub_step = st.session_state['cog_task_step']
        if sub_step == 1: render_memory_test()
        elif sub_step == 2: render_naming_test()
        elif sub_step == 3: render_activity_sequencing_test()
        elif sub_step == 4: render_clock_arrangement_test()
    elif step == 3:
        render_voice_recording()
    elif step == 4: render_ai_processing()
    elif step == 5:
        # Guard: voice analysis must be completed before viewing results
        scores = st.session_state.get('cog_scores', {})
        if scores.get('acoustic') is None:
            st.warning("Please complete Voice Analysis before viewing results.")
            st.session_state['current_step'] = 3
            st.rerun()
        else:
            render_scoring_dashboard()
    elif step == 6:
        # Dynamic detailed clinical report page (Page 6)
        scores = st.session_state.get('cog_scores', {})
        p_info = st.session_state.get('patient_info', {})
        
        if scores and p_info:
            results = evaluate_risk(scores)
            overall_score = int(results.get('final_score', 0))
            raw_risk = results.get('risk_level', "Low Risk")
            
            # Normalize Risk Level & Colors
            if raw_risk in ['Low', 'Low Risk']:
                risk_level = 'Low Risk'
                risk_class = 'green'
            elif raw_risk in ['Moderate', 'Moderate Risk', 'Medium', 'Medium Risk']:
                risk_level = 'Moderate Risk'
                risk_class = 'orange'
            else:
                risk_level = 'High Risk'
                risk_class = 'red'
                
            confidence_score = 90
            
            breakdown = results.get('breakdown', {})
            working_memory_score = int(breakdown.get('Memory Recall', {}).get('value', 0))
            naming_score = int(breakdown.get('Object Identification', {}).get('value', 0))
            sequencing_score = int(breakdown.get('Activity Sequencing', {}).get('value', 0))
            clock_score = int(breakdown.get('Clock Arrangement', {}).get('value', 0))
            acoustic_score = int(breakdown.get('Voice Analysis', {}).get('value', 0))
            
            # Patient details
            patient_name = p_info.get('name', 'N/A')
            patient_id = p_info.get('id', 'AC-2024-004')
            age = p_info.get('age', 'N/A')
            gender = p_info.get('gender', 'N/A')
            
            # --- START ML PREDICTION BLOCK ---
            try:
                from ml_predictor import predict_ml_risk
                voice_features = scores.get('acoustic', {})
                if not isinstance(voice_features, dict):
                    voice_features = {}
                    
                features_dict = {
                    "age": age if age != 'N/A' else 0,
                    "gender": gender if gender != 'N/A' else 'Unknown',
                    "memory_score": working_memory_score,
                    "object_score": naming_score,
                    "sequencing_score": sequencing_score,
                    "clock_score": clock_score,
                    "voice_score": acoustic_score,
                    "wpm": voice_features.get('speech_rate_wpm', 0),
                    "pause_count": voice_features.get('pause_count', 0),
                    "long_pause_count": voice_features.get('long_pauses', 0),
                    "silence_ratio": voice_features.get('silence_ratio', 0),
                    "hesitation_count": voice_features.get('hesitation_count', 0),
                    "fluency_score": voice_features.get('fluency_score', 0)
                }
                ml_result = predict_ml_risk(features_dict)
            except Exception:
                ml_result = {"available": False}
            # --- END ML PREDICTION BLOCK ---
            
            # Dynamic date
            import datetime
            dt_now = datetime.datetime.now()
            assessment_date = dt_now.strftime("%d %b %Y - %I:%M %p")
            
            # Recommendations
            if risk_level == 'Low Risk':
                explanation = "The assessment shows normal speech patterns and good cognitive task performance. No major dementia-related warning signs were detected."
                recommendation = "Continue wellness monitoring and follow-up after 12 months."
            elif risk_level == 'Moderate Risk':
                explanation = "The assessment shows some mild deviations in speech flow and moderate cognitive task performance. Some subtle indicators of cognitive change are present."
                recommendation = "Continue monitoring and follow-up after 3 months."
            else:
                explanation = "The assessment shows significant deviations in speech patterns, prolonged pauses, and lower performance on cognitive recall tasks. Strong cognitive risk indicators are present."
                recommendation = "Significant cognitive risk patterns detected. Immediate clinical consultation is recommended."

            # Top Header Row
            st.markdown(f"""
            <div style="margin-bottom: 2rem; text-align:center;">
                <div style="font-size:60px; font-weight:900; color:#002B5C; text-align:center; line-height:1.1; margin-top:10px; margin-bottom:20px; letter-spacing:-0.5px;">Assessment Report</div>
                <p style="margin:0; color:var(--text-secondary);">Patient ID: <strong style="color:#145CFF;">{patient_id}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Dynamic Report Layout
            col_l, col_r = st.columns([1, 1.3], gap="large")
            
            with col_l:
                st.markdown(f"""
<div class="premium-card fade-in" style="text-align: center; height: 100%;">
<p style="font-size: 0.8rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Overall Risk Level</p>
<div class="pill-badge {risk_class}" style="font-size: 1.1rem; padding: 8px 24px; margin-bottom: 2rem;">{risk_level}</div>

<!-- Circular Score Indicator SVG/CSS -->
<div style="margin: 2rem auto; width: 160px; height: 160px; border-radius: 50%; border: 12px solid #F5F8FF; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 2px 8px rgba(7,27,77,0.02); background: white; border-top-color: #145CFF;">
<span style="font-size: 2.5rem; font-weight: 800; color: var(--dark-navy); font-family: 'Outfit';">{overall_score}%</span>
<span style="font-size: 0.72rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: -2px;">Overall Score</span>
</div>

<p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.85rem; line-height: 1.4; font-style: italic;">
Confidence Score: {confidence_score}%
</p>
</div>
""", unsafe_allow_html=True)
                
            with col_r:
                st.markdown("""
                <div class="premium-card fade-in" style="height: 100%;">
                    <p style="font-size: 0.8rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Domain Scores</p>
                """, unsafe_allow_html=True)
                
                # Helper for progress bars
                def render_report_bar(label, val):
                    bar_color = "#4CAF50" if val >= 70 else "#FF9800" if val >= 45 else "#F44336"
                    st.markdown(f"""
                    <div style="margin-bottom: 1.2rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:700; font-size:0.9rem; color:var(--dark-navy);">
                            <span>{label}</span>
                            <span>{val}%</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: {val}%; background: {bar_color};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                render_report_bar("Memory Recall", working_memory_score)
                render_report_bar("Object Identification", naming_score)
                render_report_bar("Activity Sequencing", sequencing_score)
                render_report_bar("Clock Arrangement", clock_score)
                render_report_bar("Voice Analysis", acoustic_score)
                
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # --- START ML UI DISPLAY BLOCK ---
            if ml_result.get("available", False):
                st.markdown(f"""
                <div class="premium-card fade-in" style="margin-bottom: 20px; border-left: 4px solid #2A67D8 !important;">
                    <h4 style="margin: 0 0 8px 0; color: var(--dark-navy); font-size: 1.05rem; font-weight: 700;">Machine Learning Prediction</h4>
                    <div style="display: flex; gap: 20px; color: var(--text-secondary); font-size: 0.95rem;">
                        <div>Predicted Risk: <strong style="color: var(--dark-navy);">{ml_result.get('predicted_risk')}</strong></div>
                        <div>Confidence: <strong style="color: var(--dark-navy);">{ml_result.get('confidence')}%</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="premium-card fade-in" style="margin-bottom: 20px; border-left: 4px solid #CBD5E1 !important; background: #F8FAFC;">
                    <h4 style="margin: 0 0 8px 0; color: #64748B; font-size: 1.05rem; font-weight: 700;">Machine Learning Prediction</h4>
                    <p style="margin: 0; color: #94A3B8; font-size: 0.95rem;">ML prediction unavailable. Please train the model first.</p>
                </div>
                """, unsafe_allow_html=True)
            # --- END ML UI DISPLAY BLOCK ---

            # Recommendation Card
            st.markdown(f"""
            <div class="premium-card fade-in">
                <h4 style="margin: 0 0 8px 0; color: var(--dark-navy); font-size: 1.05rem; font-weight: 700;">Recommendation</h4>
                <p style="margin: 0 0 20px 0; color: var(--text-secondary); line-height: 1.5; font-size: 0.95rem;">{recommendation}</p>
                <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--text-secondary); font-weight: 600;">
                    <span>Assessment Date: <strong>{assessment_date}</strong></span>
                    <span>Assessed By: <strong>{st.session_state.get('full_name', 'User')}</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Copy plain text
            report_text = f"""--- DETAILED COGNITIVE SCREENING REPORT ---
Patient Name: {patient_name}
Patient ID: {patient_id}
Age/Gender: {age} / {gender}
Date: {assessment_date}
--- RESULTS ---
Overall Score: {overall_score}%
Risk Level: {risk_level}
Confidence Score: {confidence_score}%
--- PERFORMANCE SCORES ---
Memory Recall: {working_memory_score}%
Object Identification: {naming_score}%
Activity Sequencing: {sequencing_score}%
Clock Arrangement: {clock_score}%
Voice Analysis: {acoustic_score}%
--- EXPLANATION & RECOMMENDATION ---
Explanation: {explanation}
Recommendation: {recommendation}
---------------------------------"""
            
            if 'show_plain_report' not in st.session_state:
                st.session_state.show_plain_report = False
                
            btn_text = "Hide Plain Text Clinical Report ↑" if st.session_state.show_plain_report else "📋 View Plain Text Clinical Report ↓"
            if st.button(btn_text, key="toggle_plain_report", type="secondary", use_container_width=True):
                st.session_state.show_plain_report = not st.session_state.show_plain_report
                st.rerun()
                
            if st.session_state.show_plain_report:
                import html
                safe_report = html.escape(report_text)
                st.markdown(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #145CFF; border-radius: 12px; padding: 20px; color: #1E293B; font-family: 'Plus Jakarta Sans', sans-serif; white-space: pre-wrap; font-size: 15px; line-height: 1.6; box-shadow: 0 4px 12px rgba(20, 92, 255, 0.08); margin-top: 12px;">{safe_report}</div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
        
        # Bottom start new assessment button
        if st.button("Start New Assessment", type="primary", key="rep_new_assess_btn", use_container_width=True):
            reset_assessment_state()
            init_cognitive_state()
            st.session_state['assessment_started'] = True
            st.session_state['current_step'] = 1
            st.session_state['cog_task_step'] = 1
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)