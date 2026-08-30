"""
Module containing background tasks that run in a separate worker cluster.
"""

import hashlib
import io

import vt
from django.conf import settings
from django.core.mail import mail_admins, send_mass_mail
from django.template.loader import render_to_string

from cohortly.settings import env
from resources.models import Resource
from tutoring.models import Session, SessionParticipant

client = vt.Client(env("VIRUS_TOTAL_API_KEY"))


def scan_file(file):
    """
    Scans a given file for viruses using VirusTotal.
    """
    sha256_hash = hashlib.sha256()
    with file.open("rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    hash = sha256_hash.hexdigest()
    try:
        # Check the file's hash against VirusTotal's existing database
        file_obj = client.get_object(f"/files/{hash}")
        return (
            file_obj.last_analysis_stats["suspicious"] == 0
            and file_obj.last_analysis_stats["malicious"] == 0
        )
    except vt.APIError as e:
        if e.code == "NotFoundError":
            # Upload the file to VirusTotal to run a new scan
            with file.open("rb") as f:
                analysis = client.scan_file(
                    io.BytesIO(f.read()), wait_for_completion=True
                )
                return (
                    analysis.stats["suspicious"] == 0
                    and analysis.stats["malicious"] == 0
                )

        raise e


def scan_resource(resource_id):
    """Scans the file attached to a resource for viruses using VirusTotal"""
    resource = Resource.objects.get(id=resource_id)
    try:
        result = scan_file(resource.content)
        if not result:
            mail_admins(
                f"Resource uploaded by {resource.uploader.get_full_name()} flagged as a virus",
                f"Resource Title: {resource.title} ID: {resource.id} has been flagged as a virus.",
            )

        resource.scan_status = (
            Resource.ScanStatus.CLEAN if result else Resource.ScanStatus.INFECTED
        )
    except:
        resource.scan_status = Resource.ScanStatus.ERROR
        raise

    resource.save(update_fields=["scan_status"])


def send_session_reminder(session_id):
    """Sends a reminder email to all participants of a session"""
    session = Session.objects.get(id=session_id)

    participants = session.participants.filter(
        status=SessionParticipant.Status.ACCEPTED
    )
    send_mass_mail(
        (
            (
                f"Reminder: {session.title} starts in 10 minutes",
                render_to_string(
                    "emails/session_reminder.txt",
                    {
                        "participant": participant,
                        "session": session,
                        "site": settings.SITE_URL,
                    },
                ),
                None,
                [participant.student.email],
            )
            for participant in participants
            if participant.student.email
        )
    )
