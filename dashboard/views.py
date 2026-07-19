from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView

from subjects.models import Subject


class Index(ListView):
    model = Subject
    context_object_name = "subjects"
    template_name = "dashboard/index.html"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(members=self.request.user)

        return qs
