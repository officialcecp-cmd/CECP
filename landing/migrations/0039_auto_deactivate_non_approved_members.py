"""
Data migration: Auto-deactivate ClubMembers who don't have an approved
ClubApplication. This ensures public/visitor users who registered directly
(not through the club application process) are automatically locked out of
protected project resources.

Superusers and staff users are exempted from deactivation.
"""
from django.db import migrations


def deactivate_non_approved_members(apps, schema_editor):
    ClubMember = apps.get_model('landing', 'ClubMember')
    ClubApplication = apps.get_model('landing', 'ClubApplication')
    User = apps.get_model('auth', 'User')

    # Get all user IDs that have an approved club application
    approved_user_ids = set()

    # Users linked directly to approved applications
    direct_ids = ClubApplication.objects.filter(
        status='approved', user__isnull=False
    ).values_list('user_id', flat=True)
    approved_user_ids.update(direct_ids)

    # Users whose email matches an approved application's email
    approved_emails = ClubApplication.objects.filter(
        status='approved'
    ).values_list('email', flat=True)
    email_user_ids = User.objects.filter(
        email__in=approved_emails
    ).values_list('id', flat=True)
    approved_user_ids.update(email_user_ids)

    # Also check personal_email field
    approved_personal_emails = ClubApplication.objects.filter(
        status='approved'
    ).exclude(personal_email__isnull=True).exclude(
        personal_email=''
    ).values_list('personal_email', flat=True)
    personal_email_user_ids = User.objects.filter(
        email__in=approved_personal_emails
    ).values_list('id', flat=True)
    approved_user_ids.update(personal_email_user_ids)

    # Get superuser/staff IDs (always keep active)
    staff_ids = set(
        User.objects.filter(
            is_superuser=True
        ).values_list('id', flat=True)
    ) | set(
        User.objects.filter(
            is_staff=True
        ).values_list('id', flat=True)
    )

    # Combine: users to keep active
    keep_active_ids = approved_user_ids | staff_ids

    # Deactivate all ClubMembers NOT in the keep-active list
    deactivated = ClubMember.objects.exclude(
        user_id__in=keep_active_ids
    ).filter(is_active=True).update(is_active=False)

    print(f"  → Deactivated {deactivated} non-approved ClubMember(s)")
    print(f"  → Kept {len(keep_active_ids)} approved/staff member(s) active")


def reverse_migration(apps, schema_editor):
    # No-op reverse: we can't know the previous state
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0038_projectaccessrequest'),
    ]

    operations = [
        migrations.RunPython(
            deactivate_non_approved_members,
            reverse_migration,
        ),
    ]
