"""
Quick recovery script — Run this with: python manage.py shell < recover_profile.py
This will recreate the superuser + ClubMember + UserProfile if they were deleted.
"""
from django.contrib.auth.models import User
from landing.models import ClubMember, UserProfile
import uuid

# === EDIT THESE VALUES ===
USERNAME = 'admin'           # Change to your username
EMAIL = 'adityaraj@example.com'  # Change to your email
FIRST_NAME = 'Aditya'
LAST_NAME = 'Raj'
PASSWORD = 'cecp2026'        # Change to your desired password
IS_SUPERUSER = True          # Set True if you were the admin
ROLE = 'club_head'           # 'hod', 'faculty', 'club_head', or 'member'
CATEGORY = 'head'            # 'advisor', 'head', 'core', or 'member'
DISPLAY_ROLE = 'Club Head'
# =========================

# Step 1: Create or get User
user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={
        'email': EMAIL,
        'first_name': FIRST_NAME,
        'last_name': LAST_NAME,
        'is_superuser': IS_SUPERUSER,
        'is_staff': IS_SUPERUSER,
    }
)
if created:
    user.set_password(PASSWORD)
    user.save()
    print(f"✅ User '{USERNAME}' created (superuser={IS_SUPERUSER})")
else:
    print(f"ℹ️  User '{USERNAME}' already exists (id={user.id})")

# Step 2: Create ClubMember
member, created = ClubMember.objects.get_or_create(
    user=user,
    defaults={
        'role': ROLE,
        'category': CATEGORY,
        'display_role': DISPLAY_ROLE,
        'display_name': f'{FIRST_NAME} {LAST_NAME}',
        'member_id': f'CECP-{str(uuid.uuid4())[:8].upper()}',
        'is_active': True,
    }
)
if created:
    print(f"✅ ClubMember profile created (role={ROLE})")
else:
    print(f"ℹ️  ClubMember already exists (id={member.id})")

# Step 3: Create UserProfile
profile, created = UserProfile.objects.get_or_create(user=user)
if created:
    print(f"✅ UserProfile created")
else:
    print(f"ℹ️  UserProfile already exists")

print(f"\n🎉 Recovery complete! Login with: {USERNAME} / {PASSWORD}")
