with open('landing/views.py', 'rb') as f:
    content = f.read()

lines = content.split(b'\n')
for i, line in enumerate(lines):
    if b'def approve_project' in line or b'def reject_project' in line or b'approval_status' in line:
        print(f"{i+1}: {line.decode('latin-1').rstrip()}")
