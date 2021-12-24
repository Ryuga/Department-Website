from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify

from utils.hashing import PasswordHasher
from core.apps.web.models import Student, Event, Faculty, Course

hasher = PasswordHasher()


def create_user(email, avatar_url, access_token, name):
    user = User.objects.create_user(username=email,
                                    email=email,
                                    first_name=name,
                                    password=hasher.get_hashed_pass(email))
    Student.objects.create(user=user, image_url=avatar_url, name=name, access_token=access_token)
    return user


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
