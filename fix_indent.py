with open('landing/views.py', 'rb') as f:
    content = f.read()

import re

# We will just write a python script that fixes the specific indentation at line 301 and 302.
# Let's find the exact bad lines and replace them.
lines = content.split(b'\n')
for i, line in enumerate(lines):
    if b"project.approval_status = 'pending'" in line and b"messages.success" in lines[i+1]:
        # we found it
        lines[i] = b"                project.approval_status = 'pending'"
        lines[i+1] = b"                messages.success(request, f'Project \"{project.title}\" submitted for review!')"
        lines[i+2] = b"            project.save()"
        lines[i+3] = b"            if project.approval_status == 'pending':"
        lines.insert(i+4, b"                _notify_club_heads(project, member)")
        
        # Now remove any subsequent _notify_club_heads
        for j in range(i+5, i+15):
            if j < len(lines) and b"_notify_club_heads" in lines[j]:
                lines[j] = b""
        break

with open('landing/views.py', 'wb') as f:
    f.write(b'\n'.join(lines))
    
print("Fixed indentation!")
