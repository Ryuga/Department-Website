import os
import qrcode

from django.core import mail
from django.conf import settings

from core.apps.dashboard.models import Transaction
from utils.discord_handler import DiscordAPIClient
from utils.operations import get_html_formatted_message
from celery import shared_task

api = DiscordAPIClient(authorization=f"Bot {settings.BOT_TOKEN}")

@shared_task
def send_registration_email(transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        registration = transaction.registration
        programs = transaction.programs_selected.all()
        if not registration.qr:
            img = qrcode.make(f"https://zephyrus.christcs.in/event/registration/details/{registration.id}/")
            img.save(f"{registration.id}.png")
            resp = api.upload_file(open(f"{registration.id}.png", "rb"))
            if resp:
                registration.qr = resp["attachments"][0]["url"]
                registration.save()
            os.remove(f"{registration.id}.png")
        msg = get_html_formatted_message(registration.id, programs, registration.qr, transaction.value)
        mail.send_mail(
        subject=f"{registration.event.name} Registration Successful!",
        from_email="zephyrus-no-reply@christcs.in",
        message="",
        recipient_list=[registration.student.user.email],
        html_message=msg
    )
    except Transaction.DoesNotExist:
        print("Does not exist")
    except Exception as E:
        print(E)
