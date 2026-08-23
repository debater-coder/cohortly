from django.shortcuts import get_object_or_404, render

from subjects.models import Subject


def session_list_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    return render(request, "tutoring/session_list.html", {"subject": subject})
