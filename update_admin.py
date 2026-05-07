with open('s:/CECP/landing/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_str = "from .models import (\n    Project, Initiative, ClubMember, ProjectCategory, Notification,\n    ClubApplication, UserProfile, Blog, Event\n)"
new_import = "from .models import (\n    Project, Initiative, ClubMember, ProjectCategory, Notification,\n    ClubApplication, UserProfile, Blog, Event, EventStat\n)"
content = content.replace(import_str, new_import)

# if the import structure is different:
if import_str not in content:
    content = content.replace("Blog, Event", "Blog, Event, EventStat")

content += """

@admin.register(EventStat)
class EventStatAdmin(admin.ModelAdmin):
    list_display = ('events_hosted', 'participants', 'winners_crowned', 'collaborations')
"""

with open('s:/CECP/landing/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
