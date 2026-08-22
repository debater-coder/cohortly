from django.forms.models import ModelForm
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from cohortly.markdown_utils import safe_markdownify
from qa.models import Answer, Question
from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member


class AnswerForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Answer
        fields = ["body"]


@is_member
@require_POST
def answer_upvote(request, subject_pk: int, question_pk: int, answer_pk: int):
    get_object_or_404(Subject, pk=subject_pk)
    get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)
    answer = get_object_or_404(Answer, question_id=question_pk, pk=answer_pk)

    upvoted = answer.upvoted_by.filter(id=request.user.id).exists()
    if upvoted:
        answer.upvoted_by.remove(request.user)
    else:
        answer.upvoted_by.add(request.user)

    return render(
        request,
        "core/_upvote_button.html",
        {
            "upvote_count": answer.upvoted_by.count(),
            "upvoted": not upvoted,
            "upvote_target": reverse(
                "subjects:qa:upvote-answer", args=[subject_pk, question_pk, answer_pk]
            ),
        },
    )
