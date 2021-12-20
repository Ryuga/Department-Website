from django.contrib.auth.models import User
from utils.hashing import PasswordHasher
from web.models import Student

hasher = PasswordHasher()


def create_user(email, avatar_url, access_token, name):
    user = User.objects.create_user(username=email,
                                    email=email,
                                    first_name=name,
                                    password=hasher.get_hashed_pass(email))
    Student.objects.create(user=user, image_url=avatar_url)
    return user
