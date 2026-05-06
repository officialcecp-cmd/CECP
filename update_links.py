import sys

file_path = r'e:\cecp club\landing\templates\landing\team.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Github links
content = content.replace('{% if member.github_url %}\n                        <a href="{{ member.github_url }}"', '{% if member.github_url or member.user.profile.github_profile %}\n                        <a href="{{ member.user.profile.github_profile|default:member.github_url }}"')

# Replace Linkedin links
content = content.replace('{% if member.linkedin_url %}\n                        <a href="{{ member.linkedin_url }}"', '{% if member.linkedin_url or member.user.profile.linkedin_profile %}\n                        <a href="{{ member.user.profile.linkedin_profile|default:member.linkedin_url }}"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
