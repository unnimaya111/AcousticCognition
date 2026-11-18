import sys

FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

NEW_NAV = """# --- Page Routing ---

if st.session_state.get('logged_in') and st.session_state.get('page') not in ['home', 'auth']:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Determine default index
    default_idx = 0
    if st.session_state['page'] == 'analytics': default_idx = 1
    elif st.session_state['page'] == 'feedback': default_idx = 2
        
    selected = option_menu(
        menu_title=None,
        options=["Cognitive Test", "Analytics", "Feedback", "Logout"],
        icons=["puzzle", "graph-up", "chat-square-text", "box-arrow-right"],
        menu_icon="cast",
        default_index=default_idx,
        orientation="horizontal",
        styles={
            "container": {"background-color": "rgba(11, 15, 26, 0.6)", "backdrop-filter": "blur(20px)", "border-radius": "15px", "border": "1px solid rgba(255, 255, 255, 0.08)", "padding": "0!important"},
            "icon": {"color": "#e2e8f0", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "rgba(74, 144, 226, 0.3)", "color": "#e2e8f0", "font-family": "Inter"},
            "nav-link-selected": {"background-color": "transparent", "background": "linear-gradient(135deg, #4A90E2 0%, #A084E8 100%)", "color": "white", "font-weight": "600"},
        }
    )
    
    if selected == "Cognitive Test" and st.session_state['page'] != 'main':
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

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace the '# --- Page Routing ---' with our new nav
content = content.replace("# --- Page Routing ---", NEW_NAV)

# 2. To remove the redundant logout button and title in main:
old_main_header = """    col_empty, col_title, col_logout = st.columns([1, 4, 1])
    with col_title:
        st.markdown("<h1 style='text-align: center; text-shadow: 0 4px 15px rgba(0,0,0,0.2);'>🧠 The Screening Tool</h1>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_main_card", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_id'] = None
            st.session_state['page'] = 'home'
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)"""

content = content.replace(old_main_header, "    # Navigation is now handled by the top-level option_menu component.")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied Ethereal Neuro Luxe styled navigation bar!")
