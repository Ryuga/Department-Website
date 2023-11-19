from django.contrib.auth.models import User

from utils.hashing import PasswordHasher
from core.apps.dashboard.models import Student, Transaction
from utils.html_message import template_1st_half, template_2nd_half, pricing_row, style, special_message


hasher = PasswordHasher()


def create_user(email, avatar_url, access_token, name):
    user = User.objects.create_user(username=email,
                                    email=email,
                                    first_name=name,
                                    password=hasher.get_hashed_pass(email))
    Student.objects.create(user=user, image_url=avatar_url, name=name, access_token=access_token)
    return user


def write_sheet(sheet, row, *args):
    for item in args:
        sheet.write(row, args.index(item), item)


def get_special_message(transaction):
    if transaction.registration.event.special_message:
        return special_message.format(
            message=transaction.registration.event.special_message
        )
    return "<br/>"


def get_html_formatted_message(transaction):
    pricing = ""
    spl_message = get_special_message(transaction)
    for program in transaction.programs_selected.all():
        pricing = pricing + pricing_row.format(img=program.image or "https://lairesit.sirv.com/Images/"
                                                                    "Individual%20Event%201x1/Blitz.jpg",
                                               program_name=program.name,
                                               fee=program.reg_fee)
    first_half = template_1st_half.format(txn_id=transaction.id,
                                          reg_link=f"https://zephyrus.christcs.in/{transaction.registration.event.link}"
                                                   f"/registration/me/",
                                          event_name=transaction.registration.event.name,
                                          qrcode_url=transaction.registration.qr,
                                          name=transaction.registration.student.name,
                                          reg_id=transaction.registration.id,
                                          style=style,
                                          spl_message=spl_message
                                          )
    second_half = template_2nd_half.format(name=transaction.registration.student.name,
                                           address=transaction.registration.student.address,
                                           txn_date=transaction.date.strftime("%d/%m/%Y"),
                                           payment_mode=transaction.mode,
                                           total=transaction.value,
                                           tax=transaction.value*0.18,
                                           )
    return first_half + pricing + second_half




