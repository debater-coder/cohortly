from django.urls import path
from haystack.forms import HighlightedModelSearchForm
from haystack.views import SearchView, search_view_factory

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path(
        "search",
        search_view_factory(
            view_class=SearchView,
            template="dashboard/search.html",
            form_class=HighlightedModelSearchForm,
        ),
        name="search",
    ),
    path("profile", views.profile_view, name="profile"),
    path("settings", views.settings_view, name="settings"),
    path("help", views.help_view, name="help"),
]
