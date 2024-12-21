import os
import json
import pytz
import xlwt
from datetime import datetime, timezone, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseForbidden
from utils.google_oauth2 import GoogleOauth
from utils.mixins import ResponseMixin
from utils.operations import create_user, write_sheet
from utils.functions import generate_css_text_animation
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.paytm_checksum import generateSignature, verifySignature
from utils.payment_handler import PaytmPaymentHandler
from .models import Program, Slideshow, Registration, Transaction, Event, EventDay, Student, SiteSetting
from core.apps.dashboard.tasks import send_registration_email, remove_account_restriction

google_oauth = GoogleOauth(redirect_uri=settings.OAUTH_REDIRECTION_URL)
google_oauth_url, _ = google_oauth.flow.authorization_url()
paytm = PaytmPaymentHandler()


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
        context = {}
        context["google_oauth_url"] = google_oauth_url
        context['upcoming_events_with_registration_open'] = Event.upcoming_events_with_registration_open()
        if context['upcoming_events_with_registration_open']:
            context['generated_css'] = generate_css_text_animation(context['upcoming_events_with_registration_open'])
        return render(request, self.template_name, context)


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
                user = User.objects.get(username=email)
                login(request, user)
                return redirect(to="/")
            except User.DoesNotExist:
                user = create_user(email=email, avatar_url=avatar, access_token=access_token, name=name)
                login(request, user)
                return redirect(to="/")
        else:
            return self.http_response_404(request)


class DashView(LoginRequiredMixin, View):
    template_name = "dashboard/index.html"

    def get(self, request):
        slideshow = Slideshow.objects.all().order_by('order')
        return render(request, self.template_name, {"slideshow": slideshow, "settings": SiteSetting.load()})


class UserProfileView(LoginRequiredMixin, View):
    template_name = "dashboard/user-profile.html"
    fields = (
        "name", "phone_number", "college_name", "department"
    )

    def get(self, request):
        return render(request, self.template_name, {"settings": SiteSetting.load()})

    def post(self, request):
        if request.user.student.restricted:
            return render(request, self.template_name, {"restricted": True, "saved": False, "settings": SiteSetting.load()})
        saved = False
        student = request.user.student
        for field in self.fields:
            if request.POST.get(field):
                setattr(student, field, request.POST.get(field))
        if (datetime.now(timezone.utc) - request.user.student.last_updated).total_seconds() < 5:
            student.anomalous_update_count += 1
            if student.anomalous_update_count > 5:
                student.restricted = True
                remove_account_restriction.apply_async((student.user.username,),
                                                       eta=datetime.now(timezone.utc) + timedelta(hours=1))
        student.last_updated = datetime.now(timezone.utc)
        student.save()
        saved = True
        if request.POST.get("initial"):
            student.completed_profile_setup = True
            student.save()
            return redirect("/")
        return render(request, self.template_name, {"saved": saved, "settings": SiteSetting.load()})


class SettingsView(LoginRequiredMixin, View, ResponseMixin):
    template_name = "dashboard/settings.html"

    def get(self, request):
        return render(request, self.template_name, {"restricted": request.user.student.restricted,
                                                    "settings": SiteSetting.load()})

    def delete(self, request):
        if request.user.student.active_registrations():
            return HttpResponse(status=403)
        else:
            accounts_created = User.objects.filter(email=request.user.email)
            if len(accounts_created) > 2:
                request.user.student.restricted = True
                request.user.student.save()
                return HttpResponse(status=406)
            request.user.username = request.user.username + "--" + str(len(accounts_created) - 1) + "--deleted"
            request.user.is_active = False
            request.user.save()
            return HttpResponse(status=200)


