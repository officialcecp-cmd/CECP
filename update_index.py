import re

with open('s:/CECP/landing/templates/landing/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update Search Input
html = html.replace(
    'placeholder="Search events..."',
    'id="eventSearchInput" placeholder="Search events..." onkeyup="filterEvents()"'
)

# Update Event Card Div
old_card = '<div class="bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-{% if event.is_featured %}purple{% elif event.status == \'Live Now\' %}green{% else %}cyan{% endif %}-500/50 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] transition-all duration-300 flex flex-col group relative">'
new_card = '<div class="event-card bg-slate-900/80 border border-slate-700/60 rounded-2xl overflow-hidden hover:border-{% if event.is_featured %}purple{% elif event.status == \'Live Now\' %}green{% else %}cyan{% endif %}-500/50 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] transition-all duration-300 flex flex-col group relative" data-type="{{ event.event_type }}" data-status="{{ event.status }}" data-title="{{ event.title|lower }}">'
html = html.replace(old_card, new_card)

# Update buttons
def update_button(html, label, filter_val):
    # Find the button element that contains the label
    # This regex looks for `<button class="..."> ... label ... </button>`
    pattern = r'(<button class="[^"]*)("([^>]*)>(.*?)' + re.escape(label) + r'(.*?)</button>)'
    
    def replacer(match):
        class_attr = match.group(1)
        rest_of_open = match.group(3)
        inner1 = match.group(4)
        inner2 = match.group(5)
        
        new_class = class_attr + ' event-filter-btn'
        
        # Determine if it's the active button (All Events) by default
        if label == 'All Events':
            # Remove bg-transparent text-slate-400 and add bg-slate-800 text-white (already there mostly)
            pass
            
        onclick = f' onclick="filterEvents(\'{filter_val}\', this)"'
        
        return f'{new_class}"{onclick}{rest_of_open}>{inner1}{label}{inner2}</button>'
        
    return re.sub(pattern, replacer, html, flags=re.DOTALL)

buttons = [
    ('All Events', 'all'),
    ('Hackathons', 'Hackathon'),
    ('Workshops', 'Workshop'),
    ('Competitions', 'Competition'),
    ('Talks', 'Talk'),
    ('Ongoing', 'status:Ongoing'),
    ('Past Events', 'status:Completed')
]

for label, filter_val in buttons:
    html = update_button(html, label, filter_val)

with open('s:/CECP/landing/templates/landing/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
