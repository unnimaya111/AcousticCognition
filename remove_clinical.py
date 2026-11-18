import sys

FILE_PATH = r"c:\Users\unnim\OneDrive\Desktop\dementia_project\app.py"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "# Form to prevent early submission" in line:
        start_idx = i
    if "st.metric(\"Fluency Score\"" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx] + ["    render_cognitive_tests()\n"] + lines[end_idx+1:]
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Successfully removed clinical assessment block. Deleted lines {start_idx+1} to {end_idx+1}.")
else:
    print(f"Indices not found: start={start_idx}, end={end_idx}")
