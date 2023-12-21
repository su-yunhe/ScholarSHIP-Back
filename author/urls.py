# publish/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('get_scholar', get_scholar),
    path('get_scholar_papers', get_scholar_papers),
    path('get_scholar_institutions', get_scholar_institutions)
]