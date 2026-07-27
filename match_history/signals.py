from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile instance whenever a new User is created.
    This ensures every user has an associated profile.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile instance whenever the User is saved.
    This ensures the profile is always kept in sync.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist (fallback)
        UserProfile.objects.create(user=instance)