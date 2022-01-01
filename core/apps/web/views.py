import hashlib

import xlwt

from django.shortcuts import render, redirect

from .models import Course, Faculty, Message, Gallery, Batch, Tag, IpHash, PopUp
from core.apps.dashboard.models import Event, Registration, Program
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from ipware import get_client_ip


def zephyrus_redirect(request):
    return redirect(to="https://dashboard.christcs.in")


class IndexView(View):
    def get(self, request):
        context = {}
        context["upcoming_events"] = Event.objects.filter(status="upcoming")
        context["messages"] = Message.objects.all()[:3]
        ip, is_routable = get_client_ip(request)
        if is_routable:
            ip_hash = hashlib.md5(str.encode(ip)).hexdigest()[:10]
            if not IpHash.objects.filter(hash=ip_hash).exists():
                IpHash.objects.create(
                    hash=ip_hash
                )
                context["first_popup"] = PopUp.objects.last()
                context["popups"] = PopUp.objects.all().order_by('-id')[1:]
        return render(request, "web/index.html", context)


def about_view(request):
    return render(request, "web/about.html")


def lazy_load_faculty(request):
    faculties = Faculty.objects.all()
    return render(request, "web/faculty-lazyload.html", {"faculties": faculties})


class EventView(View):
    model = Event
    template_name = "web/event-details.html"

    def get(self, request, slug=None):
        if slug:
            try:
                event = self.model.objects.get(link=slug)
                return render(request, self.template_name, {"event": event})
            except self.model.DoesNotExist:
                return render(request, "web/404.html")
        else:
            events = Event.objects.all()
            return render(request, "web/events.html", {"events": events})


class CourseView(View):
    model = Course
    template_name = "web/course-details.html"

    def get(self, request, slug):
        try:
            course = self.model.objects.get(link=slug)
            return render(request, self.template_name, {"course": course})
        except self.model.DoesNotExist:
            return render(request, "web/404.html")


class GalleryListView(ListView):
    template_name = "web/gallery.html"
    model = Gallery
    paginate_by = 12
    queryset = model.objects.order_by('-date')
    extra_context = {"tags": Tag.objects.all()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = sorted(set([date[0].year for date in self.queryset.values_list('date')]), reverse=True)
        return context


class AlumniListView(ListView):
    template_name = "web/alumni.html"
    model = Batch
    paginate_by = 3
    queryset = Batch.objects.order_by('-year')


class AdminUserDataView(LoginRequiredMixin, View):

    def get(self, request, reg_id=None):
        if request.user.is_staff:
            try:
                registration = Registration.objects.get(id=reg_id)
            except Registration.DoesNotExist:
                registration = None
            if request.GET.get("ajax") == 'true':
                return render(request, "web/extendable/user-data-section.html", {"registration": registration})
            return render(request, "web/user-data.html", {"registration": registration})
        return render(request, "web/404.html")


def write_sheet(sheet, row, *args):
    for item in args:
        sheet.write(row, args.index(item), item)


class AdminRegistrationCountView(LoginRequiredMixin, View):

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
            return render(request, "web/registration-count.html", {"programs": programs})
        return render(request, "web/404.html")
