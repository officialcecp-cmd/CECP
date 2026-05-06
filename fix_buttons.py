import re

with open('s:/CECP/landing/templates/landing/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Define the new buttons HTML
new_buttons_html = """                        <div class="flex flex-wrap gap-2 w-full lg:w-auto">
                            <button class="px-4 py-2 rounded-lg bg-slate-800 text-white border border-slate-600 text-sm font-medium flex items-center gap-2 transition-colors event-filter-btn" onclick="filterEvents('all', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                                All Events
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2 event-filter-btn" onclick="filterEvents('Hackathon', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                                Hackathons
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2 event-filter-btn" onclick="filterEvents('Workshop', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                                Workshops
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2 event-filter-btn" onclick="filterEvents('Talk', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                                Talks
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2 event-filter-btn" onclick="filterEvents('status:Ongoing', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                Ongoing
                            </button>
                            <button class="px-4 py-2 rounded-lg bg-transparent text-slate-400 border border-transparent hover:bg-slate-800/50 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-2 event-filter-btn" onclick="filterEvents('status:Completed', this)">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                Past Events
                            </button>
                        </div>"""

# Find the start and end of the div
start_marker = '<div class="flex flex-wrap gap-2 w-full lg:w-auto">'
end_marker = '</div>\n                        <div class="relative w-full lg:w-72 flex-shrink-0">'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_buttons_html + '\n' + html[end_idx:]
    with open('s:/CECP/landing/templates/landing/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Updated buttons successfully.')
else:
    print('Failed to find markers.')
