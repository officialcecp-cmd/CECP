with open('s:/CECP/landing/templates/landing/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_index = -1
end_index = -1
for i, line in enumerate(lines):
    if '<!-- Card 1: TECHNOMAX 5.0 -->' in line:
        start_index = i
    if '<!-- Card 6: INDUSTRY TALK -->' in line:
        for j in range(i, len(lines)):
            if '<!-- =============================================================' in lines[j]:
                end_index = j - 5
                break
        if end_index != -1:
            break

replacement = """
                        {% for event in events %}
                        <div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-{% if event.is_featured %}purple{% elif event.status == 'Live Now' %}green{% else %}cyan{% endif %}-500/50 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] transition-all duration-300 flex flex-col group relative">
                            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-{% if event.is_featured %}purple-500 to-indigo-500{% elif event.status == 'Live Now' %}green-500 to-emerald-500{% else %}cyan-500 to-blue-500{% endif %} z-20"></div>
                            <div class="h-40 bg-[url('{% if event.image %}{{ event.image.url }}{% else %}https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop{% endif %}')] bg-cover bg-center relative overflow-hidden">
                                <div class="absolute inset-0 bg-{% if event.is_featured %}indigo{% elif event.status == 'Live Now' %}green{% else %}cyan{% endif %}-900/40 group-hover:bg-{% if event.is_featured %}indigo{% elif event.status == 'Live Now' %}green{% else %}cyan{% endif %}-900/20 transition-colors"></div>
                                <div class="absolute top-3 left-3 bg-{% if event.is_featured %}purple{% elif event.status == 'Live Now' %}green{% else %}cyan{% endif %}-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded shadow-lg z-10 flex items-center gap-1">
                                    {% if event.status == 'Live Now' %}<span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>{% endif %} {{ event.status }}
                                </div>
                            </div>
                            <div class="p-5 flex-1 flex flex-col relative z-10 -mt-6">
                                <div class="bg-slate-900 border border-slate-700 w-max px-3 py-1 rounded text-xs font-mono text-{% if event.is_featured %}cyan{% elif event.status == 'Live Now' %}blue{% else %}blue{% endif %}-400 mb-3 shadow-lg">{{ event.event_type }}</div>
                                <h3 class="text-xl font-bold text-white mb-2">{{ event.title }}</h3>
                                <p class="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed flex-1">{{ event.description }}</p>
                                
                                <div class="space-y-2 mb-6">
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        {{ event.date_range }}
                                    </div>
                                    <div class="flex items-center gap-2 text-xs text-slate-300 font-mono">
                                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                        {{ event.location }}
                                    </div>
                                </div>
                                <div class="flex items-center justify-between mt-auto">
                                    <a href="{% if event.action_url %}{{ event.action_url }}{% else %}#{% endif %}" class="bg-{% if event.status == 'Completed' %}slate-700 hover:bg-slate-600{% elif event.status == 'Live Now' %}blue-600 hover:bg-blue-500{% else %}indigo-600 hover:bg-indigo-500{% endif %} text-white text-sm font-medium py-2 px-4 rounded transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba({% if event.status == 'Completed' %}100,116,139{% elif event.status == 'Live Now' %}37,99,235{% else %}79,70,229{% endif %},0.3)]">
                                        {{ event.action_text }} <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% empty %}
                        <div class="col-span-full text-center py-12 text-slate-400">
                            No events found. Check back later!
                        </div>
                        {% endfor %}
"""

if start_index != -1 and end_index != -1:
    new_lines = lines[:start_index] + [replacement] + lines[end_index+1:]
    with open('s:/CECP/landing/templates/landing/index.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Replacement successful")
else:
    print(f"Failed. Start: {start_index}, End: {end_index}")
