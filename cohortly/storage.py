from django.urls import reverse
from storages.backends.s3 import S3Storage


class ProxiedS3Storage(S3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        return reverse("media-proxy", args=[name])
