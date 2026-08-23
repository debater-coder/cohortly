from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from markdownx.models import MarkdownxField
from modelsearch import index
from modelsearch.queryset import SearchableQuerySetMixin

from cohortly.markdown_utils import MARKDOWN_HELP_TEXT


class SubjectQuerySet(SearchableQuerySetMixin, models.QuerySet): ...


class Subject(index.Indexed, models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="SubjectMembership"
    )
    objects = SubjectQuerySet.as_manager()
    search_fields = [index.SearchField("name")]

    def get_absolute_url(self):
        return reverse(
            "subjects:subject-detail",
            args=(self.id,),
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


class TopicQuerySet(SearchableQuerySetMixin, models.QuerySet): ...


class Topic(index.Indexed, models.Model):
    objects = TopicQuerySet.as_manager()

    search_fields = [
        index.SearchField("name", boost=2.0),
        index.SearchField("description"),
        index.RelatedFields("subject", Subject.search_fields),
    ]
    name = models.CharField(max_length=200)
    description = MarkdownxField(
        blank=True,
        help_text=MARKDOWN_HELP_TEXT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        ordering = ["position"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse(
            "subjects:topic-detail",
            args=(self.subject.id, self.id),
        )

    def get_all_descendants(self):
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())

        return descendants
