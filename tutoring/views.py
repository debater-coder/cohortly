from django import forms
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from django_tomselect.app_settings import Const, PluginRemoveButton, TomSelectConfig
from django_tomselect.forms import (
    TomSelectModelMultipleChoiceField,
)

from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member
from tutoring.models import Session, SessionParticipant


def query_upcoming_tutoring_sessions():
    """Query for tutoring sessions that are open in the next week"""
    return Q(
        needs_join_requests=True,
        open=True,
        end_time__gt=timezone.now(),
        end_time__lt=timezone.now() + timezone.timedelta(days=7),
    )


def query_group_or_joined(user):
    """Returns a django query that matches sessions that are either group or the user has made a request to join"""
    return Q(needs_join_requests=False) | Q(
        participants__student=user,
        participants__status__in=[
            SessionParticipant.Status.ACCEPTED,
            SessionParticipant.Status.PENDING,
        ],
    )


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
            "open",
        ]
        help_texts = {
            "location": "A physical location or meeting link",
            "capacity": "The maximum number of students who can join this session",
            "topics": "The specific topics this session will focus on",
            "open": "Whether the session is open to new participants",
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
                plugin_remove_button=PluginRemoveButton(
                    title="Remove this item",
                    label="&times;",
                    class_name="remove",
                ),
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

    # Sessions in the next week
    upcoming_sessions = Session.objects.filter(
        Q(
            subject=subject,
            end_time__gt=timezone.now(),
            end_time__lt=timezone.now() + timezone.timedelta(days=7),
        )
        & query_group_or_joined(request.user)
    ).order_by("start_time")

    return render(
        request,
        "tutoring/session_list.html",
        {
            "subject": subject,
            "membership": membership,
            "upcoming_sessions": upcoming_sessions,
            "upcoming_tutoring_sessions": Session.objects.filter(
                query_upcoming_tutoring_sessions()
            ),
        },
    )


def new_group_study_session_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    if not (membership and membership.moderator):
        raise PermissionDenied()

    preset_session = Session(
        needs_join_requests=False, host=request.user, subject=subject
    )

    form = SessionForm(
        request.POST or None, instance=preset_session, subject_id=subject_pk
    )

    if request.method == "POST" and form.is_valid():
        session = form.save()

        # Add the host to the participants list
        participation = SessionParticipant(
            student=request.user,
            session=session,
            status=(SessionParticipant.Status.ACCEPTED),
        )
        participation.save()
        return redirect("subjects:tutoring:session-detail", subject_pk, session.id)

    return render(
        request, "tutoring/session_form.html", {"subject": subject, "form": form}
    )


@is_member
def new_tutoring_session_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    preset_session = Session(
        needs_join_requests=True, host=request.user, subject=subject, capacity=2
    )

    form = SessionForm(
        request.POST or None,
        instance=preset_session,
        subject_id=subject_pk,
    )

    if request.method == "POST" and form.is_valid():
        session = form.save()

        # Add the host to the participants list
        participation = SessionParticipant(
            student=request.user,
            session=session,
            status=(SessionParticipant.Status.ACCEPTED),
        )
        participation.save()
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
    participation = SessionParticipant.objects.filter(
        student=request.user, session=session
    ).first()

    pending_participants = SessionParticipant.objects.filter(
        session=session, status=SessionParticipant.Status.PENDING
    )

    return render(
        request,
        "tutoring/session_detail.html",
        {
            "subject": subject,
            "session": session,
            "can_modify": can_modify,
            "participation": participation,
            "pending_participants": pending_participants,
            "Status": SessionParticipant.Status,
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
        participation = None
    elif session.open:
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
        if (
            session.capacity
            == session.participants.filter(
                status=SessionParticipant.Status.ACCEPTED
            ).count()
        ):
            session.open = False
            session.save()
    else:
        raise PermissionDenied()

    return render(
        request,
        "tutoring/session_detail.html#join_session_button",
        {
            "subject": subject,
            "session": session,
            "participation": participation,
            "Status": SessionParticipant.Status,
        },
    )


def get_session_events(qs):
    """
    Gets session events into a format readable by fullcalendar,
    qs: the queryset to obtain sessions from
    start: start datetime of filter
    end: end datetime of filter
    """

    return [
        {
            "id": session.id,
            "title": session.title,
            "start": session.start_time,
            "end": session.end_time,
            "url": session.get_absolute_url(),
        }
        for session in qs
    ]


def session_events(request, subject_pk: int):
    """Session feed for a particular subject to be displayed in the calendar"""
    start = parse_datetime(request.GET["start"])

    end = parse_datetime(request.GET["end"])

    subject = get_object_or_404(Subject, pk=subject_pk)
    sessions = Session.objects.filter(
        Q(subject=subject, start_time__gt=start, end_time__lt=end)
        & query_group_or_joined(request.user)
    ).order_by("start_time")

    start = parse_datetime(request.GET["start"])
    end = parse_datetime(request.GET["end"])

    return JsonResponse(
        get_session_events(sessions),
        safe=False,
    )


def all_session_events(request):
    """Session feed for all subjects for the shared calendar"""
    start = parse_datetime(request.GET["start"])
    end = parse_datetime(request.GET["end"])

    return JsonResponse(
        get_session_events(
            Session.objects.filter(
                Q(
                    start_time__gt=start,
                    end_time__lt=end,
                )
                & query_group_or_joined(request.user)
            ),
        ),
        safe=False,
    )


def get_participation_for_modify(
    user, subject_pk: int, session_pk: int, participation_pk: int
):
    """Helper to get participation and validate the user can modify it"""

    subject = get_object_or_404(Subject, pk=subject_pk)
    session = get_object_or_404(Session, subject_id=subject_pk, pk=session_pk)

    membership = SubjectMembership.objects.filter(user=user, subject=subject).first()

    can_modify = can_modify_session(session, user, membership)
    if not can_modify:
        raise PermissionDenied()

    participation = get_object_or_404(
        SessionParticipant, session_id=session_pk, pk=participation_pk
    )

    return session, participation


@require_POST
def accept_join_request(
    request, subject_pk: int, session_pk: int, participation_pk: int
):
    session, participation = get_participation_for_modify(
        request.user, subject_pk, session_pk, participation_pk
    )

    participation.status = SessionParticipant.Status.ACCEPTED
    participation.save()

    if (
        SessionParticipant.objects.filter(
            session=session, status=SessionParticipant.Status.ACCEPTED
        ).count()
        >= session.capacity
    ):
        session.open = False
        session.save()

    if request.htmx:
        return HttpResponseClientRefresh()

    return redirect("subjects:tutoring:session-detail", subject_pk, session_pk)


@require_POST
def reject_join_request(
    request, subject_pk: int, session_pk: int, participation_pk: int
):
    participation = get_participation_for_modify(
        request.user, subject_pk, session_pk, participation_pk
    )
    participation.delete()

    if request.htmx:
        return HttpResponseClientRefresh()

    return redirect("subjects:tutoring:session-detail", subject_pk, session_pk)
