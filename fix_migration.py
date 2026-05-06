import os

path = 's:/CECP/landing/migrations/0028_delete_event_remove_initiative_action_text_and_more.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

bad_str = """        migrations.DeleteModel(
            name='Event',
        ),
"""

content = content.replace(bad_str, "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Delete the bad merge migration
if os.path.exists('s:/CECP/landing/migrations/0029_merge_20260507_0309.py'):
    os.remove('s:/CECP/landing/migrations/0029_merge_20260507_0309.py')
if os.path.exists('s:/CECP/landing/migrations/0028_remove_initiative_action_text_and_more.py'):
    os.remove('s:/CECP/landing/migrations/0028_remove_initiative_action_text_and_more.py')
if os.path.exists('s:/CECP/landing/migrations/0027_merge_20260507_0148.py'):
    os.remove('s:/CECP/landing/migrations/0027_merge_20260507_0148.py')
    
print("Fixed migrations")
