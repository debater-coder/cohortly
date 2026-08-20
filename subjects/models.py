from django.conf import settings
from django.db import models
from markdownx.models import MarkdownxField


class Subject(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="SubjectMembership"
    )

    def __str__(self) -> str:
        return self.name


class SubjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    moderator = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} is a {'moderator' if self.moderator else 'member'} of {self.subject}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subject"], name="unique_user_subject"
            )
        ]


class Topic(models.Model):
    name = models.CharField(max_length=200)
    description = MarkdownxField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    def __str__(self) -> str:
        return self.name
