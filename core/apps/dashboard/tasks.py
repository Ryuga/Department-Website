import qrcode
from io import BytesIO

from core.apps.dashboard.models import Transaction, Student
from utils.operations import get_html_formatted_message
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage


@shared_task
def remove_account_restriction(username):
    try:
        student = Student.objects.get(user__username=username)
        student.restricted = False
        student.anomalous_update_count = 0
        student.save()
    except Student.DoesNotExist:
        print("Student Does not exist")
    except Exception as E:
        print(E)


def pil_image_to_mime_image(pil_image, filename="image.png"):
    image_buffer = BytesIO()
    pil_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)
    mime_image = MIMEImage(image_buffer.read(), _subtype="png")
    mime_image.add_header("Content-ID", "<qrcode_image>")
    mime_image.add_header('Content-Disposition', 'inline', filename=filename)

    return mime_image


@shared_task
def send_registration_email(transaction_id, fail=False):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        registration = transaction.registration
        img = qrcode.make(f"https://zephyrus.christcs.in/event/registration/details/{registration.id}/")
        msg = get_html_formatted_message(transaction)
        if not fail:
            email = EmailMultiAlternatives(
                subject=f"{registration.event.name} Registration Successful!",
                from_email="zephyrus-no-reply@christcs.in",
                body="",
                to=[registration.student.user.email],
            )
            email.attach_alternative(msg, "text/html")
            email.attach(pil_image_to_mime_image(img))
            email.send()
        return msg
    except Transaction.DoesNotExist:
        print("Does not exist")
    except Exception as E:
        print(E)
