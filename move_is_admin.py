with open('landing/views.py', 'rb') as f:
    content = f.read()

# 1. Remove the duplicate import and is_admin definition from line ~682
old_block = b"""from django.contrib.auth.decorators import user_passes_test\r\n\r\ndef is_admin(user):\r\n    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())\r\n\r\n"""
new_block = b""  # remove it from the middle

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Removed mid-file is_admin block OK")
else:
    print("WARNING: mid-file block not found exactly - trying alternate")
    # Try without \r
    old_block2 = b"from django.contrib.auth.decorators import user_passes_test\n\ndef is_admin(user):\n    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())\n\n"
    if old_block2 in content:
        content = content.replace(old_block2, b"")
        print("Removed mid-file is_admin block (LF variant) OK")

# 2. Add is_admin right after the imports block (after line 20 roughly)
# Find the insertion point: right after the last import line in the top block
# We'll insert after "from .services import categorize_project_level"
insertion_marker = b"from .services import categorize_project_level\r\n"
insertion_marker_lf = b"from .services import categorize_project_level\n"

is_admin_block = b"\r\n\r\ndef is_admin(user):\r\n    \"\"\"Returns True if user is a superuser or in CECP_Admins group.\"\"\"\r\n    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())\r\n"

if insertion_marker in content:
    content = content.replace(insertion_marker, insertion_marker + is_admin_block, 1)
    print("Inserted is_admin after imports OK")
elif insertion_marker_lf in content:
    is_admin_block_lf = b"\n\n\ndef is_admin(user):\n    \"\"\"Returns True if user is a superuser or in CECP_Admins group.\"\"\"\n    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())\n"
    content = content.replace(insertion_marker_lf, insertion_marker_lf + is_admin_block_lf, 1)
    print("Inserted is_admin after imports (LF) OK")
else:
    print("WARNING: insertion marker not found!")

with open('landing/views.py', 'wb') as f:
    f.write(content)
print("Done!")
