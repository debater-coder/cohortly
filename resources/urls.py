from django.urls import path

from resources import views

app_name = "resources"

urlpatterns = [
    path("", views.resources_list_view, name="resource-list"),
    path("new", views.resources_upload_view, name="resource-new"),
    path("<int:resource_pk>", views.resource_detail_view, name="resource-detail"),
    path("<int:resource_pk>/edit", views.resources_edit_view, name="resource-edit"),
    path("<int:resource_pk>/delete", views.resource_delete, name="resource-delete"),
    path("<int:resource_pk>/upvote", views.resource_upvote, name="upvote-resource"),
]
