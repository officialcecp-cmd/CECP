import re

file_path = r'e:\cecp club\landing\templates\landing\review_application.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modify "Identity & Contact" card to add profile photo
identity_old = '''            <div class="admin-card p-6 rounded-xl border border-slate-700/50">
                <h2 class="text-lg font-semibold text-cyan-400 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                    Identity & Contact
                </h2>
                <div class="space-y-3">'''

identity_new = '''            <div class="admin-card p-6 rounded-xl border border-slate-700/50">
                <h2 class="text-lg font-semibold text-cyan-400 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                    Identity & Contact
                </h2>
                <div class="flex gap-5 items-start">
                    {% if app.profile_photo %}
                    <div class="flex-shrink-0">
                        <img src="{{ app.profile_photo.url }}" alt="Photo" class="w-24 h-24 rounded-xl object-cover border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                        <a href="{{ app.profile_photo.url }}" target="_blank" class="block text-center mt-2 text-xs text-cyan-400 hover:text-cyan-300">View Full</a>
                    </div>
                    {% endif %}
                    <div class="space-y-3 flex-1">'''

# Ensure line endings match
identity_old = identity_old.replace('\n', '\r\n')
identity_new = identity_new.replace('\n', '\r\n')

if identity_old in content:
    content = content.replace(identity_old, identity_new)
    # Don't forget to close the extra div
    content = content.replace(
'''                    <div>
                        <span class="text-xs text-slate-500 uppercase font-bold tracking-wider">Roll Number</span>
                        <p class="text-sm text-slate-300">{{ app.roll_number }}</p>
                    </div>
                </div>
            </div>'''.replace('\n', '\r\n'),
'''                    <div>
                        <span class="text-xs text-slate-500 uppercase font-bold tracking-wider">Roll Number</span>
                        <p class="text-sm text-slate-300">{{ app.roll_number }}</p>
                    </div>
                    </div>
                </div>
            </div>'''.replace('\n', '\r\n')
    )
else:
    print("identity_old not found!")


# 2. Modify Motivation & Links to add Resume and rename
motivation_old = '''                <h2 class="text-lg font-semibold text-amber-400 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    Motivation & Links
                </h2>'''

motivation_new = '''                <h2 class="text-lg font-semibold text-amber-400 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    Motivation, Links & Attachments
                </h2>'''

motivation_old = motivation_old.replace('\n', '\r\n')
motivation_new = motivation_new.replace('\n', '\r\n')

content = content.replace(motivation_old, motivation_new)

links_old = '''                        <a href="{{ app.linkedin_url }}" target="_blank" class="text-cyan-400 hover:text-cyan-300 text-sm font-medium flex items-center gap-1">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.475-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            LinkedIn
                        </a>
                        {% endif %}'''

links_new = '''                        <a href="{{ app.linkedin_url }}" target="_blank" class="text-cyan-400 hover:text-cyan-300 text-sm font-medium flex items-center gap-1">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.475-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            LinkedIn
                        </a>
                        {% endif %}
                        {% if app.resume %}
                        <a href="{{ app.resume.url }}" target="_blank" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-1 border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 rounded-full">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            View Resume
                        </a>
                        {% endif %}'''

links_old = links_old.replace('\n', '\r\n')
links_new = links_new.replace('\n', '\r\n')

if links_old in content:
    content = content.replace(links_old, links_new)
else:
    print("links_old not found!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
