from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("", views.ai_assistant, name="assistant"),
]
