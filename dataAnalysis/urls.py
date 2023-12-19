from django.urls import path

from .views import *

urlpatterns = [
    path("get_author_college", get_author_college),
    path("get_author_partner", get_author_partner),
]
