import datetime

import requests
import json

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.decorators.csrf import csrf_exempt
from utils.paytm_checksum import generate_checksum, verify_checksum
from .models import SubEvents, DashboardNotification, Registration, Transaction
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
        order_amt = int(request.POST.get("txnAmt"))
        order_items = request.POST.getlist("eventsList")[0].split(',')
        order_items_from_db = list()
        cost_total = 0
        registration = None
        for item_id in order_items:
            item = SubEvents.objects.get(id=item_id)
            cost_total += item.reg_fee
            order_items_from_db.append(item)
        if cost_total == order_amt:
            if not Registration.objects.filter(
                    student=request.user.student,
                    event=order_items_from_db[0].event
            ).exists():
                registration = Registration.objects.create(
                    event=order_items_from_db[0].event,
                    student=request.user.student
                )
            else:
                registration = Registration.objects.get(
                    student=request.user.student,
                    event=order_items_from_db[0].event
                )
            transaction = Transaction.objects.create(
                registration=registration,
            )
            for item in order_items_from_db:
                transaction.events_selected.add(item)
            param_dict = {
                'MID': settings.PAYTM_MERCHANT_ID,
                'ORDER_ID': str(transaction.id),
                'TXN_AMOUNT': str(order_amt),
                'CUST_ID': request.user.email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'DEFAULT',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/payments/handlers/',
            }
            param_dict["CHECKSUMHASH"] = generate_checksum(param_dict, settings.PAYTM_MERCHANT_KEY)
            return render(request, "dashboard/paytm_payments.html", {"data": param_dict})
        else:
            return self.json_response_401()


class ZephyrusEventsView(LoginRequiredMixin, View):
    template_name = "dashboard/events.html"

    def get(self, request):
        events = SubEvents.objects.all()
        return render(request, self.template_name, {"events": events})


class ZephyrusScheduleView(View):
    template_name = "dashboard/schedule.html"

    def get(self, request):
        return render(request, self.template_name)


@csrf_exempt
def payment_handler(request):
    print(request.POST)
    transaction_id = request.POST.get("ORDERID")
    paytm_transaction_id = request.POST.get("TXNID")
    transaction_status = request.POST.get("STATUS")
    bank_transaction_id = request.POST.get("BANKTXNID")
    transaction_date = request.POST.get("TXNDATE")
    checksum_hash = request.POST.get("CHECKSUMHASH")
    response_dict = request.POST.dict()
    verify = verify_checksum(response_dict, settings.PAYTM_MERCHANT_KEY, checksum_hash)
    if verify:
        if response_dict['RESPCODE'] == '01':
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.paytm_transaction_id = paytm_transaction_id
            transaction.bank_transaction_id = bank_transaction_id
            transaction.date = datetime.datetime.strptime(transaction_date[:19], "%Y-%m-%d %H:%M:%S")
            transaction.status = transaction_status
            transaction.save()
    return HttpResponse("OK")
