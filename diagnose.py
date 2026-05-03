with open('landing/views.py', 'rb') as f:
    content = f.read().decode('latin-1')

with open('landing/models.py', 'rb') as f:
    models_content = f.read().decode('latin-1')

# Find moderator_dashboard function
import re
# Extract lines around moderator_dashboard
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'moderator_dashboard' in line or 'pending_project' in line:
        print(f"views.py:{i+1}: {line.rstrip()}")

print("\n--- models.py relevant ---")
mlines = models_content.split('\n')
for i, line in enumerate(mlines):
    if 'is_approved' in line or 'approval_status' in line:
        print(f"models.py:{i+1}: {line.rstrip()}")
