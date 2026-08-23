from django.conf import settings
from django.db import models
from django.shortcuts import reverse


class Session(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=1000)
    capacity = models.PositiveIntegerField(default=10)
    title = models.CharField(max_length=200)
    needs_join_requests = models.BooleanField(default=False)
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse(
            "subjects:tutoring:session-detail", args=(self.subject.id, self.id)
        )

    def __str__(self):
        return self.title


class SessionParticipant(models.Model):
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
        unique_together = ("session", "student")
