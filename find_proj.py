import re

with open('landing/models.py', 'rb') as f:
    content = f.read()

# try to find 'class Project'
lines = content.split(b'\n')
for i, line in enumerate(lines):
    if b'class Project' in line:
        print(f"Line {i+1}: {line}")
