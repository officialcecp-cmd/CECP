import re

with open('landing/templates/landing/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# For mobile menu
content = content.replace(
    'onclick="switchTab(\'events\')">Events</a>',
    'onclick="switchTab(\'events\')">Events</a>\n        {% if is_faculty_application_open %}\n        <a href="{% url \'landing:apply_faculty\' %}" class="nav-link text-xl text-cyan-400">Faculty Join</a>\n        {% endif %}'
)

with open('landing/templates/landing/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
