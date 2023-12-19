from django.urls import path

from .views import *

urlpatterns = [
    path("get_relation_map", get_relation_map),
    path("get_works", get_works),
    path("get_detail", get_detail),
    path("change_status", change_status),
]
