from django.contrib import admin
from .models import (
    Student, Program, Slideshow, Registration, Transaction,
    Event, EventDay, EventSchedule, TransactionProgramRelation
)

admin.site.register([
    Student, Program, Slideshow, Registration, Transaction,
    Event, EventDay, EventSchedule, TransactionProgramRelation
])
