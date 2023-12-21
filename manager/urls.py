from django.urls import path

from .views import *

urlpatterns = [
    path("manager_register", register),
    path("manager_login", login),
    path("get_all_user", get_all_user),
    path("get_single_user", get_single_user),
    path("user_delete", user_delete),
    path("apply_modify_condition", apply_modify_condition),
    path("get_all_apply", get_all_apply),
    path("apply_refuse_condition", apply_refuse_condition),
]
