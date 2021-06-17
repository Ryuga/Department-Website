import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=30)
    # qualifications = ArrayField(models.CharField(max_length=20), null=True, blank=True)


class Event(models.Model):
    EVENT_CHOICES = (
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("ended", "Ended"),
    )
    name = models.CharField(max_length=100)
    link = models.SlugField(max_length=30, null=True, blank=True, help_text="Leave empty to auto create or add custom",
                            unique=True)
    date = models.DateTimeField()
    status = models.CharField(choices=EVENT_CHOICES, default="upcoming", max_length=10)
    image_url = models.URLField()
    venue = models.CharField(max_length=30)
    description = models.TextField()


@receiver(pre_save, sender=Event)
def event_link_setter(sender, instance, **kwargs):
    if not instance.link:
        instance.link = slugify(instance.name)
