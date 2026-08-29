from django import forms
from django.core.handlers.exception import PermissionDenied
from django.db.models import Count
from django.forms import ModelForm
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from django_q.tasks import async_task
from django_tomselect.app_settings import Const, PluginRemoveButton, TomSelectConfig
from django_tomselect.forms import TomSelectModelMultipleChoiceField

from resources.models import Resource
from subjects.models import Subject, SubjectMembership
from subjects.utils import is_member


def can_modify_resource(resource, user, membership):
    return (membership and membership.moderator) or (resource.uploader == user)


class ResourceForm(ModelForm):
    required_css_class = "field-required"

    class Meta:
        model = Resource
        fields = ["title", "topics", "description", "content"]
        labels = {"content": "Upload a file (optional)"}
        help_texts = {
            "description": "If you wish to provide a Google Docs link or similar, paste the link in here and leave the upload blank",
            "content": "Only PDF files are supported.",
        }

    def __init__(self, *args, subject_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id = subject_id
        self.fields["topics"] = TomSelectModelMultipleChoiceField(
            config=TomSelectConfig(
                url="subjects:autocomplete-topic",
                placeholder="Select one or more topics:",
                filter_by=[Const(subject_id, "subject_id")],
                label_field="path",
                plugin_remove_button=PluginRemoveButton(
                    title="Remove this item",
                    label="&times;",
                    class_name="remove",
                ),
            )
        )

    def clean_topics(self):
        topics = self.cleaned_data["topics"]

        for topic in topics:
            if topic.subject_id != self.subject_id:
                raise forms.ValidationError(
                    "That topic doesn't belong to the selected subject"
                )
        return topics


def resources_list_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    resources = (
        Resource.objects.filter(
            subject_id=subject_pk, scan_status=Resource.ScanStatus.CLEAN
        )
        .annotate(upvote_count=Count("upvoted_by"))
        .order_by(
            "-upvote_count",
        )
    )

    return render(
        request,
        "resources/resource_list.html",
        {
            "subject": subject,
            "resources": resources,
        },
    )


def scan_resource_if_needed(resource: Resource):
    """Scans a resource if it contains a file"""
    if resource.content:
        resource.scan_status = Resource.ScanStatus.PENDING
        # Scan file
        async_task("cohortly.tasks.scan_resource", resource.id)
    else:
        # No file to scan: set to clean
        resource.scan_status = Resource.ScanStatus.CLEAN
    resource.save(update_fields=["scan_status"])


def resources_upload_view(request, subject_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    if not membership:
        raise PermissionDenied()

    preset_resource = Resource(subject=subject, uploader=request.user)

    form = ResourceForm(
        request.POST or None,
        request.FILES or None,
        subject_id=subject_pk,
        instance=preset_resource,
    )

    if request.method == "POST" and form.is_valid():
        resource = form.save()
        scan_resource_if_needed(resource)
        return redirect("subjects:resources:resource-detail", subject_pk, resource.id)

    return render(
        request, "resources/resource_form.html", {"subject": subject, "form": form}
    )


def resource_detail_view(request, subject_pk: int, resource_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    resource = get_object_or_404(Resource, pk=resource_pk)
    #
    # Hide resources not from this user that are not confirmed to be clean of viruses
    if (
        resource.scan_status != Resource.ScanStatus.CLEAN
        and resource.uploader != request.user
    ):
        raise Http404()

    can_modify = can_modify_resource(resource, request.user, membership)

    return render(
        request,
        "resources/resource_detail.html",
        {
            "subject": subject,
            "resource": resource,
            "can_modify": can_modify,
            "upvoted": resource.upvoted_by.filter(pk=request.user.id).exists(),
            "upvote_count": resource.upvoted_by.count(),
            "ScanStatus": Resource.ScanStatus,
        },
    )


def resources_edit_view(request, subject_pk: int, resource_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    resource = get_object_or_404(Resource, pk=resource_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    if not can_modify_resource(resource, request.user, membership):
        raise PermissionDenied()

    form = ResourceForm(
        request.POST or None,
        request.FILES or None,
        subject_id=subject_pk,
        instance=resource,
    )

    if request.method == "POST" and form.is_valid():
        resource = form.save()
        scan_resource_if_needed(resource)
        return redirect("subjects:resources:resource-detail", subject_pk, resource.id)

    return render(
        request, "resources/resource_form.html", {"subject": subject, "form": form}
    )


@require_POST
def resource_delete(request, subject_pk: int, resource_pk: int):
    subject = get_object_or_404(Subject, pk=subject_pk)
    resource = get_object_or_404(Resource, subject_id=subject_pk, pk=resource_pk)

    membership = SubjectMembership.objects.filter(
        user=request.user, subject=subject
    ).first()

    can_modify = can_modify_resource(resource, request.user, membership)

    if not can_modify:
        raise PermissionDenied()

    resource.delete()

    if request.htmx:
        return HttpResponseClientRedirect(
            reverse("subjects:resources:resource-list", args=(subject_pk,))
        )

    return redirect("subjects:resources:resource-list", subject_pk)


@is_member
@require_POST
def resource_upvote(request, subject_pk: int, resource_pk: int):
    get_object_or_404(Subject, pk=subject_pk)
    resource = get_object_or_404(Resource, subject_id=subject_pk, pk=resource_pk)

    upvoted = resource.upvoted_by.filter(id=request.user.id).exists()
    if upvoted:
        resource.upvoted_by.remove(request.user)
    else:
        resource.upvoted_by.add(request.user)

    return render(
        request,
        "core/_upvote_button.html",
        {
            "upvote_count": resource.upvoted_by.count(),
            "upvoted": not upvoted,
            "upvote_target": reverse(
                "subjects:resources:upvote-resource",
                args=[
                    subject_pk,
                    resource_pk,
                ],
            ),
        },
    )
