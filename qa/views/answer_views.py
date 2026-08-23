from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.forms.models import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRefresh

from cohortly.markdown_utils import safe_markdownify
from qa.models import Answer, Question
from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member


class AnswerForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Answer
        fields = ["body"]


def process_answer(answer: Answer, user, upvote_count):
    return {
        "content": safe_markdownify(answer.body),
        "marked_as_solution": answer.marked_as_solution,
        "posted_by_name": answer.posted_by.get_full_name(),
        "posted_by_id": answer.posted_by.id,
        "upvote_count": upvote_count,
        "created_at": answer.created_at,
        "upvoted": answer.upvoted_by.filter(id=user.id).exists(),
        "id": answer.id,
    }


def process_answers(answers, user):
    return [
        process_answer(answer, user, answer.upvote_count)
        for answer in answers.annotate(upvote_count=Count("upvoted_by")).order_by(
            "-marked_as_solution", "-upvote_count", "-created_at"
        )
    ]


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


@is_member
@require_POST
def mark_as_solution(request, subject_pk: int, question_pk: int, answer_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)
    answer = get_object_or_404(Answer, question_id=question_pk, pk=answer_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()
    is_moderator = membership and membership.moderator

    if not (is_moderator or question.asked_by == request.user):
        raise PermissionDenied()

    answer.marked_as_solution = not answer.marked_as_solution
    answer.save()

    return render(
        request,
        "qa/question_detail.html#answer_header",
        {
            "subject": subject,
            "question": question,
            "answer": process_answer(answer, request.user, answer.upvoted_by.count()),
        },
    )


@require_POST
@is_member
def answer_delete(request, subject_pk: int, question_pk: int, answer_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)
    answer = get_object_or_404(Answer, question_id=question_pk, pk=answer_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()
    is_moderator = membership and membership.moderator

    if not (is_moderator or answer.posted_by == request.user):
        raise PermissionDenied()

    answer.delete()

    if request.htmx:
        return HttpResponseClientRefresh()

    return redirect("subjects:qa:question-detail", subject_pk, question_pk)


@is_member
def answer_edit_view(request, subject_pk: int, question_pk: int, answer_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)
    answer = get_object_or_404(Answer, question_id=question_pk, pk=answer_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()
    is_moderator = membership and membership.moderator

    if not (is_moderator or answer.posted_by == request.user):
        raise PermissionDenied()

    answer_form = AnswerForm(request.POST or None, instance=answer)

    if request.method == "POST" and answer_form.is_valid():
        answer_form.save()
        return redirect("subjects:qa:question-detail", subject_pk, question_pk)

    return render(
        request,
        "qa/answer_edit.html",
        {"answer_form": answer_form, "subject": subject, "question": question},
    )
