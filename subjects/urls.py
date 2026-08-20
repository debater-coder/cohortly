from django.urls import path

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.SubjectsListView.as_view(), name="subject-list"),
    path("<int:subject>/", views.SubjectDetailView.as_view(), name="subject-detail"),
    path(
        "<int:subject>/toggle-membership",
        views.subject_toggle_membership,
        name="subject-toggle-membership",
    ),
    path("<int:subject_pk>/topics", views.topic_list_view, name="topic-list"),
    path(
        "<int:subject_pk>/topics/create",
        views.topic_create_view,
        name="topic-create",
    ),
    path(
        "autocomplete/topics",
        views.TopicAutocompleteView.as_view(),
        name="autocomplete-topic",
    ),
]
