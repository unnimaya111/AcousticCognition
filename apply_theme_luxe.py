import sys

FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

NEW_CSS = """# --- Advanced Custom Styling (Ethereal Neuro Luxe) ---
st.markdown(\"\"\"
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global Ethereal Luxe Background */
    .stApp {
        background: #0B0F1A !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
    }
    
    /* Cinematic Neural Network Glow Overlay */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(74, 144, 226, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 80% 70%, rgba(160, 132, 232, 0.15) 0%, transparent 45%);
        animation: cinematicGlow 12s ease-in-out infinite alternate;
        z-index: -1;
        pointer-events: none;
    }

    @keyframes cinematicGlow {
        0% { transform: scale(1); opacity: 0.7; }
        100% { transform: scale(1.15); opacity: 1; }
    }

    /* Typography overrides for readability in dark mode */
    p, h1, h2, h3, h4, h5, h6, span, label, li {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Global Content Width & Centering */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Force backgrounds clear */
    .main, [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Form and Main Content Micro-Interactions */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"], [data-testid="stForm"], div[data-testid="stExpander"], .vp-box {
        background: rgba(11, 15, 26, 0.4) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        padding: 28px !important;
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"]:hover, [data-testid="stForm"]:hover, div[data-testid="stExpander"]:hover {
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3), 0 0 15px rgba(74, 144, 226, 0.1) !important;
    }

    @keyframes slideUpFade {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Gradient Glowing Buttons */
    div.stButton > button, div.stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #4A90E2 0%, #A084E8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        height: 50px !important;
        padding: 0 24px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 20px rgba(74, 144, 226, 0.25) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-5px) scale(1.03) !important;
        box-shadow: 0 15px 30px rgba(160, 132, 232, 0.5), 0 0 20px rgba(74, 144, 226, 0.4) !important;
    }
    div.stButton > button:active, div.stDownloadButton > button:active, [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(2px) scale(0.97) !important;
        box-shadow: 0 5px 10px rgba(160, 132, 232, 0.3) !important;
    }

    /* Ethereal Branding Header */
    .title-container {
        text-align: center;
        margin-top: 4rem;
        width: 100%;
        animation: pulseTitle 6s infinite alternate;
    }
    
    @keyframes pulseTitle {
        0% { text-shadow: 0 0 15px rgba(255,255,255,0.05); }
        100% { text-shadow: 0 0 30px rgba(74, 144, 226, 0.3); }
    }

    .title-acoustic {
        font-size: 4.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -2px;
    }
    .title-cognition {
        font-size: 4.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #4A90E2 0%, #A084E8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
    }
    .home-subtitle {
        text-align: center !important;
        color: #94a3b8 !important;
        font-size: 1.4rem;
        margin-top: -10px;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* Luxury Value Prop Cards */
    .vp-box {
        background: rgba(11, 15, 26, 0.4) !important;
        backdrop-filter: blur(30px) !important;
        padding: 40px 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-align: left;
        height: 100%;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .vp-box:hover {
        transform: translateY(-15px);
        box-shadow: 0 25px 50px rgba(0,0,0,0.6), 0 0 30px rgba(74, 144, 226, 0.2) !important;
        border-color: rgba(160, 132, 232, 0.4) !important; /* Soft violet border on hover */
    }
    .vp-icon {
        font-size: 2.8rem;
        margin-bottom: 25px;
        display: inline-block;
        animation: floatAnimation 4s ease-in-out infinite;
        text-shadow: 0 0 20px rgba(74, 144, 226, 0.4);
    }
    .vp-title {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 15px;
        letter-spacing: -0.5px;
    }
    .vp-text {
        color: #94a3b8 !important;
        font-size: 1.05rem;
        line-height: 1.7;
        font-weight: 300;
    }

    @keyframes floatAnimation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }

    /* Audio Uploader Glass Style */
    .stFileUploader > div > div {
        background: rgba(11, 15, 26, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 3rem !important;
        transition: all 0.4s ease;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }
    .stFileUploader > div > div:hover {
        border-color: rgba(74, 144, 226, 0.5) !important;
        background: rgba(11, 15, 26, 0.6) !important;
        box-shadow: inset 0 0 30px rgba(74, 144, 226, 0.15);
    }
    .stApp .stFileUploader * { color: #ffffff !important; }

    /* Dark Mode Form Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255,255,255,0.05) !important;
        color: #ffffff !important;
        height: 50px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 0 1px #4A90E2 !important;
    }
    
    /* Metrics - Gradient Text */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #4A90E2 0%, #A084E8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-shadow: none !important; /* Remove shadow to let gradient shine */
    }

    /* Hide Unwanted internal Streamlit arrow artifacts/text or overlap elements */
    .arrow_down, .arrow, [data-testid="stMetricDelta"] svg, .stSelectbox svg {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* Explicitly restore and style the native Expander toggle chevron */
    [data-testid="stExpanderToggleIcon"] {
        display: inline-block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        width: auto !important;
        color: #002B5C !important;
    }


    </style>
\"\"\", unsafe_allow_html=True)"""

def apply_theme():
    # Read the current content
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {FILE_PATH}: {e}")
        sys.exit(1)

    start_idx = -1
    end_idx = -1
    
    # We are looking for the start which was either "Advanced Custom Styling (Neuro Calm)" or whatever the header is.
    # The safest way is to find '# --- Advanced Custom Styling' and the next '\"\"\", unsafe_allow_html=True)'
    
    for i, line in enumerate(lines):
        if "# --- Advanced Custom Styling" in line:
            start_idx = i
            break
            
    if start_idx != -1:
        for i in range(start_idx, len(lines)):
            if '""", unsafe_allow_html=True)' in line or 'unsafe_allow_html=True)' in lines[i]:
                end_idx = i
                break

    if start_idx == -1 or end_idx == -1:
        print(f"Could not find existing CSS block bounds. start: {start_idx}, end: {end_idx}")
        # Append as a fallback before page routing if it fails? No, better to view file and fix
        sys.exit(1)

    # Reconstruct the file with the new CSS
    new_lines = lines[:start_idx] + [NEW_CSS + "\n"] + lines[end_idx+1:]
    
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Successfully applied Ethereal Neuro Luxe theme!")
    except Exception as e:
        print(f"Error writing to file {FILE_PATH}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_theme()
