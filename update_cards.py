import re

filepath = 'landing/templates/landing/index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace div to be clickable
content = re.sub(
    r'(<div class="bg-\[#0a0f18\] rounded-2xl [^"]*flex flex-col [^"]*")',
    r'\1 onclick="window.location.href=\'{% url \'landing:member_detail\' member.id %}\'" style="cursor:pointer;" ',
    content
)

# Replace social links to stop propagation
content = content.replace(
    'target="_blank" rel="noopener" class="text-slate-500 hover:text-cyan-400',
    'target="_blank" rel="noopener" onclick="event.stopPropagation()" class="text-slate-500 hover:text-cyan-400'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
