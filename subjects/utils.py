from functools import wraps

from django.core.exceptions import PermissionDenied

from subjects.models import SubjectMembership


def is_moderator(view_func):
    @wraps(view_func)
    def wrap(request, subject_pk: int, *args, **kwargs):
        membership = SubjectMembership.objects.filter(
            user=request.user, subject_id=subject_pk
        ).first()

        if membership and membership.moderator:
            return view_func(request, *args, subject_pk=subject_pk, **kwargs)

        raise PermissionDenied()

    return wrap
