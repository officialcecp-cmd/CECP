with open('landing/models.py', 'rb') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if b'class Project(models.Model):' in line:
        new_lines.append(b'    is_approved = models.BooleanField(default=False)\n')

with open('landing/models.py', 'wb') as f:
    f.writelines(new_lines)

print("Injected is_approved into Project model.")
