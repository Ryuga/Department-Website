import pytz
import xlwt
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseForbidden
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user, write_sheet
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.paytm_checksum import generate_checksum, verify_checksum
from .models import Program, Slideshow, Registration, Transaction, Event, EventDay, Student

google_oauth = GoogleOauth(redirect_uri=settings.OAUTH_REDIRECTION_URL)
google_oauth_url, _ = google_oauth.flow.authorization_url()


def media_access(request, path):
    if request.user.is_superuser:
        response = HttpResponse()
        # Content-type will be detected by nginx
        del response['Content-Type']
        response['X-Accel-Redirect'] = '/protected/media/' + path
        return response
    else:
        return HttpResponseForbidden('Not authorized to access this file.')


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
                return redirect(to="/")
            except User.DoesNotExist:
                user = create_user(email=email, avatar_url=avatar, access_token=access_token, name=name)
                login(request, user)
                return redirect(to="/")
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

    def get(self, request, event_link):
        programs = []
        event = Event.objects.get(link=event_link)
        if request.user.is_superuser:
            all_programs = event.program_set.filter(spot_registration_open=True)
        else:
            all_programs = event.program_set.filter(online_registration_open=True)
        if request.user.is_superuser:
            if request.GET.get("ajax") == "true":
                does_not_exist = False
                email = request.GET.get("email")
                try:
                    student = Student.objects.get(user__email=email)
                    registered_programs = student.registered_programs.all()
                    programs = [
                        program for program in all_programs if program not in registered_programs
                    ]
                except Student.DoesNotExist:
                    does_not_exist = True
                return render(request, "dashboard/extendable/registration_card.html", {"programs": programs,
                                                                                       "does_not_exist": does_not_exist
                                                                                       })
        else:
            registered_programs = request.user.student.registered_programs.all()
            programs = [
                program for program in all_programs if program not in registered_programs
            ]
        return render(request, self.template_name, {"programs": programs,
                                                    "event": event
                                                    })

    def post(self, request, event_link):
        order_amt = int(request.POST.get("txnAmt"))
        order_items = request.POST.getlist("eventsList")[0].split(',')
        order_items_from_db = list()
        cost_total = 0
        for item_id in order_items:
            item = Program.objects.get(id=item_id)
            cost_total += item.reg_fee
            order_items_from_db.append(item)
        if request.user.is_superuser:
            registration_owner = User.objects.get(email=request.POST.get("recipientEmail")).student
        else:
            registration_owner = request.user.student
        if cost_total == order_amt:
            if not Registration.objects.filter(
                    student=registration_owner,
                    event=order_items_from_db[0].event
            ).exists():
                registration = Registration.objects.create(
                    event=order_items_from_db[0].event,
                    student=registration_owner
                )
            else:
                registration = Registration.objects.get(
                    student=registration_owner,
                    event=order_items_from_db[0].event
                )
            transaction = Transaction.objects.create(
                registration=registration,
            )
            for item in order_items_from_db:
                transaction.programs_selected.add(item)
                transaction.events_selected_json[item.name] = item.reg_fee
                transaction.value += item.reg_fee
                if request.user.is_superuser:
                    registration_owner.registered_programs.add(item)
            if request.user.is_superuser:
                transaction.status = "TXN_SUCCESS"
                transaction.spot = True
                transaction.registration.made_successful_transaction = True
                transaction.raw_response = f"This transaction was created manually by registration admin: " \
                                           f"{request.user.email}\n The payment was collected and verified offline "
                transaction.registration.save()
            transaction.save()
            if request.user.is_superuser:
                return render(request, self.template_name, {"created": True})
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


class ZephyrusProgramsView(LoginRequiredMixin, View):
    template_name = "dashboard/programs.html"

    def get(self, request, event_link):
        event = get_object_or_404(Event, link=event_link)
        return render(request, self.template_name, {"programs": event.program_set.all()})


