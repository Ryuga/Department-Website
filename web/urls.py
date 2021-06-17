from django.urls import path
from .views import index_view, EventView


urlpatterns = [
    path('', index_view, name="home"),
    path('events/<str:slug>', EventView.as_view()),
    path('events/', EventView.as_view())
]
