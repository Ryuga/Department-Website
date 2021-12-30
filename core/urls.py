from django.contrib import admin
from django.urls import path, include
from core.apps.web.views import AdminUserDataView

urlpatterns = [
    path('data/users/qr/<str:reg_id>/', AdminUserDataView.as_view()),
    path('data/users/', AdminUserDataView.as_view()),
    path('', admin.site.urls),
]
