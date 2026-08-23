from django.urls import path

from tutoring import views

app_name = "tutoring"

urlpatterns = [
    path("", views.session_list_view, name="session-list"),
    path(
        "new-group-session",
        views.new_group_study_session_view,
        name="group-session-new",
    ),
    path(
        "sessions/<int:session_pk>",
        views.session_detail_view,
        name="session-detail",
    ),
]
