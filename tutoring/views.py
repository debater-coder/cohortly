from django import forms
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from django_tomselect.app_settings import Const, TomSelectConfig
from django_tomselect.forms import (
    TomSelectModelMultipleChoiceField,
)

from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member
from tutoring.models import Session, SessionParticipant


class SessionForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Session
        fields = [
            "title",
            "description",
            "location",
            "capacity",
            "topics",
            "start_time",
            "end_time",
        ]
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
        return redirect("subjects:tutoring:session-detail", subject_pk, session.id)

    return render(
        request, "tutoring/session_form.html", {"subject": subject, "form": form}
    )


def can_modify_session(session, user, membership):
    return (membership and membership.moderator) or (
        session.needs_join_requests and session.host == user
    )


def session_detail_view(request, subject_pk: int, session_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()
    session = get_object_or_404(Session, pk=session_pk)

    can_modify = can_modify_session(session, request.user, membership)
    joined = SessionParticipant.objects.filter(
        student=request.user, session=session
    ).exists()

    return render(
        request,
        "tutoring/session_detail.html",
        {
            "subject": subject,
            "session": session,
            "can_modify": can_modify,
            "joined": joined,
        },
    )


def session_edit_view(request, subject_pk: int, session_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()
    session = get_object_or_404(Session, pk=session_pk)

    can_modify = can_modify_session(session, request.user, membership)

    if not can_modify:
        raise PermissionDenied()

    form = SessionForm(request.POST or None, instance=session, subject_id=subject_pk)

    if request.method == "POST" and form.is_valid():
        session = form.save()
        return redirect("subjects:tutoring:session-detail", subject_pk, session_pk)

    return render(
        request, "tutoring/session_form.html", {"subject": subject, "form": form}
    )


@require_POST
@is_member
def session_delete(request, subject_pk: int, session_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    session = get_object_or_404(Session, subject_id=subject_pk, pk=session_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    can_modify = can_modify_session(session, request.user, membership)

    if not can_modify:
        raise PermissionDenied()

    session.delete()

    if request.htmx:
        return HttpResponseClientRedirect(
            reverse("subjects:tutoring:session-list", args=(subject_pk,))
        )

    return redirect("subjects:tutoring:session-list", subject_pk)


@require_POST
@is_member
def session_join(request, subject_pk: int, session_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    session = get_object_or_404(Session, subject_id=subject_pk, pk=session_pk)

    participation = SessionParticipant.objects.filter(
        student=request.user, session=session
    ).first()

    if participation:
        participation.delete()
        joined = False
    else:
        participation = SessionParticipant(
            student=request.user,
            session=session,
            status=(
                SessionParticipant.Status.PENDING
                if session.needs_join_requests
                else SessionParticipant.Status.ACCEPTED
            ),
        )
        participation.save()
        joined = True

    return render(
        request,
        "tutoring/session_detail.html#join_session_button",
        {"joined": joined, "subject": subject, "session": session},
    )
