from django.urls import include, path

from tutoring.views import all_session_events

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.SubjectsListView.as_view(), name="subject-list"),
    path("<int:subject_pk>/", views.SubjectDetailView.as_view(), name="subject-detail"),
    path(
        "<int:subject_pk>/toggle-membership",
        views.subject_toggle_membership,
        name="subject-toggle-membership",
    ),
    path("<int:subject_pk>/topics", views.topic_list_view, name="topic-list"),
    path(
        "<int:subject_pk>/topics/<int:topic_pk>",
        views.topic_detail_view,
        name="topic-detail",
    ),
    path(
        "<int:subject_pk>/topics/create",
        views.topic_create_view,
        name="topic-create",
    ),
    path(
        "<int:subject_pk>/topics/delete/<topic_pk>",
        views.topic_delete,
        name="topic-delete",
    ),
    path(
        "<int:subject_pk>/topics/edit/<topic_pk>",
        views.topic_edit_view,
        name="topic-edit",
    ),
    path(
        "<int:subject_pk>/topics/reorder",
        views.topic_reorder_view,
        name="topic-reorder",
    ),
    path(
        "autocomplete/topics",
        views.TopicAutocompleteView.as_view(),
        name="autocomplete-topic",
    ),
    path("<int:subject_pk>/qa/", include("qa.urls")),
    path("<int:subject_pk>/tutoring/", include("tutoring.urls")),
    path("tutoring", all_session_events, name="all-session-events"),
]
