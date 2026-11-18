import re

app_file = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# --- FIX 1: Patient Summary text visibility ---
old_summary = """    <div style="background: #F0F8FF; padding: 24px; border-radius: 16px; margin-bottom: 24px; border: 1px solid #BAE6FD; margin-top: 16px;">
        <h3 style="color: #0369A1; margin-top: 0; margin-bottom: 16px;">Patient Summary</h3>"""

new_summary = """    <div class="patient-summary-card" style="background: #F0F8FF; padding: 24px; border-radius: 16px; margin-bottom: 24px; border: 1px solid #BAE6FD; margin-top: 16px;">
        <h3 style="color: #0B2A5B; margin-top: 0; margin-bottom: 16px; font-weight: 900;">Patient Summary</h3>"""

if old_summary in content:
    content = content.replace(old_summary, new_summary)
else:
    print("WARNING: Could not find old_summary block.")

# --- FIX 2: Assessment Guide router to allow assessment_guide explicitly ---
# In page dispatcher
old_router = "elif st.session_state['page'] == 'Guide':"
new_router = "elif st.session_state['page'] in ['Guide', 'assessment_guide']:"

if old_router in content:
    content = content.replace(old_router, new_router)
else:
    print("WARNING: Could not find router block.")

old_sidebar_guide = "type=\"primary\" if st.session_state['page'] == 'Guide' else \"secondary\"):"
new_sidebar_guide = "type=\"primary\" if st.session_state['page'] in ['Guide', 'assessment_guide'] else \"secondary\"):"

if old_sidebar_guide in content:
    content = content.replace(old_sidebar_guide, new_sidebar_guide)
else:
    print("WARNING: Could not find sidebar guide block.")

# Update the buttons in page_assessment_guide
# We will use regex to find the button click block and update it
btn_pattern = r'if st\.button\(btn_label, key=b_key, type="secondary", use_container_width=True\):\s*st\.session_state\[s_key\] = not st\.session_state\.get\(s_key, False\)\s*st\.session_state\.page = "Guide"\s*st\.rerun\(\)'

def replace_btn(m):
    return """if st.button(btn_label, key=b_key, type="secondary", use_container_width=True):
                st.session_state[s_key] = not st.session_state.get(s_key, False)
                st.session_state.page = "assessment_guide"
                st.rerun()"""

content = re.sub(btn_pattern, replace_btn, content)

# Update criteria rendering
old_criteria = """        if st.session_state.get(s_key, False):
            st.markdown(f\"\"\"
            <div style="background: #FFFFFF; border: 1px solid #C9D6EA; border-radius: 18px; padding: 22px; color: #334155; font-size: 17px; line-height: 1.7; box-shadow: 0 8px 24px rgba(22, 74, 159, 0.06); margin-top: -8px; margin-bottom: 24px;">
                {item['criteria']}
            </div>
            \"\"\", unsafe_allow_html=True)"""

new_criteria = """        if st.session_state.get(s_key, False):
            st.markdown(f\"\"\"
            <div class="criteria-box">
                <h4>Scoring Criteria</h4>
                <div class="criteria-content">{item['criteria']}</div>
            </div>
            \"\"\", unsafe_allow_html=True)"""

if old_criteria in content:
    content = content.replace(old_criteria, new_criteria)
else:
    print("WARNING: Could not find criteria block.")

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)


# --- Add CSS to elite_style.css ---
css_file = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\elite_style.css"
with open(css_file, "a", encoding="utf-8") as f:
    f.write('''

/* BUG 1: Patient Summary Fix */
.patient-summary-card,
.patient-summary-card * {
    color: #1E293B !important;
}

.patient-summary-card h3 {
    color: #0B2A5B !important;
    font-weight: 900 !important;
}

.patient-summary-card strong {
    color: #0B2A5B !important;
}

/* BUG 2: Assessment Guide Criteria Box Fix */
.criteria-box {
    background: #FFFFFF !important;
    border: 1px solid #C9D6EA !important;
    border-radius: 18px !important;
    padding: 22px !important;
    margin: 16px 0 28px 0 !important;
    color: #1E293B !important;
    font-size: 17px !important;
    line-height: 1.7 !important;
    box-shadow: 0 8px 24px rgba(22, 74, 159, 0.06) !important;
}

.criteria-box * {
    color: #1E293B !important;
}

.criteria-box h4 {
    color: #0B2A5B !important;
    font-weight: 900 !important;
    margin-top: 0 !important;
    margin-bottom: 12px !important;
}
''')

print("Fixes applied successfully.")
