import requests
import json

from paytmchecksum import PaytmChecksum
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from .models import SubEvents, DashboardNotification, Order
google_oauth = GoogleOauth(redirect_uri="http://localhost:8000/login/oauth2/google/")
google_oauth_url, _ = google_oauth.flow.authorization_url()


def logout_request(request):
    logout(request)
    return LoginView.as_view()(request)


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name, {"google_oauth_url": google_oauth_url})


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        return render(request, self.template_name, {"google_oauth_url": google_oauth_url})


class GoogleAuthLoginCallback(View, ResponseMixin):

    def get(self, request):
        access_token = google_oauth.get_access_token(request)
        if access_token is not None:
            user_json = google_oauth.get_user_json(access_token)
            email = user_json.get("email")
            avatar = user_json.get("picture")
            name = user_json.get("given_name")
            try:
                user = User.objects.get(email=email)
                login(request, user)
                return DashView.as_view()(self.request)
            except User.DoesNotExist:
                user = create_user(email=email, avatar_url=avatar, access_token=access_token, name=name)
                login(request, user)
                return DashView.as_view()(self.request)
        else:
            return self.http_responce_404(request)


class DashView(LoginRequiredMixin, View):
    template_name = "dashboard/index.html"

    def get(self, request):
        notifications = DashboardNotification.objects.all()
        return render(request, self.template_name, {"notifications": notifications})
import base64
import string
import random
import hashlib

from Crypto.Cipher import AES


IV = "@@@@&&&&####$$$$"
BLOCK_SIZE = 16


def generate_checksum(param_dict, merchant_key, salt=None):
    params_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)

def generate_refund_checksum(param_dict, merchant_key, salt=None):
    for i in param_dict:
        if("|" in param_dict[i]):
            param_dict = {}
            exit()
    params_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)


def generate_checksum_by_str(param_str, merchant_key, salt=None):
    params_string = param_str
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return __encode__(hash_string, IV, merchant_key)


def verify_checksum(param_dict, merchant_key, checksum):
    # Remove checksum
    if 'CHECKSUMHASH' in param_dict:
        param_dict.pop('CHECKSUMHASH')

    # Get salt
    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]
    calculated_checksum = generate_checksum(param_dict, merchant_key, salt=salt)
    return calculated_checksum == checksum

def verify_checksum_by_str(param_str, merchant_key, checksum):
    # Remove checksum
    #if 'CHECKSUMHASH' in param_dict:
        #param_dict.pop('CHECKSUMHASH')

    # Get salt
    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]
    calculated_checksum = generate_checksum_by_str(param_str, merchant_key, salt=salt)
    return calculated_checksum == checksum



