from turtle import ondrag

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from markdownx.models import MarkdownxField

from cohortly.markdown_utils import MARKDOWN_HELP_TEXT


class Question(models.Model):
    """Record for questions asked by students, associated with a particular subject and set of topics."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150, validators=[MinLengthValidator(15)])
    body = MarkdownxField(max_length=30000, help_text=MARKDOWN_HELP_TEXT)
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="questions"
    )
    topics = models.ManyToManyField("subjects.Topic")
    asked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def get_absolute_url(self):
        return reverse(
            "subjects:qa:question-detail",
            args=(self.subject.id, self.id),
        )

    def is_solved(self):
        """Returns whether this question has any answer marked as the solution to the student's question."""
        return self.answer_set.filter(marked_as_solution=True).exists()

    def __str__(self) -> str:
        return self.title


class Answer(models.Model):
    """Record for answers to student questions, posted by other students in the subject."""

    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = MarkdownxField(max_length=30000, help_text=MARKDOWN_HELP_TEXT)
    marked_as_solution = models.BooleanField(default=False)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"Answer to {self.question}"

    def get_absolute_url(self):
        return (
            reverse(
                "subjects:qa:question-detail",
                args=(self.question.subject.id, self.question.id),
            )
            + f"#answer-header-{self.id}"
        )
