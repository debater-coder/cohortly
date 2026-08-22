from turtle import ondrag

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from markdownx.models import MarkdownxField


class Question(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150, validators=[MinLengthValidator(15)])
    body = MarkdownxField(max_length=30000)
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="questions"
    )
    topic = models.ManyToManyField("subjects.Topic")
    asked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Answer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = MarkdownxField(max_length=30000)
    marked_as_solution = models.BooleanField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)
