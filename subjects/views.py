from typing import override

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Exists, OuterRef
from django.forms.models import ModelForm
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView
from django_tomselect.app_settings import Const, TomSelectConfig
from django_tomselect.autocompletes import AutocompleteModelView
from django_tomselect.forms import TomSelectModelChoiceField

from subjects.models import Subject, SubjectMembership, Topic
from subjects.utils import is_moderator


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
    pk_url_kwarg = "subject"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        obj.membership = SubjectMembership.objects.filter(
            user=self.request.user, subject=obj
        ).first()

        return obj


def topic_list_view(request, subject_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = (
        SubjectMembership.objects.filter(user=request.user, subject=subject).first()
        if subject
        else None
    )
    topics = Topic.objects.filter(subject=subject_pk)

    return render(
        request,
        "subjects/topic_list.html",
        {"subject": subject, "membership": membership, "topics": topics},
    )


class TopicAutocompleteView(AutocompleteModelView):
    model = Topic
    search_lookups = ["name__icontains", "description__icontains"]
    virtual_fields = ["path"]

    def hook_prepare_results(self, results):
        lookup = {
            topic["id"]: topic
            for topic in self.get_queryset().values("id", "name", "parent_id")
        }

        for row in results:
            crumbs = []
            seen = set()
            node = lookup.get(row["id"])  # leaf node
            while node and node["id"] not in seen:
                crumbs.append(node["name"])
                seen.add(node["id"])
                node = lookup.get(node["parent_id"])

            row["path"] = " › ".join(crumbs[::-1])

        return results


class CreateTopicForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Topic
        fields = ["name", "description", "parent"]
        widgets = {"description": Textarea()}

    def __init__(self, *args, subject_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id = subject_id

        self.fields["parent"] = TomSelectModelChoiceField(
            required=False,
            label="Parent topic",
            help_text="The broader topic that this topic is a sub-topic for.",
            config=TomSelectConfig(
                url="subjects:autocomplete-topic",
                placeholder="Select a topic...",
                filter_by=[Const(subject_id, "subject_id")],
                label_field="path",
            ),
        )

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and parent.subject_id != self.subject_id:
            raise forms.ValidationError(
                "That topic doesn't belong to the selected subject"
            )
        return parent


@is_moderator
def topic_create_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    preset_topic = Topic(subject_id=subject_pk)
    form = CreateTopicForm(
        request.POST or None, instance=preset_topic, subject_id=subject_pk
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("subjects:topic-list", subject_pk)

    return render(
        request,
        "subjects/topic_create_form.html",
        {"form": form, "subject": subject},
    )


@require_POST
def subject_toggle_membership(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership, created = SubjectMembership.objects.get_or_create(
        subject=subject, user=request.user
    )

    if not created:
        membership.delete()

    response = HttpResponse()
    response.headers["HX-Refresh"] = "true"

    return response
