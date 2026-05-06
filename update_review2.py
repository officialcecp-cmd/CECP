import re

file_path = r'e:\cecp club\landing\templates\landing\review_application.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modify "Identity & Contact" card to add profile photo
identity_pattern = re.compile(
    r'(Identity & Contact\s*</h2>\s*)<div class="space-y-3">',
    re.DOTALL
)
identity_replacement = r'''\1<div class="flex gap-5 items-start">
                    {% if app.profile_photo %}
                    <div class="flex-shrink-0">
                        <img src="{{ app.profile_photo.url }}" alt="Photo" class="w-24 h-24 rounded-xl object-cover border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                        <a href="{{ app.profile_photo.url }}" target="_blank" class="block text-center mt-2 text-xs text-cyan-400 hover:text-cyan-300">View Full</a>
                    </div>
                    {% endif %}
                    <div class="space-y-3 flex-1">'''

content = identity_pattern.sub(identity_replacement, content)

# Also fix the closing div for identity card
roll_number_pattern = re.compile(
    r'(Roll Number</span>\s*<p class="text-sm text-slate-300">{{ app\.roll_number }}</p>\s*</div>\s*</div>\s*</div>)',
    re.DOTALL
)
roll_number_replacement = r'\1\n            </div>'

if '{% if app.profile_photo %}' in content:
    # Need to add an extra closing div since we wrapped the inner fields in another div
    content = content.replace(
        '''                    <div>\n                        <span class="text-xs text-slate-500 uppercase font-bold tracking-wider">Roll Number</span>\n                        <p class="text-sm text-slate-300">{{ app.roll_number }}</p>\n                    </div>\n                </div>\n            </div>''',
        '''                    <div>\n                        <span class="text-xs text-slate-500 uppercase font-bold tracking-wider">Roll Number</span>\n                        <p class="text-sm text-slate-300">{{ app.roll_number }}</p>\n                    </div>\n                    </div>\n                </div>\n            </div>'''
    )

# 2. Modify Motivation & Links
motivation_pattern = re.compile(r'Motivation & Links')
content = motivation_pattern.sub('Motivation, Links & Attachments', content)

# Add Resume
resume_pattern = re.compile(
    r'(LinkedIn\s*</a>\s*{% endif %})',
    re.DOTALL
)
resume_replacement = r'''\1
                        {% if app.resume %}
                        <a href="{{ app.resume.url }}" target="_blank" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-1 border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 rounded-full">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            View Resume
                        </a>
                        {% endif %}'''

content = resume_pattern.sub(resume_replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
