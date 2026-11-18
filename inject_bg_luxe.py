import os
import base64
import re

IMG_PATH = r"C:\Users\unnim\.gemini\antigravity\brain\07a6a924-3d4e-4210-8c7f-2c36f0fb0959\futuristic_brain_bg_1776276643819.png"
FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

try:
    with open(IMG_PATH, "rb") as image_file:
        img_b64 = base64.b64encode(image_file.read()).decode()
except Exception as e:
    print(f"Error reading image: {e}")
    # Fallback if the image was somehow deleted, though it shouldn't be.
    img_b64 = ""

new_css_bg = f"""    /* Global Ethereal Luxe Background */
    .stApp {{
        background: linear-gradient(rgba(11, 15, 26, 0.88), rgba(11, 15, 26, 0.88)), url('data:image/png;base64,{img_b64}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
    }}"""

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# We are searching for:
#     /* Global Ethereal Luxe Background */
#     .stApp {
#         background: #0B0F1A !important;
#         background-attachment: fixed !important;
#         font-family: 'Inter', sans-serif !important;
#         color: #e2e8f0 !important;
#     }

pattern = r"/\* Global Ethereal Luxe Background \*/\s*\.stApp \{(.*?)\}"

if re.search(pattern, content, flags=re.DOTALL):
    content = re.sub(pattern, new_css_bg, content, flags=re.DOTALL)
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected background image into app.py (Luxe Edition)!")
else:
    print("Regex match failed. CSS block not found.")
