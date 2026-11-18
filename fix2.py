import re
import os

# --- Fix cognitive_tests.py (Issue 1) ---
cog_file = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\cognitive_tests.py"
with open(cog_file, "r", encoding="utf-8") as f:
    cog_content = f.read()

old_report_block = """            with st.expander("📋 Copy Plain Text Clinical Report"):
                st.code(report_text, language="text")"""

new_report_block = """            if 'show_plain_report' not in st.session_state:
                st.session_state.show_plain_report = False
                
            btn_text = "Hide Plain Text Clinical Report ↑" if st.session_state.show_plain_report else "📋 View Plain Text Clinical Report ↓"
            if st.button(btn_text, key="toggle_plain_report", type="secondary", use_container_width=True):
                st.session_state.show_plain_report = not st.session_state.show_plain_report
                st.rerun()
                
            if st.session_state.show_plain_report:
                import html
                safe_report = html.escape(report_text)
                st.markdown(f\"\"\"
                <div style="background-color: #FFFFFF; border: 1px solid #145CFF; border-radius: 12px; padding: 20px; color: #1E293B; font-family: 'Plus Jakarta Sans', sans-serif; white-space: pre-wrap; font-size: 15px; line-height: 1.6; box-shadow: 0 4px 12px rgba(20, 92, 255, 0.08); margin-top: 12px;">{safe_report}</div>
                \"\"\", unsafe_allow_html=True)"""

if old_report_block in cog_content:
    cog_content = cog_content.replace(old_report_block, new_report_block)
else:
    print("Could not find old report block in cognitive_tests.py")

with open(cog_file, "w", encoding="utf-8") as f:
    f.write(cog_content)


# --- Fix app.py (Issue 2) ---
app_file = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"
with open(app_file, "r", encoding="utf-8") as f:
    app_content = f.read()

guide_start = app_content.find("def page_assessment_guide():")
guide_end = app_content.find("def page_settings():")
old_guide = app_content[guide_start:guide_end]

new_guide = """def page_assessment_guide():
    st.markdown("<h2 style='font-size: 42px; font-weight: 900; color: #0B2A5B; margin-bottom: 0.5rem; letter-spacing: -0.5px;'>Assessment Guide</h2>", unsafe_allow_html=True)
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
            "desc": "The patient arranges daily activity steps in the correct order.",
            "bg": "#FAF5FF",
            "border": "#E9D5FF",
            "title_color": "#7E22CE",
            "criteria": "Score is based on how many steps are placed in the correct position.<br>- <b>4/4 correct</b> = 100%<br>- <b>3/4 correct</b> = 75%<br>- <b>2/4 correct</b> = 50%<br>- <b>1/4 correct</b> = 25%<br>- <b>0/4 correct</b> = 0%"
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
            "criteria": "- Clear reading with normal speed gives a higher score.<br>- Long pauses, hesitation, missing words, or very short speech reduce the score."
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
        
        st.markdown(f\"\"\"
        <div style="background-color: {item['bg']}; padding: 24px; border-radius: 16px; margin-bottom: 12px; border: 1px solid {item['border']}; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h3 style="margin-top: 0; color: {item['title_color']}; font-size: 1.5rem; font-weight: bold;">{item['title']}</h3>
            <p style="color: #334155; margin-bottom: 12px; font-size: 1.1rem;"><strong>How it works:</strong> {item['desc']}</p>
        </div>
        \"\"\", unsafe_allow_html=True)
        
        btn_label = "Hide Criteria ↑" if st.session_state[s_key] else "View Criteria ↓"
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(btn_label, key=b_key, type="secondary", use_container_width=True):
                st.session_state[s_key] = not st.session_state[s_key]
                st.rerun()
        
        if st.session_state[s_key]:
            st.markdown(f\"\"\"
            <div style="background: #FFFFFF; border: 1px solid #C9D6EA; border-radius: 18px; padding: 22px; color: #334155; font-size: 17px; line-height: 1.7; box-shadow: 0 8px 24px rgba(22, 74, 159, 0.06); margin-top: -8px; margin-bottom: 24px;">
                {item['criteria']}
            </div>
            \"\"\", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 40px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown(\"\"\"
    <div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 20px;">
        <em><strong>Disclaimer:</strong> This system is only for early screening support. It does not replace a doctor, clinical diagnosis, or professional medical advice.</em>
    </div>
    \"\"\", unsafe_allow_html=True)

"""

if old_guide in app_content:
    app_content = app_content.replace(old_guide, new_guide)
else:
    print("Could not find old guide block in app.py")

with open(app_file, "w", encoding="utf-8") as f:
    f.write(app_content)

print("Updates completed successfully.")
