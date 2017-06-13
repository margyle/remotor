from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)
    app_label = 'board'

    def __unicode__(self):
        """Unicode representation for admin site."""
        return self.name


class RequiredKeyword(Keyword):
    required = True


class ExcludedKeyword(Keyword):
    required = False


class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        """Unicode representation for admin site."""
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    required_techs = models.ManyToManyField(RequiredKeyword)
    excluded_techs = models.ManyToManyField(ExcludedKeyword)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()