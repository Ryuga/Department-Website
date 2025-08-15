import uuid
from datetime import datetime, timezone

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.template.defaultfilters import slugify
from utils.functions import generate_transaction_id, generate_registration_id
from utils.abstract_models import SingletonModel


def time_now():
    return datetime.now(timezone.utc)


def default_json():
    return {}


class SiteSetting(SingletonModel):
    site_email = models.EmailField(max_length=100, null=True, blank=True)
    site_instagram = models.URLField(max_length=100, null=True, blank=True,
                                     help_text="Please enter valid instagram profile url"
                                     )
    site_external_link = models.URLField(max_length=100, null=True, blank=True,
                                         help_text="Please enter valid website url"
                                         )
    support_enabled = models.BooleanField(default=False, help_text="Select if support option needs to be enabled")
    event_support_email = models.CharField(max_length=100, null=True, blank=True)
    event_support_whatsapp = models.CharField(max_length=10, null=True, blank=True,
                                              help_text="Please enter valid whatsapp number"
                                              )
    event_support_instagram = models.CharField(max_length=20, null=True, blank=True,
                                               help_text="Please enter valid instagram id (exclude '@')"
                                               )
    youtube_video_box_title = models.CharField(max_length=30, null=True, blank=True)
    youtube_video_embed_code = models.CharField(
        max_length=30, null=True, blank=True,
        help_text="Make sure video embedding is allowed in youtube console"
    )
    custom_event_page_name = models.CharField(max_length=12, null=True, blank=True,
                                              help_text="[Optional]: This will change the default Event page links")


class Event(models.Model):
    name = models.CharField(max_length=100)
    link = models.SlugField(max_length=30, null=True,
                            blank=True, help_text="Leave empty to auto create or add custom",
                            unique=True)
    registration_open_date = models.DateTimeField(null=True)
    registration_end_date = models.DateTimeField(null=True)
    hidden = models.BooleanField(default=False)
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
    special_message = models.TextField(null=True, blank=True, help_text="Special message to send in email if any")
    listing_order = models.IntegerField(default=0)
    custom_registration_button_link = models.URLField(null=True, blank=True, help_text="Optional")

    @classmethod
    def event_link_setter(cls, instance, **kwargs):
        if not instance.link:
            instance.link = slugify(instance.name)

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

    @property
    def has_registration_open(self):
        return self.registration_end_date > time_now() > self.registration_open_date

    @property
    def successful_registrations(self):
        return self.registrations.filter(made_successful_transaction=True)

    @property
    def transactions(self):
        return Transaction.objects.filter(registration__event=self, status="TXN_SUCCESS")

    @property
    def online_transactions(self):
        return Transaction.objects.filter(registration__event=self, status="TXN_SUCCESS", spot=False)

    @property
    def spot_transactions(self):
        return Transaction.objects.filter(registration__event=self, status="TXN_SUCCESS", spot=True)

    @property
    def registration_count(self):
        return self.successful_registrations.count()

    @property
    def transaction_count(self):
        return self.transactions.count()

    @property
    def online_transaction_count(self):
        return self.online_transactions.count()

    @property
    def spot_transaction_count(self):
        return self.spot_transactions.count()

    @classmethod
    def upcoming_events_with_registration_open(cls):
        return cls.objects.filter(registration_open_date__lt=time_now(), registration_end_date__gt=time_now())


class Student(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(null=True, max_length=200)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    access_token = models.CharField(max_length=300)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student", null=True)
    college_name = models.CharField(max_length=150, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    completed_profile_setup = models.BooleanField(default=False)
    registered_programs = models.ManyToManyField("Program", blank=True)
    restricted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now_add=True)
    anomalous_update_count = models.IntegerField(default=0)
    is_student = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def active_registrations(self):
        return self.my_registrations.filter(event__end_date__gt=time_now(),
                                            made_successful_transaction=True
                                            )

    @staticmethod
    def active_events():
        return Event.objects.filter(end_date__gt=time_now(), hidden=False).order_by("listing_order")

    @property
    def registered_programs_str(self):
        return "".join(f"{program.name}, " for program in self.registered_programs.all())

    @property
    def total_payment_collected(self):
        return self.transaction_set.all().aggregate(models.Sum('value')).get('value__sum')

    @property
    def address(self):
        return f"{self.college_name}\n+91{self.phone_number}"


class Registration(models.Model):
    id = models.CharField(max_length=9, default=generate_registration_id, primary_key=True)
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="registrations", null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="my_registrations")
    qr = models.URLField(blank=True, null=True)
    made_successful_transaction = models.BooleanField(default=False)
    physical_id_allotted = models.BooleanField(default=False)

    def registered_programs(self):
        return self.transaction_set.filter(status="TXN_SUCCESS").values_list("events_selected_json")

    def my_registered_programs(self):
        return self.student.registered_programs.all()

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
    reg_fee = models.IntegerField(validators=[MinValueValidator(0)])
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    registration_limit = models.IntegerField(default=-1)
    staff = models.ForeignKey("web.Faculty", null=True, on_delete=models.CASCADE)
    spot_registration_open = models.BooleanField(default=True)
    online_registration_open = models.BooleanField(default=True)
    venue = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def total_registrations(self):
        return self.transactions.filter(status="TXN_SUCCESS").count()

    @property
    def registered_users(self):
        return self.student_set.all()


class Transaction(models.Model):
    id = models.CharField(max_length=9, primary_key=True, default=generate_transaction_id)
    paytm_transaction_id = models.CharField(max_length=35, null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    programs_selected = models.ManyToManyField(Program, blank=True, related_name="transactions",
                                               through="TransactionProgramRelation")
    events_selected_json = models.JSONField(null=True, default=default_json)
    bank_transaction_id = models.CharField(max_length=25, null=True, blank=True)
    creation_time = models.DateTimeField(default=time_now)
    registrar = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
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


class TransactionProgramRelation(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="program_relation")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="transaction_relation")


class ProgramStudentRelation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="program_relation")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="student_relation")
    entry_given = models.BooleanField(default=False)
