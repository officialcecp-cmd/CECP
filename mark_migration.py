import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cecp_project.settings')
django.setup()

from django.db import connection

sql = """
INSERT INTO django_migrations (app, name, applied) 
VALUES ('landing', '0038_projectaccessrequest', NOW())
ON CONFLICT DO NOTHING;
"""

with connection.cursor() as cursor:
    cursor.execute(sql)
    print("Migration 0038 marked as applied!")
