from django.dispatch import receiver

from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify

from core.apps.web.models import Faculty, Course
from core.apps.dashboard.models import Event


@receiver(pre_save, sender=Event)
def event_link_setter(sender, instance, **kwargs):
    if not instance.link:
        instance.link = slugify(instance.name)


@receiver(pre_save, sender=Faculty)
def faculty_link_setter(sender, instance, **kwargs):
    if not instance.link:
        instance.link = slugify(instance.name)


@receiver(pre_save, sender=Course)
def course_link_setter(sender, instance, **kwargs):
    if not instance.link:
        instance.link = slugify(instance.name)
