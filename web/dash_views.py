import requests
import json

from paytmchecksum import PaytmChecksum
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import View
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from .models import SubEvents
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
        return render(request, self.template_name)


class UserProfileView(View):
    template_name = "dashboard/user-profile.html"

    def get(self, request):
        return render(request, self.template_name)


class ZephyrusRegistrationView(View):
    template_name = "dashboard/registration.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        order_amt = request.POST.get("orderAmt")
        order_items = []
        paytmParams = dict()

        paytmParams["body"] = {
            "requestType": "Payment",
            "mid": "YOUR_MID_HERE",
            "websiteName": "WEBDEMO",
            "orderId": "ORDERID_98765",
            "callbackUrl": "https://localhost:8000/payments/handler/",
            "txnAmount": {
                "value": "1.00",
                "currency": "INR",
            },
            "userInfo": {
                "custId": request.user.email
            },
        }
        checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), settings.PAYTM_MERCHANT_ID)

        paytmParams["head"] = {
            "signature": checksum
        }

        post_data = json.dumps(paytmParams)
        # for Staging
        url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"

        # for Production
        # url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
        response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
        print(response)


class ZephyrusEventsView(LoginRequiredMixin, View):
    template_name = "dashboard/events.html"

    def get(self, request):
        events = SubEvents.objects.all()
        print(request.user)
        return render(request, self.template_name, {"events": events})


class ZephyrusScheduleView(View):
    template_name = "dashboard/schedule.html"

    def get(self, request):
        return render(request, self.template_name)