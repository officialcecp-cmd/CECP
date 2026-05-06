import re

file_path = r'e:\cecp club\landing\templates\landing\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Advisors linkedin
content = content.replace(
    '{% if member.linkedin_url %}\n                                        <a href=\"{{ member.linkedin_url }}\"',
    '{% if member.user.profile.linkedin_profile or member.linkedin_url %}\n                                        <a href=\"{{ member.user.profile.linkedin_profile|default:member.linkedin_url }}\"'
)

# Replace Others github
content = content.replace(
    '{% if member.github_url %}\n                                    <a href=\"{{ member.github_url }}\"',
    '{% if member.user.profile.github_profile or member.github_url %}\n                                    <a href=\"{{ member.user.profile.github_profile|default:member.github_url }}\"'
)

# Replace Others linkedin
content = content.replace(
    '{% if member.linkedin_url %}\n                                    <a href=\"{{ member.linkedin_url }}\"',
    '{% if member.user.profile.linkedin_profile or member.linkedin_url %}\n                                    <a href=\"{{ member.user.profile.linkedin_profile|default:member.linkedin_url }}\"'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
