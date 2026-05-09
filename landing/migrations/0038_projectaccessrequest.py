from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('landing', '0037_userprofile_github_languages_cache_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAccessRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], db_index=True, default='pending', max_length=20)),
                ('message', models.TextField(blank=True, help_text='Optional message from the requester explaining why they need access')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(help_text='The project whose resources are being requested', on_delete=django.db.models.deletion.CASCADE, related_name='access_requests', to='landing.project')),
                ('requester', models.ForeignKey(help_text='The user requesting access to the project resources', on_delete=django.db.models.deletion.CASCADE, related_name='access_requests', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='Project owner who reviewed this request', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_access_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project Access Request',
                'verbose_name_plural': 'Project Access Requests',
                'ordering': ['-created_at'],
                'unique_together': {('requester', 'project')},
            },
        ),
    ]
