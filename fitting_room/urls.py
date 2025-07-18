from django.urls import path
from . import views

app_name = "fitting_room"

urlpatterns = [
    path("", views.fitting_room, name="fitting_room"),
    path("lookbook/", views.lookbook, name="lookbook"),
    path("lookbook/delete/<int:look_id>/", views.delete_look, name="delete_look"),
    path("test/", views.test, name="test"),
]
