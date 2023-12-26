from django.urls import path

from .views import *

urlpatterns = [
    path("user_register", register),
    path("user_login", login),
    path("concern_add", concern_add),
    path("concern_delete", concern_delete),
    path("get_all_concern", get_all_concern),
    path("get_single_concern", get_single_concern),
    path("label_star_add", label_star_add),
    path("label_star_get_all", label_star_get_all),
    path("label_star_get_single", label_star_get_single),
    path("label_delete", label_delete),
    path("star_add", star_add),
    path("star_get_all", star_get_all),
    path("star_get_single", star_get_single),
    path("star_delete", star_delete),
    path("history_add", history_add),
    path("History_get_all", History_get_all),
    path("History_get_single", History_get_single),
    path("History_delete_single", History_delete_single),
    path("History_delete_all", History_delete_all),
    path("apply_add", apply_add),
    path("get_user_info", get_user_info),
    path("judge_concern", judge_concern),
    path("judge_scholar", judge_scholar),
    path("judge_authenticated", judge_authenticated),
    path("scholar_get_user", scholar_get_user),
]
