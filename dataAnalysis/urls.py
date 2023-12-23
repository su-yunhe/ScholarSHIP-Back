from django.urls import path

from .views import *

urlpatterns = [
    path("get_author_college", get_author_college),
    path("get_author_partner", get_author_partner),
    path("get_site_num", get_site_num),
    path("get_institution_basic", get_institution_basic),
    path("get_institution_range", get_institution_range),
    path("get_institution_authors", get_institution_authors),
    path("get_main_basic", get_main_basic),
    path("single_work_analysis", single_work_analysis),
    path("muti_work_analysis", muti_work_analysis),
]
