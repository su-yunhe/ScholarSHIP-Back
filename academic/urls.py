from django.urls import path

from .views import *

urlpatterns = [
    path("get_relation_map", get_relation_map),
    path("get_works", get_works),
    path("get_detail", get_detail),
    path("change_status", change_status),
    path("get_citation", get_citation),
    path("get_referenced_related", get_referenced_related),
    path("get_works_count", get_works_count),
]
