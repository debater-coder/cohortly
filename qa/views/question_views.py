from enum import member

from django import forms
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_tomselect.app_settings import Const, TomSelectConfig
from django_tomselect.forms import TomSelectModelMultipleChoiceField

from cohortly.markdown_utils import safe_markdownify
from qa.models import Answer, Question
from qa.views.answer_views import AnswerForm
from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member


class QuestionForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Question
        fields = ["title", "body", "topics"]

    def __init__(self, *args, subject_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id = subject_id

        self.fields["topics"] = TomSelectModelMultipleChoiceField(
            config=TomSelectConfig(
                url="subjects:autocomplete-topic",
                placeholder="Select one or more topics...",
                filter_by=[Const(subject_id, "subject_id")],
                label_field="path",
            ),
        )

    def clean_topics(self):
        topics = self.cleaned_data["topics"]

        for topic in topics:
            if topic.subject_id != self.subject_id:
                raise forms.ValidationError(
                    "That topic doesn't belong to the selected subject"
                )
        return topics


@is_member
def question_list_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    return render(
        request,
        "qa/question_list.html",
        {
            "subject": subject,
            "questions": Question.objects.filter(subject_id=subject_pk),
        },
    )


@is_member
def question_ask_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    preset_question = Question(asked_by=request.user, subject_id=subject_pk)
    form = QuestionForm(
        request.POST or None, instance=preset_question, subject_id=subject_pk
    )

    if request.method == "POST" and form.is_valid():
        question = form.save()
        return redirect("subjects:qa:question-detail", subject_pk, question.id)

    return render(
        request,
        "qa/question_form.html",
        {"subject": subject, "form": form, "new": True},
    )


def question_detail_view(request, subject_pk: int, question_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    answers = [
        {
            "content": safe_markdownify(answer.body),
            "marked_as_solution": answer.marked_as_solution,
            "posted_by": answer.posted_by.get_full_name(),
            "upvote_count": answer.upvote_count,
            "created_at": answer.created_at,
            "upvoted": answer.upvoted_by.filter(id=request.user.id).exists(),
            "id": answer.id,
        }
        for answer in question.answer_set.annotate(upvote_count=Count("upvoted_by"))
    ]

    # Answer Form
    preset_answer = Answer(
        question_id=question_pk,
        posted_by=request.user,
    )

    answer_form = AnswerForm(request.POST or None, instance=preset_answer)

    if request.method == "POST" and answer_form.is_valid():
        answer_form.save()
        return redirect(request.path)

    return render(
        request,
        "qa/question_detail.html",
        {
            "question": question,
            "subject": subject,
            "content": safe_markdownify(question.body),
            "membership": membership,
            "answers": answers,
            "answer_form": answer_form,
            "upvoted": question.upvoted_by.filter(pk=request.user.id).exists(),
            "upvote_count": question.upvoted_by.count(),
        },
    )


def question_edit_view(request, subject_pk: int, question_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    # Can only edit a question if you created it, or if you are a subject moderator
    is_moderator = membership and membership.moderator

    if not (is_moderator or question.asked_by == request.user):
        raise PermissionDenied()

    form = QuestionForm(request.POST or None, instance=question, subject_id=subject_pk)

    if request.method == "POST" and form.is_valid():
        question = form.save()
        return redirect("subjects:qa:question-detail", subject_pk, question.id)

    return render(
        request,
        "qa/question_form.html",
        {"subject": subject, "form": form, "new": False},
    )


@is_member
@require_POST
def question_upvote(request, subject_pk: int, question_pk: int):
    get_object_or_404(Subject, pk=subject_pk)
    question = get_object_or_404(Question, subject_id=subject_pk, pk=question_pk)

    upvoted = question.upvoted_by.filter(id=request.user.id).exists()
    if upvoted:
        question.upvoted_by.remove(request.user)
    else:
        question.upvoted_by.add(request.user)

    return render(
        request,
        "core/_upvote_button.html",
        {
            "upvote_count": question.upvoted_by.count(),
            "upvoted": not upvoted,
            "upvote_target": reverse(
                "subjects:qa:upvote-question",
                args=[
                    subject_pk,
                    question_pk,
                ],
            ),
        },
    )
