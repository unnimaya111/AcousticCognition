import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update page_patients
old_patient_render = "<td style='padding: 16px; color: #475569;'>{row['gender']}</td>"
new_patient_render = "<td style='padding: 16px; color: #475569;'>{row['gender'] if str(row['gender']).strip() not in ['None', '', 'nan'] else 'Not Specified'}</td>"
content = content.replace(old_patient_render, new_patient_render)

# 2. Update page_reports
old_report_render = "<p style=\"margin:4px 0 0 0; color:#64748B; font-size:0.85rem;\">{row['age']} yrs • {row['gender']} • Assessed: {str(row['assessment_date'])[:16]}</p>"
new_report_render = "<p style=\"margin:4px 0 0 0; color:#64748B; font-size:0.85rem;\">{row['age']} yrs • {row['gender'] if str(row['gender']).strip() not in ['None', '', 'nan'] else 'Not Specified'} • Assessed: {str(row['assessment_date'])[:16]}</p>"
content = content.replace(old_report_render, new_report_render)

# 3. Update page_assessment_history
old_history_render = "<p style=\"margin: 4px 0 0 0; font-size: 0.85rem; color: var(--text-secondary);\">{age} yrs • {gender}</p>"
new_history_render = "<p style=\"margin: 4px 0 0 0; font-size: 0.85rem; color: var(--text-secondary);\">{age} yrs • {gender if str(gender).strip() not in ['None', '', 'nan'] else 'Not Specified'}</p>"
content = content.replace(old_history_render, new_history_render)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
