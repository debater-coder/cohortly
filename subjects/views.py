from typing import override

import nh3
from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Exists, OuterRef
from django.forms.models import ModelForm
from django.forms.widgets import Textarea
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView
from django_tomselect.app_settings import Const, TomSelectConfig
from django_tomselect.autocompletes import AutocompleteModelView
from django_tomselect.forms import TomSelectModelChoiceField
from markdownx.utils import markdownify

from cohortly.markdown_utils import safe_markdownify
from subjects.models import Subject, SubjectMembership, Topic
from subjects.utils import get_topic_lookup, get_topic_path, is_moderator


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


class TopicAutocompleteView(AutocompleteModelView):
    model = Topic
    search_lookups = ["name__icontains", "description__icontains"]
    virtual_fields = ["path"]
    value_fields = ["path", "name"]

    def hook_prepare_results(self, results):
        lookup = get_topic_lookup(self.get_queryset())

        for row in results:
            crumbs = get_topic_path(lookup, row["id"])
            row["path"] = " › ".join([crumb["name"] for crumb in crumbs])

        return results


class TopicForm(ModelForm):
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


def topic_list_view(request, subject_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = (
        SubjectMembership.objects.filter(user=request.user, subject=subject).first()
        if subject
        else None
    )
    topics = Topic.objects.filter(subject=subject_pk, parent__isnull=True)

    return render(
        request,
        "subjects/topic_list.html",
        {"subject": subject, "membership": membership, "topics": topics},
    )


def topic_detail_view(request, subject_pk, topic_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    topic = get_object_or_404(Topic, pk=topic_pk)
    membership = (
        SubjectMembership.objects.filter(user=request.user, subject=subject).first()
        if subject
        else None
    )
    topics = Topic.objects.filter(subject=subject_pk, parent_id=topic_pk)

    lookup = get_topic_lookup(Topic.objects.get_queryset())
    path = get_topic_path(lookup, topic_pk)

    return render(
        request,
        "subjects/topic_list.html",
        {
            "subject": subject,
            "membership": membership,
            "topics": topics,
            "topic_path": path,
            "topic": topic,
            "content": safe_markdownify(topic.description),
        },
    )


@is_moderator
def topic_create_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    preset_topic = Topic(subject_id=subject_pk)
    form = TopicForm(request.POST or None, instance=preset_topic, subject_id=subject_pk)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("subjects:topic-list", subject_pk)

    return render(
        request,
        "subjects/topic_form.html",
        {"form": form, "subject": subject},
    )


@is_moderator
def topic_edit_view(
    request,
    subject_pk: int,
    topic_pk: int,
):
    subject = get_object_or_404(Subject, pk=subject_pk)
    topic = get_object_or_404(Topic, pk=topic_pk)
    form = TopicForm(request.POST or None, instance=topic, subject_id=subject_pk)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("subjects:topic-detail", subject_pk, topic_pk)

    return render(
        request,
        "subjects/topic_form.html",
        {"form": form, "subject": subject},
    )


@require_POST
def topic_delete(
    request,
    subject_pk: int,
    topic_pk: int,
):
    topic = get_object_or_404(Topic, pk=topic_pk)
    membership = get_object_or_404(
        SubjectMembership, subject_id=topic.subject.id, user=request.user
    )

    if subject_pk != topic.subject.id:
        raise Http404()

    if not membership.moderator:
        raise PermissionDenied("You must be a moderator to perform this action")

    topic.delete()
    response = HttpResponse()
    response.headers["HX-Redirect"] = reverse("subjects:topic-list", args=[subject_pk])
    return response


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
