from django.urls import path
from . import views

app_name = "history"

urlpatterns = [
    path("", views.history, name="history"),
    path("log/", views.log_outfit, name="log_outfit"),
]
