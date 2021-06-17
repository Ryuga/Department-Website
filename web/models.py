import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    designation = models.CharField(max_length=30)
    # qualifications = ArrayField(models.CharField(max_length=20), null=True, blank=True)


class Event(models.Model):
    EVENT_CHOICES = (
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("ended", "Ended"),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    status = models.CharField(choices=EVENT_CHOICES, default="upcoming", max_length=10)
    image_url = models.URLField()
    venue = models.CharField(max_length=30)
    description = models.TextField()
