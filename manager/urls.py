from django.urls import path

from .views import register, login

urlpatterns = [path("manager_register", register), path("manager_login", login)]