def __id_generator__(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def __get_param_string__(params):
    params_string = []
    for key in sorted(params.keys()):
        if("REFUND" in params[key] or "|" in params[key]):
            respons_dict = {}
            exit()
        value = params[key]
        params_string.append('' if value == 'null' else str(value))
    return '|'.join(params_string)


__pad__ = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
__unpad__ = lambda s: s[0:-ord(s[-1])]


def __encode__(to_encode, iv, key):
    # Pad
    to_encode = __pad__(to_encode)
    # Encrypt
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    to_encode = c.encrypt(to_encode.encode('utf-8'))
    # Encode
    to_encode = base64.b64encode(to_encode)
    return to_encode.decode("UTF-8")


def __decode__(to_decode, iv, key):
    # Decode
    to_decode = base64.b64decode(to_decode)
    # Decrypt
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    to_decode = c.decrypt(to_decode)
    if type(to_decode) == bytes:
        # convert bytes array to str.
        to_decode = to_decode.decode()
    # remove pad
    return __unpad__(to_decode)


if __name__ == "__main__":
    params = {
        "MID": "mid",
        "ORDER_ID": "order_id",
        "CUST_ID": "cust_id",
        "TXN_AMOUNT": "1",
        "CHANNEL_ID": "WEB",
        "INDUSTRY_TYPE_ID": "Retail",
        "WEBSITE": "xxxxxxxxxxx"
    }

    print(verify_checksum(
        params, 'xxxxxxxxxxxxxxxx',
        "CD5ndX8VVjlzjWbbYoAtKQIlvtXPypQYOg0Fi2AUYKXZA5XSHiRF0FDj7vQu66S8MHx9NaDZ/uYm3WBOWHf+sDQAmTyxqUipA7i1nILlxrk="))

    # print(generate_checksum(params, "xxxxxxxxxxxxxxxx"))

class UserProfileView(View):
    template_name = "dashboard/user-profile.html"
    fields = (
        "name", "phone_number", "college_name", "department"
    )

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        saved = False
        for field in self.fields:
            if request.POST.get(field):
                setattr(request.user.student, field, request.POST.get(field))
            request.user.student.save()
            saved = True
        return render(request, self.template_name, {"saved": saved})


class ZephyrusRegistrationView(LoginRequiredMixin, View, ResponseMixin):
    template_name = "dashboard/registration.html"

    def get(self, request):
        events = SubEvents.objects.all()
        return render(request, self.template_name, {"events": events})

    def post(self, request):
        print(request.POST)
        order_amt = int(request.POST.get("txnAmt"))
        order_items = request.POST.getlist("eventsList")[0].split(',')
        order_items_from_db = list()
        cost_total = 0
        for item_id in order_items:
            item = SubEvents.objects.get(id=item_id)
            cost_total += item.reg_fee
            order_items_from_db.append(item)
        if cost_total == order_amt:
            order = Order.objects.create(
                student=request.user.student,
                payment_amount=cost_total,
            )
            for item in order_items_from_db:
                order.events_registered.add(item)

            # paytmParams = dict()
            #
            # paytmParams["body"] = {
            #     "requestType": "Payment",
            #     "mid": settings.PAYTM_MERCHANT_ID,
            #     "websiteName": "WEBSTAGING",
            #     "orderId": order.id,
            #     "callbackUrl": "https://localhost:8000/payments/handler/",
            #     "txnAmount": {
            #         "value": str(order.payment_amount),
            #         "currency": "INR",
            #     },
            #     "userInfo": {
            #         "custId": request.user.email
            #     },
            # }
            # checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), settings.PAYTM_MERCHANT_KEY)
            #
            # paytmParams["head"] = {
            #     "signature": checksum
            # }
            #
            # post_data = json.dumps(paytmParams)
            # # for Staging
            # url = f"https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={settings.PAYTM_MERCHANT_ID}&orderId={order.id}"
            #
            # # for Production
            # # url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
            # response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
            # print(
            #     response
            # )
            # print(response["body"]["txnToken"])
            params = {
                "MID": settings.PAYTM_MERCHANT_ID,
                "ORDER_ID": str(order.id),
                "CUST_ID": request.user.email,
                "TXN_AMOUNT": str(order_amt),
                "CHANNEL_ID": "WEB",
                "INDUSTRY_TYPE_ID": "Retail",
                "WEBSITE": "WEBSTAGING",
                'CALLBACK_URL': 'http://127.0.0.1:8000/payments/handlers/',
            }
            checksum = generate_checksum(params, settings.PAYTM_MERCHANT_KEY)
            print(checksum)
            params["CHECKSUMHASH"] = checksum
            return render(request, "dashboard/paytm_payments.html", {"data": params})
        else:
            return self.json_response_401()  # FIX


class ZephyrusEventsView(LoginRequiredMixin, View):
    template_name = "dashboard/events.html"

    def get(self, request):
        events = SubEvents.objects.all()
        return render(request, self.template_name, {"events": events})


class ZephyrusScheduleView(View):
    template_name = "dashboard/schedule.html"

    def get(self, request):
        return render(request, self.template_name)
