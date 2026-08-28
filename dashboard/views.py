from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView
from haystack.generic_views import SearchView

from subjects.models import Subject


class Index(ListView):
    model = Subject
    context_object_name = "subjects"
    template_name = "dashboard/index.html"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(members=self.request.user)

        return qs


def profile_view(request):
    return render(request, "dashboard/profile.html", {})


def settings_view(request):
    return render(request, "dashboard/settings.html", {})


def help_view(request):
    return render(request, "dashboard/help.html", {})
