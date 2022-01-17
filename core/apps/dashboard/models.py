import uuid
from datetime import datetime, timezone

from django.db import models
from django.contrib.auth.models import User
from utils.functions import generate_transaction_id, generate_registration_id


def time_now():
    return datetime.now(timezone.utc)


def default_json():
    return {}


class Event(models.Model):
    name = models.CharField(max_length=100)
    link = models.SlugField(max_length=30, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom",
                            unique=True)
    registration_open_date = models.DateTimeField(null=True)
    registration_end_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    image_url = models.URLField()
    venue = models.CharField(max_length=30)
    topic = models.CharField(max_length=30, null=True, blank=True)
    host = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField()
    markdown_content = models.TextField(null=True, blank=True, help_text="Markdown content if any")
    staff_in_charge = models.ForeignKey("web.Faculty", on_delete=models.SET_NULL, null=True, blank=True)
    registration_link = models.URLField(null=True, blank=True, help_text="Optional")

    @property
    def status(self):
        if time_now() < self.start_date:
            return "upcoming"
        elif time_now() > self.end_date:
            return "ended"
        return "live"

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
    registered_programs = models.ManyToManyField("Program", blank=True)

    def __str__(self):
        return self.name

    def active_registration(self):
        active_registrations = self.my_registrations.filter(event__end_date__gt=time_now(),
                                                            made_successful_transaction=True
                                                            )
        if active_registrations:
            return active_registrations[0]

    @property
    def registered_programs_str(self):
        return "".join(f"{program.name}, " for program in self.registered_programs.all())


class Registration(models.Model):
    id = models.CharField(max_length=9, default=generate_registration_id, primary_key=True)
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="registrations", null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="my_registrations")
    qr = models.URLField(blank=True, null=True)
    made_successful_transaction = models.BooleanField(default=False)
    physical_id_allotted = models.BooleanField(default=False)

    def registered_programs(self):
        return self.transaction_set.filter(status="TXN_SUCCESS").values_list("events_selected_json")

    def __str__(self):
        return f"{self.student.name}: {self.id} " \
               f"| Status: {'CONFIRMED' if self.made_successful_transaction else 'NOT CONFIRMED'}"

    @property
    def successful_transactions(self):
        return self.transaction_set.filter(status="TXN_SUCCESS")

    @property
    def spot_transaction_value(self):
        txn_sum = self.transaction_set.filter(
            status="TXN_SUCCESS", spot=True
        ).aggregate(models.Sum('value')).get('value__sum')
        if txn_sum:
            return txn_sum
        return 0

    @property
    def online_transaction_value(self):
        txn_sum = self.transaction_set.filter(
            status="TXN_SUCCESS", spot=False
        ).aggregate(models.Sum('value')).get('value__sum')
        if txn_sum:
            return txn_sum
        return 0


class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    reg_fee = models.IntegerField()
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    staff = models.ForeignKey("web.Faculty", null=True, on_delete=models.CASCADE)
    spot_registration_open = models.BooleanField(default=True)
    online_registration_open = models.BooleanField(default=True)
    venue = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def total_registrations(self):
        return self.transactions.filter(status="TXN_SUCCESS").count()


class Transaction(models.Model):
    id = models.CharField(max_length=9, primary_key=True, default=generate_transaction_id)
    paytm_transaction_id = models.CharField(max_length=35, null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    events_selected = models.ManyToManyField(Program, blank=True, related_name="transactions")
    events_selected_json = models.JSONField(null=True, default=default_json)
    bank_transaction_id = models.CharField(max_length=25, null=True, blank=True)
    creation_time = models.DateTimeField(default=time_now)
    date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, default="INITIATED")
    mode = models.CharField(max_length=20, null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)
    value = models.FloatField(default=0.0)
    raw_response = models.TextField(null=True)
    mail_sent = models.BooleanField(default=False)
    failure_msg = models.TextField(null=True)
    spot = models.BooleanField(default=False)

    def __str__(self):
        if self.status == "TXN_SUCCESS":
            return f"{self.registration.student.name}: {self.id} " \
                   f"| Status: {self.status} "
        return f"{self.registration.student.name}: {self.id} " \
               f"| Status: {self.status} " \
               f"| Phone: {self.registration.student.phone_number}"

    class Meta:
        ordering = ('-creation_time',)


class Slideshow(models.Model):
    order = models.IntegerField(default=0, unique=True)
    image = models.URLField()

    def __str__(self):
        return f"Slideshow {self.order}"


class EventDay(models.Model):
    date = models.DateField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def schedule(self):
        return self.eventschedule_set.order_by('start_time')


class EventSchedule(models.Model):
    day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    default_display = models.CharField(max_length=200,
                                       help_text="Will be displayed if no program is assigned",
                                       null=True, blank=True)
    programs = models.ManyToManyField(Program, blank=True)
    venue = models.CharField(max_length=100, blank=True,
                             null=True, help_text="Will be displayed for default")

    def __str__(self):
        return f"Day {self.day.date} {self.start_time} - {self.end_time}"

    def has_assigned_programs(self):
        return self.programs.exists()
