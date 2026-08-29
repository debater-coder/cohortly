import magic
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import ValidationError


def validate_file_size(file):
    max_size_kb = 10240  # 10MB
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"File size exceeds {max_size_kb} KB")


def validate_pdf(file):
    """Checks MIME type of file to validate that the uploaded file is a true PDF"""
    file_buffer = file.read(2048)
    file.seek(0)
    mime = magic.from_buffer(file_buffer, mime=True)
    if mime != "application.pdf":
        raise ValidationError(
            "Unsupported file type, the file must be a valid PDF document."
        )


class Resource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="resources"
    )
    topics = models.ManyToManyField("subjects.Topic")
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resources"
    )
    upvoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL)
    description = models.TextField(blank=True)
    content = models.FileField(
        upload_to="resources/",
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=["pdf"],
                message="Unsupported file type, the file must be a valid PDF document.",
            ),
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.title}"
