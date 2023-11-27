from django.urls import path

from .views import register, login

urlpatterns = [path("user_register", register), path("user_login", login)]
