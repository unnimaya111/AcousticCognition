import os
import base64

IMG_PATH = r"C:\Users\unnim\.gemini\antigravity\brain\07a6a924-3d4e-4210-8c7f-2c36f0fb0959\futuristic_brain_bg_1776276643819.png"
FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

# Read Image as base64
with open(IMG_PATH, "rb") as image_file:
    img_b64 = base64.b64encode(image_file.read()).decode()

new_css_bg = f"""    /* Global Overrides */
    .stApp {{
        background: linear-gradient(rgba(74, 144, 226, 0.85), rgba(160, 132, 232, 0.85)), url('data:image/png;base64,{img_b64}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Poppins', sans-serif !important;
    }}"""

# We are going to replace this block:
#     /* Global Overrides */
#     .stApp {
#         background: linear-gradient(135deg, #4A90E2 0%, #A084E8 100%) !important;
#         background-attachment: fixed !important;
#         font-family: 'Poppins', sans-serif !important;
#     }

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Match the old block using regex
pattern = r"/\* Global Overrides \*/\s*\.stApp \{(.*?)\}"
content = re.sub(pattern, new_css_bg, content, flags=re.DOTALL)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected background image into app.py!")
