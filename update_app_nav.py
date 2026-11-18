import sys

FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

NEW_NAV = """# --- Page Routing ---

# Wrap the navigation menu in a container and inject CSS to make it sticky
st.markdown(\"\"\"
<style>
    /* Make the block container hold the sticky nav properly */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) {
        position: sticky !important;
        top: 0px !important;
        z-index: 99999 !important;
    }
</style>
\"\"\", unsafe_allow_html=True)

if st.session_state.get('logged_in') and st.session_state.get('page') not in ['home', 'auth']:
    
    # Determine default index
    default_idx = 1
    if st.session_state['page'] == 'home': default_idx = 0
    elif st.session_state['page'] == 'main': default_idx = 1
    elif st.session_state['page'] == 'analytics': default_idx = 2
    elif st.session_state['page'] == 'feedback': default_idx = 3
        
    selected = option_menu(
        menu_title=None,
        options=["Home", "Cognitive Test", "Analytics", "Feedback", "Logout"],
        icons=["house", "puzzle", "graph-up", "chat-square-text", "box-arrow-right"],
        menu_icon="cast",
        default_index=default_idx,
        orientation="horizontal",
        styles={
            "container": {
                "background": "rgba(11, 15, 26, 0.4)", 
                "backdrop-filter": "blur(30px)", 
                "-webkit-backdrop-filter": "blur(30px)",
                "border-radius": "20px", 
                "border": "1px solid rgba(255, 255, 255, 0.05)", 
                "padding": "0!important",
                "box-shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                "margin-top": "10px"
            },
            "icon": {"color": "#e2e8f0", "font-size": "16px"}, 
            "nav-link": {
                "font-size": "14px", 
                "text-align": "center", 
                "margin": "0px 5px", 
                "--hover-color": "rgba(74, 144, 226, 0.15)", 
                "color": "#94a3b8", 
                "font-family": "Inter",
                "transition": "all 0.3s ease",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4A90E2 0%, #A084E8 100%)", 
                "color": "#ffffff", 
                "font-weight": "600",
                "box-shadow": "0 4px 15px rgba(160, 132, 232, 0.4)",
                "transform": "scale(1.05)"
            },
        }
    )
    
    if selected == "Home":
        st.session_state['page'] = 'home'
        st.rerun()
    elif selected == "Cognitive Test" and st.session_state['page'] != 'main':
        st.session_state['page'] = 'main'
        st.rerun()
    elif selected == "Analytics" and st.session_state['page'] != 'analytics':
        st.session_state['page'] = 'analytics'
        st.rerun()
    elif selected == "Feedback" and st.session_state['page'] != 'feedback':
        st.session_state['page'] = 'feedback'
        st.rerun()
    elif selected == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['page'] = 'home'
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
"""

try:
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of # --- Page Routing ---
    start_str = "# --- Page Routing ---"
    # Find the end which is the next st.markdown("<br>", unsafe_allow_html=True) AFTER the big if-else block
    # We'll just replace the whole chunk:
    
    lines = content.split('\\n')
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith("# --- Page Routing ---"):
            start_idx = i
        # find where it ends (before "if st.session_state['page'] == 'home':")
        if start_idx != -1 and i > start_idx + 10 and line.startswith("if st.session_state['page'] == 'home':"):
            end_idx = i - 2 # go back above new line
            break
            
    if start_idx != -1 and end_idx != -1:
        new_lines = lines[:start_idx] + NEW_NAV.split('\\n') + lines[end_idx+1:]
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(new_lines))
        print("Successfully updated app.py Page Routing!")
    else:
        print(f"Could not find replacement boundaries in app.py. Start: {start_idx}, End: {end_idx}")
        
except Exception as e:
    print(f"Error modifying app.py: {e}")
