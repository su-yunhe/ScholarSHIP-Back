from django.urls import path
from .views import *
urlpatterns = [
    path("SearchManager/SearchWork", SearchWork),
    path("SearchManager/SearchTopAuthor", getTopAuthor),
    path("SearchManager/SearchTopInstitution", getTopInstitution),
    path("SearchManager/SearchTopConcept", getTopConcept),
    path("SearchManager/AdvancedSearchWork", AdvancedSearchWork),
    path("SearchManager/FilterWork", FilterWork),
    path("SearchManager/WorkLocation", getWorkLocation),
    path("SearchManager/DownloadWork", DownloadWork),
    path("SearchManager/SearchAuthor", SearchAuthor),
    path("SearchManager/SearchInstitution", SearchInstitution),
]