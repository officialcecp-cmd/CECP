with open('landing/templates/landing/moderator_dashboard.html', 'rb') as f:
    content = f.read().decode('latin-1')

lines = content.split('\n')
for i, line in enumerate(lines):
    kw = ['pending_project', 'section-project', 'for proj', 'proj.', 'approve_project', 'reject_project']
    if any(k in line for k in kw):
        print(f"{i+1}: {line.rstrip()}")
