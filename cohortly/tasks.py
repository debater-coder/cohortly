import hashlib

import vt
from django.core.mail import mail_admins

from cohortly.settings import env
from resources.models import Resource

client = vt.Client(env("VIRUS_TOTAL_API_KEY"))


def scan_file(file):
    sha256_hash = hashlib.sha256()
    with open(file.path, "rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    hash = sha256_hash.hexdigest()
    try:
        file_obj = client.get_object(f"/files/{hash}")
        return (
            file_obj.last_analysis_stats["suspicious"] == 0
            and file_obj.last_analysis_stats["malicious"] == 0
        )
    except vt.APIError as e:
        if e.code == "NotFoundError":
            with open(file.path, "rb") as f:
                analysis = client.scan_file(f, wait_for_completion=True)
                return (
                    analysis.stats["suspicious"] == 0
                    and analysis.stats["malicious"] == 0
                )

        raise e


def scan_resource(resource_id):
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
