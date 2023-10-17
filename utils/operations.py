from django.contrib.auth.models import User

from utils.hashing import PasswordHasher
from core.apps.dashboard.models import Student, Transaction
from utils.html_message import template_1st_half, template_2nd_half, pricing_row



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


def get_html_formatted_message(reg_id, programs, qrcode_url, total_value):
    pricing = ""
    for program in programs:
        pricing = pricing + pricing_row.format(program_name=program.name, fee=program.reg_fee)
    template = template_2nd_half.format(reg_id=reg_id, pricing=pricing, qrcode_url=qrcode_url, total_value=total_value)
    return template_1st_half + template



