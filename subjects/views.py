from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from subjects.models import Subject, SubjectMembership


class SubjectsListView(ListView):
    model = Subject
    context_object_name = "subjects"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.annotate(member_count=Count("members", distinct=True))

        membership = SubjectMembership.objects.filter(
            subject=OuterRef("pk"),
            user=self.request.user,
        )

        qs = qs.annotate(is_member=Exists(membership))

        return qs


class SubjectDetailView(DetailView):
    model = Subject
    context_object_name = "subject"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        obj.membership = SubjectMembership.objects.filter(
            user=self.request.user, subject=obj
        ).first()

        return obj


@require_POST
def subject_toggle_membership(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    membership, created = SubjectMembership.objects.get_or_create(
        subject=subject, user=request.user
    )

    if not created:
        membership.delete()

    response = HttpResponse()
    response.headers["HX-Refresh"] = "true"

    return response