class EventRegistrationView(LoginRequiredMixin, View, ResponseMixin):
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
                    student = Student.objects.get(user__username=email)
                    registered_programs = student.registered_programs.all()
                    programs = [
                        program for program in all_programs if program not in registered_programs
                    ]
                except Student.DoesNotExist:
                    does_not_exist = True
                return render(request, "dashboard/extendable/registration_card.html", {"programs": programs,
                                                                                       "does_not_exist": does_not_exist,
                                                                                       "settings": SiteSetting.load()
                                                                                       })
        else:
            registered_programs = request.user.student.registered_programs.all()
            programs = [
                program for program in all_programs if program not in registered_programs
            ]
        created = self.request.session.pop('createdRegistration', False)
        return render(request, self.template_name, {"programs": programs,
                                                    "event": event,
                                                    "settings": SiteSetting.load(),
                                                    "created": created
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
            registration_owner = User.objects.get(username=request.POST.get("recipientEmail")).student
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
                creation_time=datetime.now(pytz.timezone('Asia/Kolkata'))
            )
            for item in order_items_from_db:
                transaction.programs_selected.add(item)
                transaction.events_selected_json[item.name] = item.reg_fee
                transaction.value += item.reg_fee
                if request.user.is_superuser or cost_total == 0:
                    registration_owner.registered_programs.add(item)
            if request.user.is_superuser:
                registration_owner.restricted = False
                registration_owner.save()
                transaction.status = "TXN_SUCCESS"
                transaction.spot = True
                transaction.registrar = request.user.student
                transaction.registration.made_successful_transaction = True
                transaction.raw_response = f"This transaction was created manually by registration admin: " \
                                           f"{request.user.email}\n The payment was collected and verified offline "
                transaction.date = datetime.now(pytz.timezone('Asia/Kolkata'))
                transaction.mode = "Spot Registration"
                transaction.registration.save()
            if transaction.value == 0:
                registration_owner.save()
                transaction.status = "TXN_SUCCESS"
                transaction.date = datetime.now(pytz.timezone('Asia/Kolkata'))
                transaction.registration.made_successful_transaction = True
                transaction.registration.save()
            transaction.save()
            if request.user.is_superuser or transaction.value == 0:
                for program in transaction.programs_selected.all():
                    if not program.registration_limit == -1:
                        registration_count = Transaction.objects.filter(
                            registration__event=order_items_from_db[0].event,
                            status="TXN_SUCCESS",
                            programs_selected__in=[program]
                        ).count()
                        if registration_count >= program.registration_limit:
                            program.online_registration_open = False
                            program.spot_registration_open = False
                            program.save()
                try:
                    send_registration_email.delay(transaction_id=transaction.id)
                except Exception as E:
                    print(E)
                if request.user.is_authenticated:
                    request.session["createdRegistration"] = True
                return redirect("registration", event_link=order_items_from_db[0].event.link)

            initiation_response = paytm.initiate_transaction(transaction)
            print(initiation_response)

            param_dict = {
                "orderId": str(transaction.id),
                "txnToken": initiation_response.get("txnToken"),
                "mid": settings.PAYTM_MERCHANT_ID
            }

            return render(request, "dashboard/payments/paytm_payments.html",
                          {"data": param_dict,
                           "paytm_process_transaction_url": paytm.generate_payments_page_url(transaction)
                           }
                          )
        else:
            return self.json_response_401()


class EventProgramsView(LoginRequiredMixin, View):
    template_name = "dashboard/programs.html"

    def get(self, request, event_link):
        event = get_object_or_404(Event, link=event_link)
        return render(request, self.template_name, {"programs": event.program_set.all(), "settings": SiteSetting.load()})


class EventScheduleView(LoginRequiredMixin, View):
    template_name = "dashboard/schedule.html"

    def get(self, request, event_link):
        event_days = EventDay.objects.filter(event__link=event_link).order_by('date')
        return render(request, self.template_name, {"event_days": event_days, "settings": SiteSetting.load()})


@csrf_exempt
def payment_handler(request):
    response_dict = request.POST.dict() or "No Response received"
    checksum_hash = request.POST.get("CHECKSUMHASH") or "No checksum hash"
    transaction_id = request.POST.get("ORDERID")
    if transaction_id:
        try:
            transaction = Transaction.objects.get(id=request.POST.get("ORDERID"))
            verify = verifySignature(response_dict, settings.PAYTM_MERCHANT_KEY, checksum_hash)
            if verify:
                transaction.raw_response = response_dict
                if response_dict['RESPCODE'] == '01':
                    transaction.registration.made_successful_transaction = True
                    for program in transaction.programs_selected.all():
                        transaction.registration.student.registered_programs.add(program)
                    transaction.registration.student.restricted = False
                    transaction.registration.student.save()
                    transaction.registration.save()
                    try:
                        send_registration_email.delay(transaction_id=transaction.id)
                    except Exception as E:
                        print(E)
                else:
                    transaction.status = "FAILED"
                    transaction.failure_msg = response_dict.get("RESPMSG")
                if request.POST.get("TXNID"):
                    transaction.paytm_transaction_id = request.POST.get("TXNID")
                    transaction.bank_transaction_id = request.POST.get("BANKTXNID")
                transaction.value = request.POST.get("TXNAMOUNT")
                transaction.mode = request.POST.get("PAYMENTMODE", "Online")
                if request.POST.get("STATUS"):
                    transaction.status = request.POST.get("STATUS")
                if request.POST.get("TXNDATE"):
                    transaction.date = datetime.strptime(
                        request.POST.get("TXNDATE")[:19], "%Y-%m-%d %H:%M:%S") \
                        .replace(
                        tzinfo=pytz.timezone('Asia/Kolkata')
                    )
                transaction.save()
                if transaction.status == "TXN_SUCCESS":
                    for program in transaction.programs_selected.all():
                        if not program.registration_limit == -1:
                            registration_count = Transaction.objects.filter(
                                registration__event=program.event,
                                status="TXN_SUCCESS",
                                programs_selected__in=[program]
                            ).count()
                            if registration_count >= program.registration_limit:
                                program.online_registration_open = False
                                program.spot_registration_open = False
                                program.save()
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

    return render(request, "dashboard/payments/payment_status_new.html", {"response": response_dict})


class MyRegistrationDetailView(LoginRequiredMixin, View):
    model = Registration

    def get(self, request, event_link):
        registration = get_object_or_404(self.model, event__link=event_link, student=request.user.student)
        return render(request, "dashboard/registration_details.html", {"registration": registration,
                                                                       "settings": SiteSetting.load()})


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
                    if not os.path.isdir(f"media/{event_link}/"):
                        os.mkdir(f"media/{event_link}/")
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
                    response[
                        'X-Accel-Redirect'] = "/protected/media/" + f"{event_link}/{program.name}-registrations.xls"
                    response['Content-Disposition'] = f"attachment; filename={program.name}-registrations.xls"
                    return response
                else:
                    pass
            spot_registrars = User.objects.filter(is_superuser=True)
            return render(request, "dashboard/admin/registration-data.html",
                          {"event": event, "spot_registrars": spot_registrars})
        return render(request, "web/404.html")


class AdminTabularView(LoginRequiredMixin, View):
    model = Program

    def get(self, request, program_id):
        if request.user.is_superuser:
            program = get_object_or_404(self.model, id=program_id)
            return render(request, "dashboard/admin/tabular-view.html", {"program": program})
        return render(request, "web/404.html")


class InstagramRedirectionView(View):
    def get(self, request):
        return render(request, "web/instagram-redirect.html")
