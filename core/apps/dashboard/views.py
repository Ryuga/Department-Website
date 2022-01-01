import pytz
import xlwt
import datetime

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import View
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user, write_sheet
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.paytm_checksum import generate_checksum, verify_checksum
from .models import Program, Slideshow, Registration, Transaction, Event, EventDay

google_oauth = GoogleOauth(redirect_uri=settings.OAUTH_REDIRECTION_URL)
google_oauth_url, _ = google_oauth.flow.authorization_url()


def logout_request(request):
    logout(request)
    return LoginView.as_view()(request)


class LoginView(View):
    template_name = "web/login.html"

    def get(self, request):
        return render(request, self.template_name, {"google_oauth_url": google_oauth_url})


class RegisterView(View):
    template_name = "web/register.html"

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
        slideshow = Slideshow.objects.all().order_by('order')
        return render(request, self.template_name, {"slideshow": slideshow})


class UserProfileView(LoginRequiredMixin, View):
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
        if request.POST.get("initial"):
            request.user.student.completed_profile_setup = True
            request.user.student.save()
            return redirect("/")
        return render(request, self.template_name, {"saved": saved})


class ZephyrusRegistrationView(LoginRequiredMixin, View, ResponseMixin):
    template_name = "dashboard/registration.html"

    def get(self, request):
        event = Event.objects.get(link="zephyrus30")
        all_programs = event.program_set.filter(registration_open=True)
        registered_programs = request.user.student.registered_programs.all()
        programs = [
            program for program in all_programs if program not in registered_programs
        ]
        return render(request, self.template_name, {"programs": programs})

    def post(self, request):
        order_amt = int(request.POST.get("txnAmt"))
        order_items = request.POST.getlist("eventsList")[0].split(',')
        order_items_from_db = list()
        cost_total = 0
        for item_id in order_items:
            item = Program.objects.get(id=item_id)
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
                transaction.events_selected_json[item.name] = item.reg_fee
            transaction.save()
            param_dict = {
                'MID': settings.PAYTM_MERCHANT_ID,
                'ORDER_ID': str(transaction.id),
                'TXN_AMOUNT': str(order_amt),
                'CUST_ID': request.user.email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'DEFAULT',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
            }
            param_dict["CHECKSUMHASH"] = generate_checksum(param_dict, settings.PAYTM_MERCHANT_KEY)
            return render(request, "dashboard/payments/paytm_payments.html",
                          {"data": param_dict,
                           "paytm_process_transaction_url": settings.PAYTM_PROCESS_TRANSACTION_URL
                           }
                          )
        else:
            return self.json_response_401()


class ZephyrusEventsView(LoginRequiredMixin, View):
    template_name = "dashboard/events.html"

    def get(self, request):
        events = Program.objects.all()
        return render(request, self.template_name, {"events": events})


class ZephyrusScheduleView(LoginRequiredMixin, View):
    template_name = "dashboard/schedule.html"

    def get(self, request):
        event_days = EventDay.objects.filter(event__link="zephyrus30").order_by('date')
        return render(request, self.template_name, {"event_days": event_days})


@csrf_exempt
def payment_handler(request):
    response_dict = request.POST.dict() or "No Response received"
    checksum_hash = request.POST.get("CHECKSUMHASH") or "No checksum hash"
    transaction_id = request.POST.get("ORDERID")
    if transaction_id:
        try:
            transaction = Transaction.objects.get(id=request.POST.get("ORDERID"))
            verify = verify_checksum(response_dict, settings.PAYTM_MERCHANT_KEY, checksum_hash)
            if verify:
                transaction.raw_response = response_dict
                if response_dict['RESPCODE'] == '01':
                    transaction.registration.made_successful_transaction = True
                    for program in transaction.events_selected.all():
                        transaction.registration.student.registered_programs.add(program)
                    transaction.registration.save()
                else:
                    transaction.status = "FAILED"
                    transaction.failure_msg = response_dict.get("RESPMSG")
                if request.POST.get("TXNID"):
                    transaction.paytm_transaction_id = request.POST.get("TXNID")
                    transaction.bank_transaction_id = request.POST.get("BANKTXNID")
                transaction.value = request.POST.get("TXNAMOUNT")
                if request.POST.get("STATUS"):
                    transaction.status = request.POST.get("STATUS")
                if request.POST.get("TXNDATE"):
                    transaction.date = datetime.datetime.strptime(
                        request.POST.get("TXNDATE")[:19], "%Y-%m-%d %H:%M:%S") \
                        .replace(
                        tzinfo=pytz.UTC
                    )
                transaction.save()
            else:
                transaction.status = "FAILED"
                transaction.failure_msg = "Checksum verification failed"
                transaction.save()

        except Transaction.DoesNotExist:
            response_dict["RESPCODE"] = '00'
            response_dict["RESPMSG"] = f"Transaction {transaction_id} not found!"
    else:
        response_dict["RESPCODE"] = "00"
        response_dict["RESPMSG"] = "Transaction ID not set on callback"

    return render(request, "dashboard/payments/payment_status.html", {"response": response_dict})


class RegistrationDetailView(LoginRequiredMixin, View):

    def get(self, request, reg_id):
        try:
            registration = Registration.objects.get(id=reg_id)
            if registration.student == request.user.student:
                return render(request, "dashboard/registration_details.html", {"registration": registration})
            else:
                raise Registration.DoesNotExist
        except Registration.DoesNotExist:
            return render(request, "web/404.html")


class AdminRegistrationDetailView(LoginRequiredMixin, View):

    def get(self, request, reg_id=None):
        if request.user.is_staff:
            try:
                registration = Registration.objects.get(id=reg_id)
            except Registration.DoesNotExist:
                registration = None
            if request.GET.get("ajax") == 'true':
                return render(request,
                              "dashboard/extendable/registration-detail-section.html", {"registration": registration})
            return render(request, "dashboard/admin/registration-details.html", {"registration": registration})
        return render(request, "web/404.html")


class AdminRegistrationDataView(LoginRequiredMixin, View):

    def get(self, request):
        if request.user.is_staff:
            if request.user.is_superuser and request.GET.get("type"):
                workbook = xlwt.Workbook()
                sheet = workbook.add_sheet("registrations")
                i = 1
                if request.GET.get("type") == "all":
                    registrations = Registration.objects.filter(made_successful_transaction=True)
                    write_sheet(sheet, 0, "Reg ID", "Name", "College", "Registered Programs")
                    for registration in registrations:
                        registered_programs = ""
                        for program in registration.student.registered_programs.all():
                            registered_programs = "".join(f"{program.name}, ")
                        write_sheet(sheet, i, registration.id,
                                    registration.student.name,
                                    registration.student.college_name,
                                    registered_programs)
                        i += 1
                        workbook.save("media/all-registrations.xls")
                elif request.GET.get("type") == "individual":
                    write_sheet(sheet, 0, "Reg ID", "Name", "College")
                    program_id = request.GET.get("program_id")
                    program = Program.objects.get(id=program_id)
                    transactions = program.transactions.filter(status="TXN_SUCCESS")
                    for transaction in transactions:
                        write_sheet(sheet, i, transaction.registration.id,
                                    transaction.registration.student.name,
                                    transaction.registration.student.college_name)
                        workbook.save(f"media/{program.name}-registrations.xls")
                else:
                    pass
            programs = Program.objects.all()
            return render(request, "dashboard/admin/registration-data.html", {"programs": programs})
        return render(request, "web/404.html")
