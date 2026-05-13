import os

file_path = r'd:\All Code\CECP\landing\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change defaults from 0 to 999 for display_order in Project, ProjectCategory, Initiative
content = content.replace('class ProjectCategory(models.Model):', '###CAT###')
content = content.replace('class Project(models.Model):', '###PROJ###')
content = content.replace('class Initiative(models.Model):', '###INIT###')

# We need to be careful with replaces.
# For ProjectCategory
if '###CAT###' in content:
    # find next display_order = models.PositiveIntegerField(default=0)
    # This is a bit risky if there are others.
    pass

# Let's use a more robust way.
lines = content.splitlines()
new_lines = []
current_class = None
for line in lines:
    if 'class ProjectCategory(models.Model):' in line: current_class = 'CAT'
    elif 'class Project(models.Model):' in line: current_class = 'PROJ'
    elif 'class Initiative(models.Model):' in line: current_class = 'INIT'
    elif 'class ' in line: current_class = None
    
    if current_class in ['CAT', 'PROJ', 'INIT'] and 'display_order = models.PositiveIntegerField(default=0)' in line:
        line = line.replace('default=0', 'default=999')
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')

print("Successfully updated defaults to 999.")
