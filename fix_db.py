import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cecp_project.settings")
django.setup()

from django.db import connection
from landing.models import Initiative

try:
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Initiative)
    print("Table 'landing_initiative' created successfully!")
except Exception as e:
    print(f"Error: {e}")
