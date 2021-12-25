import uuid

from django.db import models
from django.contrib.auth.models import User
from utils.functions import generate_transaction_id, generate_registration_id


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
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    registration_open_date = models.DateTimeField(null=True)
    registration_end_date = models.DateTimeField(null=True)
    status = models.CharField(choices=EVENT_CHOICES, default="upcoming", max_length=10)
    image_url = models.URLField()
    venue = models.CharField(max_length=30)
    topic = models.CharField(max_length=30, null=True, blank=True)
    host = models.CharField(max_length=30, null=True, blank=True)
    skill_level = models.CharField(max_length=30, null=True, blank=True, choices=SKILL_LEVEL_CHOICES)
    description = models.TextField()
    markdown_content = models.TextField(null=True, blank=True, help_text="Markdown content if any")
    staff_in_charge = models.ForeignKey("web.Faculty", on_delete=models.SET_NULL, null=True, blank=True)
    facebook_page_link = models.URLField(null=True, blank=True, help_text="Optional")
    instagram_page_link = models.URLField(null=True, blank=True, help_text="Optional")
    twitter_link = models.URLField(null=True, blank=True, help_text="Optional")
    registration_link = models.URLField(null=True, blank=True, help_text="Optional")

    @property
    def month(self):
        return self.start_date.strftime('%B')[:3]

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


class Student(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(null=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    access_token = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student", null=True)
    college_name = models.CharField(max_length=150, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    completed_profile_setup = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Registration(models.Model):
    id = models.CharField(max_length=9, default=generate_registration_id, primary_key=True)
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="events_registered", null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="registered_student")
    total_value = models.IntegerField(default=0)


class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    reg_fee = models.IntegerField()
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    starting_time = models.DateTimeField()
    ending_time = models.DateTimeField()
    image = models.URLField(null=True, blank=True)
    staff = models.ForeignKey("web.Faculty", null=True, on_delete=models.CASCADE)


class Transaction(models.Model):
    id = models.CharField(max_length=9, primary_key=True, default=generate_transaction_id)
    paytm_transaction_id = models.CharField(max_length=35, null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    events_selected = models.ManyToManyField(Program, blank=True)
    bank_transaction_id = models.CharField(max_length=25, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, default="INITIATED")
    mode = models.CharField(max_length=20, null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)
    value = models.IntegerField(default=0)


class Notification(models.Model):
    message = models.CharField(max_length=250)
    creation_time = models.DateTimeField()
