import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cecp_project.settings')
django.setup()

from landing.models import Event
if not Event.objects.exists():
    Event.objects.create(
        title='TECHNOMAX 5.0',
        event_type='Hackathon',
        status='Upcoming',
        description='National level electronics hackathon. Innovate. Integrate. Inspire.',
        date_range='24-26 May 2025',
        location='CECP, Bhopal',
        is_featured=True,
        action_text='Register Now'
    )
    Event.objects.create(
        title='PCB DESIGN WORKSHOP',
        event_type='Workshop',
        status='Live Now',
        description='Learn PCB designing from basics to advanced with hands-on practice.',
        date_range='18 May 2025',
        location='Electronics Lab',
        is_featured=False,
        action_text='View Details'
    )
    Event.objects.create(
        title='INDUSTRY TALK',
        event_type='Talk',
        status='Upcoming',
        description='Insights from industry experts on emerging technologies.',
        date_range='5 June 2025',
        location='Online (Zoom)',
        is_featured=False,
        action_text='Register Now'
    )
print('Events created successfully')
