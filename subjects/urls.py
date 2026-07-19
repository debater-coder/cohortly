from django.urls import path

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.SubjectsListView.as_view(), name="subject-list"),
    path("<int:pk>/", views.SubjectDetailView.as_view(), name="subject-detail"),
    path(
        "<int:pk>/toggle-membership",
        views.subject_toggle_membership,
        name="subject-toggle-membership",
    ),
]
