from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse
from django.shortcuts import redirect, render


@login_not_required
def index(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    return render(request, "core/index.html")
