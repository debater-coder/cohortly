from django.contrib import admin

from qa.models import Answer, Question

admin.site.register([Question, Answer])
