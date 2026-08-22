from django.urls import path

from qa import views

app_name = "qa"

urlpatterns = [
    path("", views.question_list_view, name="question-list"),
    path("ask", views.question_ask_view, name="question-ask"),
    path("<int:question_pk>", views.question_detail_view, name="question-detail"),
    path("<int:question_pk>/upvote", views.question_upvote, name="upvote-question"),
]
