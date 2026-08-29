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
        "new-tutoring-session",
        views.new_tutoring_session_view,
        name="tutoring-session-new",
    ),
    path(
        "sessions/<int:session_pk>",
        views.session_detail_view,
        name="session-detail",
    ),
    path(
        "sessions/<int:session_pk>/edit",
        views.session_edit_view,
        name="session-edit",
    ),
    path(
        "sessions/<int:session_pk>/join",
        views.session_join,
        name="session-join",
    ),
    path(
        "sessions/<int:session_pk>/delete",
        views.session_delete,
        name="session-delete",
    ),
    path(
        "sessions/<int:session_pk>/<int:participation_pk>/accept",
        views.accept_join_request,
        name="session-accept",
    ),
    path(
        "sessions/<int:session_pk>/<int:participation_pk>/reject",
        views.reject_join_request,
        name="session-reject",
    ),
    path("sessions/events", views.session_events, name="session-events"),
]