class ZephyrusScheduleView(LoginRequiredMixin, View):
    template_name = "dashboard/schedule.html"

    def get(self, request, event_link):
        event_days = EventDay.objects.filter(event__link=event_link).order_by('date')
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
                    for program in transaction.programs_selected.all():
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
                    transaction.date = datetime.strptime(
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


class MyRegistrationDetailView(LoginRequiredMixin, View):
    model = Registration

    def get(self, request, event_link):
        registration = get_object_or_404(self.model, event__link=event_link, student=request.user.student)
        return render(request, "dashboard/registration_details.html", {"registration": registration})


class AdminRegistrationDetailView(LoginRequiredMixin, View):

    def get(self, request, reg_id=None):
        if request.user.is_staff:
            try:
                registration = Registration.objects.get(id=reg_id)
            except Registration.DoesNotExist:
                registration = None
            if request.GET.get("allot") == 'true':
                registration.physical_id_allotted = True
                registration.save()
                return render(request,
                              "dashboard/extendable/registration-detail-section.html", {"registration": registration})
            if request.GET.get("ajax") == 'true':
                return render(request,
                              "dashboard/extendable/registration-detail-section.html", {"registration": registration})
            return render(request, "dashboard/admin/registration-details.html", {"registration": registration})
        return render(request, "web/404.html")


class AdminRegistrationDataView(LoginRequiredMixin, View):

    def get(self, request, event_link):
        if request.user.is_staff:
            event = get_object_or_404(Event, link=event_link)
            if request.user.is_superuser and request.GET.get("type"):
                workbook = xlwt.Workbook()
                sheet = workbook.add_sheet("registrations", cell_overwrite_ok=True)
                i = 1
                if request.GET.get("type") == "all":
                    registrations = event.successful_registrations
                    write_sheet(sheet, 0, "Reg ID",
                                "Name", "Phone", "Email",
                                "College", "Registered Programs",
                                "Online", "Spot")
                    for registration in registrations:
                        write_sheet(sheet, i, registration.id,
                                    registration.student.name,
                                    registration.student.phone_number,
                                    registration.student.user.email,
                                    registration.student.college_name,
                                    registration.student.registered_programs_str,
                                    registration.online_transaction_value,
                                    registration.spot_transaction_value)
                        i += 1
                    workbook.save(f"media/{event_link}/{event_link}-registrations.xls")
                    response = HttpResponse()
                    del response['Content-Type']
                    response['X-Accel-Redirect'] = "/protected/media/" + f"{event_link}/{event_link}-registrations.xls"
                    response['Content-Disposition'] = f"attachment; filename={event_link}-registrations.xls"
                    return response
                elif request.GET.get("type") == "individual":
                    write_sheet(sheet, 0, "Reg ID",
                                "Name", "Phone", "Email",
                                "College", "Online", "Spot")
                    program_id = request.GET.get("program_id")
                    program = Program.objects.get(id=program_id)
                    transactions = program.transactions.filter(status="TXN_SUCCESS")
                    for transaction in transactions:
                        write_sheet(sheet, i, transaction.registration.id,
                                    transaction.registration.student.name,
                                    transaction.registration.student.phone_number,
                                    transaction.registration.student.user.email,
                                    transaction.registration.student.college_name,
                                    transaction.registration.online_transaction_value,
                                    transaction.registration.spot_transaction_value)
                        i += 1
                    workbook.save(f"media/{event_link}/{program.name}-registrations.xls")
                    response = HttpResponse()
                    del response['Content-Type']
                    response['X-Accel-Redirect'] = "/protected/media/" + f"{event_link}/{program.name}-registrations.xls"
                    response['Content-Disposition'] = f"attachment; filename={program.name}-registrations.xls"
                    return response
                else:
                    pass
            return render(request, "dashboard/admin/registration-data.html", {"event": event})
        return render(request, "web/404.html")
