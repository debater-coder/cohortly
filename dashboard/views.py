from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView
from modelsearch.query import Fuzzy

from qa.models import Answer, Question
from subjects.models import Subject, Topic


class Index(ListView):
    model = Subject
    context_object_name = "subjects"
    template_name = "dashboard/index.html"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(members=self.request.user)

        return qs


def search_view(request):
    search_string = request.GET.get("q", "")
    context = {}
    context["search_string"] = search_string
    if search_string:
        context["subjects"] = Subject.objects.search(search_string)
        context["topics"] = Topic.objects.search(search_string)
        context["questions"] = Question.objects.search(search_string)
        context["answers"] = Answer.objects.search(search_string)

    return render(request, "dashboard/search.html", context)


def profile_view(request):
    return render(request, "dashboard/profile.html", {})


def settings_view(request):
    return render(request, "dashboard/settings.html", {})


def help_view(request):
    return render(request, "dashboard/help.html", {})
