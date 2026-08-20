from functools import wraps

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from subjects.models import SubjectMembership, Topic


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


def get_topic_lookup(qs: QuerySet[Topic]):
    return {topic["id"]: topic for topic in qs.values("id", "name", "parent_id")}


def get_topic_path(lookup, topic_id):
    crumbs = []
    seen = set()
    node = lookup.get(topic_id)  # leaf node
    while node and node["id"] not in seen:
        crumbs.append(node)
        seen.add(node["id"])
        node = lookup.get(node["parent_id"])

    return crumbs[::-1]
