from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import ArrayField


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom")
    designation = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Alumni(models.Model):
    name = models.CharField(max_length=50)
    image_url = models.URLField()
    designation = models.CharField(max_length=30)
    quote = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=50, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom")
    image_url = models.URLField()
    description = models.TextField()
    student_count = models.IntegerField(default=35)
    language = models.CharField(max_length=40, default="English/Malayalam")
    duration = models.CharField(max_length=15, default="3 years")
    first_year_syllabus = ArrayField(models.CharField(max_length=35),
                                     help_text="Add multiple module names separated by comma",
                                     null=True, blank=True)
    second_year_syllabus = ArrayField(models.CharField(max_length=35),
                                      help_text="Add multiple module names separated by comma",
                                      null=True, blank=True)
    third_year_syllabus = ArrayField(models.CharField(max_length=35),
                                     help_text="Add multiple module names separated by comma",
                                     null=True, blank=True)


class Event(models.Model):
    EVENT_CHOICES = (
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("ended", "Ended"),
    )
    SKILL_LEVEL_CHOICES = (
        ("Open for all", "Open for all"),
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    )
    name = models.CharField(max_length=100)
    link = models.SlugField(max_length=30, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom",
                            unique=True)
    date = models.DateTimeField()
    status = models.CharField(choices=EVENT_CHOICES, default="upcoming", max_length=10)
    image_url = models.URLField()
    venue = models.CharField(max_length=30)
    topic = models.CharField(max_length=30, null=True, blank=True)
    host = models.CharField(max_length=30, null=True, blank=True)
    skill_level = models.CharField(max_length=30, null=True, blank=True, choices=SKILL_LEVEL_CHOICES)
    description = models.TextField()
    markdown_content = models.TextField(null=True, blank=True, help_text="Markdown content if any")
    staff_in_charge = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    facebook_page_link = models.URLField(null=True, blank=True, help_text="Optional")
    instagram_page_link = models.URLField(null=True, blank=True, help_text="Optional")
    twitter_link = models.URLField(null=True, blank=True, help_text="Optional")

    @property
    def month(self):
        return self.date.strftime('%B')[:3]

    @property
    def short_description(self):
        if len(self.description) <= 120:
            return self.description

        short_content = self.description[:120]
        rightmost_space = short_content.rfind(" ")
        rightmost_newline = short_content.rfind("\n")
        rightmost_separator = max((rightmost_space, rightmost_newline))
        return short_content[:rightmost_separator]

    def __str__(self):
        return self.name


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
