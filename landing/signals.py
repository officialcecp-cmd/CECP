from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ClubMember

@receiver(post_save, sender=User)
def create_club_member_for_user(sender, instance, created, **kwargs):
    """
    Automatically creates a ClubMember profile with default role 'member'
    whenever a new User is created (e.g., via Social Login).
    """
    if created:
        import uuid
        unique_id = f"CECP-{str(uuid.uuid4())[:8].upper()}"
        ClubMember.objects.get_or_create(user=instance, defaults={'role': 'member', 'member_id': unique_id})
