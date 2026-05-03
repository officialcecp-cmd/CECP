import re

with open('landing/models.py', 'r', encoding='latin-1') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'class Project(models.Model):' in line:
        print(f"Found at line {i+1}")
        break
