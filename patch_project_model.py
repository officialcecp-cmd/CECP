import re

with open('landing/models.py', 'rb') as f:
    content = f.read()

# find "class Project(models.Model):" and insert the new field
if b'class Project(models.Model):' in content and b'is_approved = models.BooleanField(default=False)' not in content:
    new_class_def = b'''class Project(models.Model):
    is_approved = models.BooleanField(default=False)'''
    content = content.replace(b'class Project(models.Model):', new_class_def)
    
    with open('landing/models.py', 'wb') as f:
        f.write(content)
    print("Project model patched successfully!")
else:
    print("Already patched or could not find Project class.")
