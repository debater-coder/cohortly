from django.urls import path

from tutoring import views

app_name = "tutoring"

urlpatterns = [path("", views.session_list_view, name="session-list")]
