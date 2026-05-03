import re

with open('landing/views.py', 'rb') as f:
    content = f.read()

old_block = b'''                project.approval_status = 'pending'
                messages.success(request, f\\'Project "{project.title}" submitted for review!\\')
                _notify_club_heads(project, member)
            project.save()'''

# Fix for bytes string literal mismatch
old_block_actual = b'''                project.approval_status = 'pending'
                messages.success(request, f'Project "{project.title}" submitted for review!')
                _notify_club_heads(project, member)
            project.save()'''

new_block_actual = b'''                project.approval_status = 'pending'
                messages.success(request, f'Project "{project.title}" submitted for review!')
            project.save()
            if project.approval_status == 'pending':
                _notify_club_heads(project, member)'''

if old_block_actual in content:
    content = content.replace(old_block_actual, new_block_actual)
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("Could not find block. Trying regex.")
    
    # regex approach to find the exact code
    pattern = re.compile(b"project\\.approval_status = 'pending'.*?messages\\.success\\(request, f'Project \"\\{project\\.title\\}\" submitted for review!'\\).*?_notify_club_heads\\(project, member\\).*?project\\.save\\(\\)", re.DOTALL)
    
    match = pattern.search(content)
    if match:
        new_content = b'''                project.approval_status = 'pending'
                messages.success(request, f'Project "{project.title}" submitted for review!')
            project.save()
            _notify_club_heads(project, member)'''
        content = content[:match.start()] + new_content + content[match.end():]
        with open('landing/views.py', 'wb') as f:
            f.write(content)
        print("Patched via regex successfully!")
    else:
        print("Could not find via regex either. Let's dump the context.")
