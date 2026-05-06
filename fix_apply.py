import re

file_path = r'e:\cecp club\landing\templates\landing\apply.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                </div>
                    </div>"""

replacement = """                </div>
                <div class="space-y-5">
                    <div>
                        <label class="field-label" for="id_full_name">Full Name *</label>
                        {{ form.full_name }}
                        {% if form.full_name.errors %}<p class="field-error">{{ form.full_name.errors.0 }}</p>{% endif %}
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                        <div>
                            <label class="field-label" for="id_profile_photo">Professional Profile Photo (Optional)</label>
                            {{ form.profile_photo }}
                            {% if form.profile_photo.errors %}<p class="field-error">{{ form.profile_photo.errors.0 }}</p>{% endif %}
                        </div>
                        <div>
                            <label class="field-label" for="id_resume">Resume (PDF / DOC) *</label>
                            {{ form.resume }}
                            {% if form.resume.errors %}<p class="field-error">{{ form.resume.errors.0 }}</p>{% endif %}
                        </div>
                    </div>
                    <div>
                        <label class="field-label" for="id_email">College Email *</label>
                        {{ form.email }}
                        <p class="text-xs text-amber-400/70 mt-1.5" style="font-family:'JetBrains Mono',monospace;">🔒 Only @ritroorkee.com emails accepted</p>
                        {% if form.email.errors %}<p class="field-error">{{ form.email.errors.0 }}</p>{% endif %}
                    </div>"""

# Ensure line endings match
target = target.replace('\n', '\r\n')
replacement = replacement.replace('\n', '\r\n')

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Target not found!")
