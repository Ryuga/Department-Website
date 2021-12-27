from datetime import datetime, timezone

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


def time_now():
    return datetime.now(timezone.utc)


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(null=True)
    link = models.CharField(max_length=100, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom")
    designation = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Gallery(models.Model):
    image_url = models.URLField()
    date = models.DateField(help_text="Images will be sorted on the basis of the dates.", null=True)
    tags = models.ManyToManyField(Tag, help_text="Select multiple tags related to the image", blank=True)
    description = models.CharField(max_length=30, null=True, blank=True)


class Course(models.Model):
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=50, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom")
    description = models.TextField()
    markdown_content = models.TextField(null=True, blank=True, help_text="Markdown content if any")
    student_count = models.IntegerField(default=35)
    language = models.CharField(max_length=40, default="English/Malayalam")
    duration = models.CharField(max_length=15, default="3 years")
    first_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                    help_text="Add multiple module names separated by comma",
                                    null=True, blank=True)
    second_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                     help_text="Add multiple module names separated by comma",
                                     null=True, blank=True)
    third_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                    help_text="Add multiple module names separated by comma",
                                    null=True, blank=True)
    fourth_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                     help_text="Add multiple module names separated by comma",
                                     null=True, blank=True)
    fifth_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                    help_text="Add multiple module names separated by comma",
                                    null=True, blank=True)
    sixth_sem_syllabus = ArrayField(models.CharField(max_length=50),
                                    help_text="Add multiple module names separated by comma",
                                    null=True, blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(help_text="Messages will be sorted on basis of this date")
    content = models.TextField()


class IpHash(models.Model):
    hash = models.CharField(max_length=10, primary_key=True)
    visit_time = models.DateTimeField(default=time_now)

    class Meta:
        verbose_name = "Site Visitor"

    def __str__(self):
        return f"Visited on {self.visit_time.date()} at {self.visit_time.time()}"


class PopUp(models.Model):
    title = models.CharField(max_length=30, null=True, blank=True, help_text="Optional")
    description = models.TextField(null=True, blank=True, help_text="Optional")
    image = models.ImageField(upload_to="img/popups")


class Batch(models.Model):
    year = models.DateField()

    def __str__(self):
        return str(self.year.year)

    @property
    def has_images(self):
        return self.alumni.first()


class Alumni(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="alumni")
    image_url = models.URLField()
