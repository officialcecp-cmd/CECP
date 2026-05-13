import os

file_path = r'd:\All Code\CECP\landing\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for i in range(len(lines)):
    if 'class Project(models.Model):' in lines[i]:
        for j in range(i+1, len(lines)):
            if 'class Meta:' in lines[j]:
                if "ordering = ['-created_at']" in lines[j+1]:
                    lines[j+1] = lines[j+1].replace("['-created_at']", "['display_order', '-created_at']")
                    found = True
                    break
        if found:
            break

if found:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully updated Project ordering.")
else:
    print("Could not find Project ordering.")
