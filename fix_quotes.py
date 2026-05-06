import os

path = 's:/CECP/landing/templates/landing/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

bad_str = r"\'{% url \'landing:member_detail\' member.id %}\'"
good_str = "'{% url 'landing:member_detail' member.id %}'"
fixed_content = content.replace(bad_str, good_str)

with open(path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('Fixed quotes in index.html')
