import re

app_file = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# --- FIX 1: Assessment Guide ---
# I will replace the button logic in page_assessment_guide
guide_start = content.find("def page_assessment_guide():")
guide_end = content.find("def page_settings():")
old_guide = content[guide_start:guide_end]

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
        
        btn_label = "Hide Criteria ↑" if st.session_state.get(s_key, False) else "View Criteria ↓"
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(btn_label, key=b_key, type="secondary", use_container_width=True):
                st.session_state[s_key] = not st.session_state.get(s_key, False)
                st.session_state.page = "Guide"
                st.rerun()
        
        if st.session_state.get(s_key, False):
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

if old_guide in content:
    content = content.replace(old_guide, new_guide)
else:
    print("WARNING: Could not replace page_assessment_guide.")

# --- FIX 2: Patient Records ---
patients_start = content.find("def page_patients():")
patients_end = content.find("# =========================", patients_start)
old_patients = content[patients_start:patients_end]

new_patients = """def page_patients():
    st.markdown(\"\"\"
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
    \"\"\", unsafe_allow_html=True)

    if 'view_history_record_id' not in st.session_state:
        st.session_state['view_history_record_id'] = None

    if st.session_state['view_history_record_id'] is not None:
        rec_id = st.session_state['view_history_record_id']
        import sqlite3
        from database import DB_FILENAME
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        c.execute(\"\"\"
            SELECT a.id, p.name, p.age, p.gender, a.assessment_date, a.overall_score,
                   a.confidence_score, a.risk_level, a.working_memory_score,
                   a.attention_score, a.recall_score, a.speech_rate, a.recommendation
            FROM assessments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = ?
        \"\"\", (rec_id,))
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
        
        st.markdown(f\"\"\"
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 2rem;">
            <div>
                <h1 style="margin:0; font-family:'Outfit'; font-size:2.2rem; color:var(--dark-navy);">Assessment Report</h1>
                <p style="margin:0; color:var(--text-secondary);">Patient ID: <strong style="color:#0E9F6E;">AC-2024-{rid:03d}</strong></p>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
        
        if st.button("← Back to History List", type="secondary", key="back_to_list_btn"):
            st.session_state['view_history_record_id'] = None
            st.rerun()
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1.3], gap="large")
        with col_left:
            st.markdown(f\"\"\"
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
            \"\"\", unsafe_allow_html=True)
        with col_right:
            st.markdown(\"\"\"
            <div class="premium-card" style="height: 100%;">
                <p style="font-size: 0.8rem; font-weight: 800; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem;">Domain Scores</p>
            \"\"\", unsafe_allow_html=True)
            def render_domain_bar(label, score):
                bar_color = "#4CAF50" if score >= 70 else "#FF9800" if score >= 45 else "#F44336"
                st.markdown(f\"\"\"
                <div style="margin-bottom: 1.2rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:700; font-size:0.9rem; color:var(--dark-navy);">
                        <span>{label}</span>
                        <span>{int(score) if score != 'N/A' else 'N/A'}%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {score if score != 'N/A' else 0}%; background: {bar_color};"></div>
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)
            render_domain_bar("Memory Recall", wm_score)
            render_domain_bar("Object Identification", rec_score)
            render_domain_bar("Activity Sequencing", att_score)
            render_domain_bar("Voice Analysis & Latency", max(20.0, min(100.0, s_rate / 3.4)))
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(f\"\"\"
        <div class="premium-card">
            <h4 style="margin: 0 0 8px 0; color: var(--dark-navy); font-size: 1.05rem; font-weight: 700;">Clinical Recommendation</h4>
            <p style="margin: 0 0 20px 0; color: var(--text-secondary); line-height: 1.5; font-size: 0.95rem;">{rec_text}</p>
            <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--text-secondary); font-weight: 600;">
                <span>Assessment Date: <strong>{date_formatted}</strong></span>
                <span>Assessed By: <strong>{st.session_state.get('full_name', 'User')}</strong></span>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
        return

    st.markdown("<h2 style='font-size: 42px; font-weight: 900; color: #0B2A5B; margin-bottom: 0.5rem; letter-spacing: -0.5px;'>Patient Records</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-secondary); margin-bottom:2rem; font-size:0.95rem;'>Search patient by name to view their historical assessments and risk trends.</p>", unsafe_allow_html=True)
    
    if 'search_query_name' not in st.session_state:
        st.session_state['search_query_name'] = ""
    if 'has_searched' not in st.session_state:
        st.session_state['has_searched'] = False
    if 'selected_patient_id' not in st.session_state:
        st.session_state['selected_patient_id'] = None

    col_search, col_btn = st.columns([4, 1], gap="small")
    
    with col_search:
        s_name = st.text_input("Patient Name", value=st.session_state['search_query_name'])
    with col_btn:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        do_search = st.button("Search Records", use_container_width=True, type="primary")

    if do_search:
        st.session_state['search_query_name'] = s_name.strip()
        st.session_state['has_searched'] = True
        st.session_state['selected_patient_id'] = None
        st.rerun()

    if not st.session_state['has_searched']:
        return

    import sqlite3
    import pandas as pd
    from database import DB_FILENAME
    
    # Reload records dynamically from the database
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    c.execute(\"\"\"
        SELECT a.id, p.id as patient_id, p.name, a.assessment_date, a.risk_level, p.age, p.gender, a.overall_score,
               a.working_memory_score, a.attention_score, a.recall_score, a.speech_rate
        FROM assessments a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.assessment_date DESC
    \"\"\")
    records = c.fetchall()
    conn.close()

    target_name = st.session_state['search_query_name'].lower()
    
    # Filter by name only
    name_matched_records = []
    for r in records:
        if str(r[2]).lower() == target_name:
            name_matched_records.append(r)

    if not name_matched_records:
        st.markdown(\"\"\"
        <div style="text-align:center; padding:3rem; border:1px solid #E5ECF6; border-radius:16px; background:white; color:var(--text-secondary); margin-top:1rem; box-shadow: var(--shadow-soft);">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🔍</div>
            <p style="font-weight:700; margin:0 0 0.25rem 0; font-size:1.1rem; color: var(--dark-navy);">No matching patient found.</p>
            <p style="font-size:0.85rem; margin:0; opacity:0.8;">Ensure the Name is correct.</p>
        </div>
        \"\"\", unsafe_allow_html=True)
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
                
            st.markdown(f\"\"\"
            <div style="background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #C9D6EA; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(22, 74, 159, 0.04);">
                <div style="font-size: 1.1rem; font-weight: 700; color: #0B2A5B; margin-bottom: 8px;">{pdata['name'].title()}, {pdata['age']}, {pdata['gender']} (PAT-{pid:04d})</div>
                <div style="color: #475569; font-size: 0.9rem; margin-bottom: 12px;">Last assessment: {last_date} | Total assessments: {pdata['total']} | Latest Risk: <strong>{pdata['latest_risk']}</strong></div>
            </div>
            \"\"\", unsafe_allow_html=True)
            if st.button("Select Patient", key=f"select_pat_{pid}", type="secondary"):
                st.session_state['selected_patient_id'] = pid
                st.rerun()
        return

    # A patient is selected, filter assessments for this specific patient ID
    selected_pid = st.session_state['selected_patient_id']
    filtered_records = [r for r in records if r[1] == selected_pid]
    
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

    st.markdown(f\"\"\"
    <div style="background: #F0F8FF; padding: 24px; border-radius: 16px; margin-bottom: 24px; border: 1px solid #BAE6FD; margin-top: 16px;">
        <h3 style="color: #0369A1; margin-top: 0; margin-bottom: 16px;">Patient Summary</h3>
        <div style="display: flex; gap: 40px; flex-wrap: wrap; line-height: 1.6;">
            <div><strong>Name:</strong> {first[2].title()}</div>
            <div><strong>Age:</strong> {first[5]}</div>
            <div><strong>Gender:</strong> {first[6]}</div>
            <div><strong>Patient ID:</strong> PAT-{first[1]:04d}</div>
            <div><strong>Total Assessments:</strong> {total_assessments}</div>
            <div><strong>Latest Risk Level:</strong> {latest_risk}</div>
            <div><strong>Latest Overall Score:</strong> {latest_score}%</div>
            <div><strong>Last Assessment:</strong> {last_date}</div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

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
        
        st.markdown(f\"\"\"
        <div class="history-row">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--dark-navy);">{date_str}</div>
                <div>
                    <span style="font-weight: 700; color: {'#16A34A' if 'Low' in r_level else '#F59E0B' if 'Mod' in r_level or 'Med' in r_level else '#EF4444'}; margin-right: 12px;">{r_level}</span>
                    <span style="font-weight: 800; font-size: 1.2rem;">{o_score}%</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 16px;">
                <div><strong>Memory Recall:</strong><br>{wm_score}%</div>
                <div><strong>Object ID:</strong><br>{rec_score}%</div>
                <div><strong>Sequencing:</strong><br>{att_score}%</div>
                <div><strong>Clock Arr:</strong><br>N/A</div>
                <div><strong>Voice Analysis:</strong><br>{voice_score}%</div>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
        if st.button("View Full Report", key=f"btn_full_rep_{rid}", type="secondary"):
            st.session_state['view_history_record_id'] = rid
            st.rerun()

    # Trend Graph
    if total_assessments > 1:
        st.markdown("<h3 style='color: var(--dark-navy); margin-top: 32px; margin-bottom: 16px;'>Screening Score Trend Over Time</h3>", unsafe_allow_html=True)
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

    # Recommendation
    st.markdown("<h3 style='color: var(--dark-navy); margin-top: 32px; margin-bottom: 16px;'>Precaution / Recommendation</h3>", unsafe_allow_html=True)
    if "Low" in latest_risk:
        rec_html = "Continue regular monitoring, good sleep, exercise, social activity, and repeat screening later."
    elif "Mod" in latest_risk or "Med" in latest_risk:
        rec_html = "Monitor symptoms closely, maintain routine, encourage cognitive activities, and consider healthcare consultation if memory issues affect daily life."
    else:
        rec_html = "Recommend clinical consultation as soon as possible. Family/caregiver support and further medical evaluation are advised."

    st.markdown(f\"\"\"
    <div style="background-color: #F8FAFC; padding: 24px; border-radius: 16px; border: 1px solid #E2E8F0; color: #334155; font-size: 1.05rem; line-height: 1.6;">
        {rec_html}
    </div>
    \"\"\", unsafe_allow_html=True)
    
    st.markdown(\"\"\"
    <div style="margin-top: 32px; padding: 16px; text-align: center; color: #64748B; font-size: 0.85rem; border-top: 1px solid #E2E8F0;">
        <em>This system is only an early screening support tool. It does not diagnose dementia or replace professional medical advice.</em>
    </div>
    \"\"\", unsafe_allow_html=True)

"""

if old_patients in content:
    content = content.replace(old_patients, new_patients)
else:
    print("WARNING: Could not replace page_patients.")

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixes applied successfully to app.py")
