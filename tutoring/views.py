from django import forms
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django_tomselect.app_settings import Const, TomSelectConfig
from django_tomselect.forms import (
    TomSelectModelMultipleChoiceField,
)

from subjects.models import Subject, SubjectMembership
from tutoring.models import Session


class SessionForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Session
        fields = ["title", "location", "capacity", "topics", "start_time", "end_time"]
        help_texts = {
            "location": "A physical location or meeting link",
            "capacity": "The maximum number of students who can join this session",
            "topics": "The specific topics this session will focus on",
        }
        widgets = {
            "start_time": forms.DateTimeInput(
                {"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                {"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, subject_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id = subject_id
        self.fields["topics"] = TomSelectModelMultipleChoiceField(
            config=TomSelectConfig(
                url="subjects:autocomplete-topic",
                placeholder="Select one or more topics:",
                filter_by=[Const(subject_id, "subject_id")],
                label_field="path",
            )
        )

    def clean_topics(self):
        topics = self.cleaned_data["topics"]

        for topic in topics:
            if topic.subject_id != self.subject_id:
                raise forms.ValidationError(
                    "That topic doesn't belong to the selected subject"
                )
        return topics


def session_list_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    group_sessions = Session.objects.filter(
        subject=subject, needs_join_requests=False
    ).order_by("start_time")

    return render(
        request,
        "tutoring/session_list.html",
        {
            "subject": subject,
            "membership": membership,
            "group_sessions": group_sessions,
        },
    )


def new_group_study_session_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    if not membership.moderator:
        raise PermissionDenied()

    preset_session = Session(
        needs_join_requests=False, host=request.user, subject=subject
    )

    form = SessionForm(
        request.POST or None, instance=preset_session, subject_id=subject_pk
    )

    if request.method == "POST" and form.is_valid():
        session = form.save()
        return redirect(
            "subjects:tutoring:session-list", subject_pk
        )  # TODO: change to redirect to newly created session

    return render(
        request, "tutoring/session_form.html", {"subject": subject, "form": form}
    )


def session_detail_view(request, subject_pk: int, session_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    session = get_object_or_404(Session, pk=session_pk)

    return render(
        request,
        "tutoring/session_detail.html",
        {"subject": subject, "session": session},
    )
