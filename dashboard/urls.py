from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("search", views.search_view, name="search"),
    path("profile", views.profile_view, name="profile"),
    path("settings", views.settings_view, name="settings"),
]
