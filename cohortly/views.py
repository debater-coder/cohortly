from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import Http404
from django.http.response import FileResponse


@login_required
def media_proxy(request, name):
    if not default_storage.exists(name):
        raise Http404()
    return FileResponse(default_storage.open(name, "rb"))
