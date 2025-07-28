from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    # path(
    #     "register/",
    #     auth_views.LoginView.as_view(template_name="users/register.html"),
    #     name="register",
    # ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
