import re

file_path = r'e:\cecp club\landing\templates\landing\register.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace provider_login_url tags with plain URLs
content = content.replace(
    "{% provider_login_url 'google' %}",
    "/accounts/google/login/?process=login"
)
content = content.replace(
    "{% provider_login_url 'github' %}",
    "/accounts/github/login/?process=login"
)
content = content.replace(
    "{% provider_login_url 'microsoft' %}",
    "/accounts/microsoft/login/?process=login"
)

# Also remove {% load socialaccount %} since we no longer need it
content = content.replace("{% load socialaccount %}\n", "")
content = content.replace("{% load socialaccount %}\r\n", "")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done - register.html fixed")
