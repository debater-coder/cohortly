from turtle import ondrag

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from markdownx.models import MarkdownxField
from modelsearch import index
from modelsearch.queryset import SearchableQuerySetMixin

from cohortly.markdown_utils import MARKDOWN_HELP_TEXT


class QuestionQuerySet(SearchableQuerySetMixin, models.QuerySet): ...


class Question(index.Indexed, models.Model):
    objects = QuestionQuerySet.as_manager()
    search_fields = [
        index.SearchField("title", boost=2.0),
        index.SearchField("body"),
    ]
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
        return self.answer_set.filter(marked_as_solution=True).exists()

    def __str__(self) -> str:
        return self.title


class AnswerQuerySet(SearchableQuerySetMixin, models.QuerySet): ...


class Answer(index.Indexed, models.Model):
    objects = AnswerQuerySet.as_manager()
    search_fields = [
        index.SearchField("body"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = MarkdownxField(max_length=30000, help_text=MARKDOWN_HELP_TEXT)
    marked_as_solution = models.BooleanField(default=False)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def get_absolute_url(self):
        return (
            reverse(
                "subjects:qa:question-detail",
                args=(self.question.subject.id, self.question.id),
            )
            + f"#answer-header-{self.id}"
        )
