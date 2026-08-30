from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView
from haystack.generic_views import SearchView

from subjects.models import Subject


class Index(ListView):
    """View that shows a list of the users' joined subjects on the dashboard, alongside the grade calendar."""

    model = Subject
    context_object_name = "subjects"
    template_name = "dashboard/index.html"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(members=self.request.user)

        return qs


def profile_view(request):
    """View that shows a user's profile"""
    return render(request, "dashboard/profile.html", {})


def settings_view(request):
    """View that shows user settings"""
    return render(request, "dashboard/settings.html", {})


def help_view(request):
    """View that shows the help centre"""
    return render(request, "dashboard/help.html", {})
