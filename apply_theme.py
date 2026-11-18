import os

FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_css = """# --- Advanced Custom Styling (Neuro Calm) ---
st.markdown(\"\"\"
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

    /* Global Overrides */
    .stApp {
        background: linear-gradient(135deg, #4A90E2 0%, #A084E8 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Simulate Particle Network Background */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
        animation: pulseBg 10s ease-in-out infinite alternate;
        z-index: -1;
        pointer-events: none;
    }

    @keyframes pulseBg {
        0% { transform: scale(1); opacity: 0.8; }
        100% { transform: scale(1.1); opacity: 1; }
    }

    /* Force text colors to be readable over the dark gradient */
    p, h1, h2, h3, h4, h5, h6, span, label, li {
        color: #f8fafc !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Global Content Width & Centering */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .main, [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Glassmorphism Containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"], [data-testid="stForm"], div[data-testid="stExpander"], .vp-box {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        padding: 28px !important;
        animation: slideUpFade 0.6s ease-out forwards;
    }

    @keyframes slideUpFade {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Buttons - Mint Green Accent (#A8E6CF) */
    div.stButton > button, div.stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
        background: #A8E6CF !important;
        color: #1a202c !important;
        border: none !important;
        height: 50px !important;
        padding: 0 24px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 20px rgba(168, 230, 207, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 25px rgba(168, 230, 207, 0.5), 0 0 15px rgba(168, 230, 207, 0.4) !important;
        background: #88d4b8 !important;
    }

    /* Title Animations & Branding */
    .title-container {
        text-align: center;
        margin-top: 3rem;
        width: 100%;
        animation: pulseTitle 4s infinite alternate;
    }
    
    @keyframes pulseTitle {
        0% { text-shadow: 0 0 10px rgba(255,255,255,0.1); }
        100% { text-shadow: 0 0 30px rgba(255,255,255,0.5), 0 0 10px rgba(168, 230, 207, 0.6); }
    }

    .title-acoustic {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        letter-spacing: -2px;
    }
    .title-cognition {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        color: #A8E6CF !important; /* Mint */
        letter-spacing: -2px;
    }
    .home-subtitle {
        text-align: center !important;
        color: #e2e8f0 !important;
        font-size: 1.4rem;
        margin-top: -10px;
        font-weight: 300;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Value Prop Cards Hover Details */
    .vp-box {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
        padding: 35px 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: left;
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .vp-box:hover {
        transform: translateY(-12px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2), 0 0 20px rgba(168, 230, 207, 0.4);
        border-color: #A8E6CF !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    .vp-icon {
        font-size: 2.5rem;
        margin-bottom: 20px;
        display: inline-block;
        animation: floatAnimation 4s ease-in-out infinite;
        text-shadow: 0 0 15px rgba(255,255,255,0.4);
    }
    .vp-title {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 1.4rem;
        margin-bottom: 15px;
    }
    .vp-text {
        color: #cbd5e1 !important;
        font-size: 1rem;
        line-height: 1.7;
        font-weight: 300;
    }

    @keyframes floatAnimation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    /* Audio Uploader Glass Style */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        transition: all 0.3s ease;
    }
    .stFileUploader > div > div:hover {
        border-color: #A8E6CF !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    .stApp .stFileUploader * { color: #ffffff !important; }

    /* Fix Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255,255,255,0.8) !important;
        color: #1e293b !important;
        height: 50px !important;
        border-radius: 12px !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #A8E6CF !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
    }

    </style>
\"\"\", unsafe_allow_html=True)
"""

# Re-assemble the file
# 1. Keep lines 0 to 47
part1 = lines[:48]

# 2. Add new CSS
part2 = [new_css]

# 3. Skip the old CSS. The old CSS ends at Line 262 ("</style>\n", "\"\"\", unsafe_allow_html=True)\n")
# Find line index where page routing starts
routing_start = 0
for i, line in enumerate(lines):
    if "# --- Page Routing ---" in line:
        routing_start = i
        break

# 4. Modify the rest of the file directly
rest_of_file = "".join(lines[routing_start:])

# Fix VP Box HTML
rest_of_file = rest_of_file.replace(
    "<h3 style='text-align: center; font-size: 2rem; font-weight: 800; color: #0f172a; margin-bottom: 2rem;'>Enterprise-Grade Assessment</h3>",
    "<h3 style='text-align: center; font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem; text-shadow: 0 4px 15px rgba(0,0,0,0.2);'>Enterprise-Grade Assessment</h3>"
)

rest_of_file = rest_of_file.replace(
    '<div class="vp-box" style="background-color: #f0fdf4; border: 1px solid #bbf7d0;">',
    '<div class="vp-box">'
)
rest_of_file = rest_of_file.replace(
    '<div class="vp-box" style="background-color: #eff6ff; border: 1px solid #bfdbfe;">',
    '<div class="vp-box">'
)
rest_of_file = rest_of_file.replace(
    '<div class="vp-box" style="background-color: #fdf4ff; border: 1px solid #fbcfe8;">',
    '<div class="vp-box">'
)

# Fix Auth Text Colors
rest_of_file = rest_of_file.replace(
    "color: #004d40;",
    "color: #A8E6CF; text-shadow: 0 2px 10px rgba(0,0,0,0.2);"
)
rest_of_file = rest_of_file.replace(
    "color: #64748b;",
    "color: #e2e8f0;"
)
rest_of_file = rest_of_file.replace(
    "border-left: 1px solid #cbd5e1;",
    "border-left: 1px solid #ffffff;"
)

# Dark Text on login box
rest_of_file = rest_of_file.replace(
    "<h3 style='text-align: center; color: #A8E6CF; text-shadow: 0 2px 10px rgba(0,0,0,0.2);'>Clinician Access</h3>",
    "<h3 style='text-align: center; color: #ffffff;'>Clinician Access</h3>"
)

# Dark Text on main titles
rest_of_file = rest_of_file.replace(
    "<h1 style='text-align: center;'>🧠 The Screening Tool</h1>",
    "<h1 style='text-align: center; text-shadow: 0 4px 15px rgba(0,0,0,0.2);'>🧠 The Screening Tool</h1>"
)

# Dark Text on Feedback White Box
rest_of_file = rest_of_file.replace(
    "<div style='background: white; padding: 40px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-top: 20px;'>",
    "<div style='background: rgba(255,255,255,0.1); backdrop-filter: blur(12px); padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px 0 rgba(31,38,135,0.15); margin-top: 20px;'>"
)


final_content = "".join(part1) + part2[0] + "\n" + rest_of_file

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(final_content)
    
print("Successfully applied Neuro Calm theme!")
