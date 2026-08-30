from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


def validate_not_in_past(value):
    if value < timezone.now():
        raise ValidationError("The date cannot be in the past.")


class Session(models.Model):
    """A group study or peer tutoring session."""

    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=1000)
    # Maximum number of students who can join the session
    capacity = models.PositiveIntegerField(default=10)
    title = models.CharField(max_length=200)
    # Peer tutoring sessions need join requests, while group study sessions are created by moderators and do not need join requests
    needs_join_requests = models.BooleanField(default=False)
    # Whether the session is open to students to join
    open = models.BooleanField(default=True)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE)
    topics = models.ManyToManyField("subjects.Topic")
    upvoted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="session_upvote_set"
    )
    start_time = models.DateTimeField(validators=[validate_not_in_past])
    end_time = models.DateTimeField(validators=[validate_not_in_past])
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    end_time__gt=models.F("start_time"),
                ),
                name="check_end_time_after_start_time",
                violation_error_message="The end time must occur after the start time",
            )
        ]

    def get_absolute_url(self):
        return reverse(
            "subjects:tutoring:session-detail", args=(self.subject.id, self.id)
        )

    def joined_participants(self):
        """Returns a query set of students who have joined the session."""
        return self.participants.filter(status=SessionParticipant.Status.ACCEPTED)

    def pending_participants(self):
        """Returns a query set of students who have pending join requests for the session."""
        return self.participants.filter(status=SessionParticipant.Status.PENDING)

    def __str__(self):
        return self.title

    def clean(self):
        """Validates the session cannot have a capacity greater than 8 (for peer tutoring) and 250 (for group study)"""
        super().clean()
        max_capacity = 8 if self.needs_join_requests else 250

        if self.capacity > max_capacity:
            raise ValidationError(
                {"capacity": f"The capacity cannot be greater than {max_capacity}"}
            )


class SessionParticipant(models.Model):
    """Represents a student's join status in a session."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="participants"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices)

    class Meta:
        # A student cannot have multiple join statuses for a session
        unique_together = ("session", "student")
