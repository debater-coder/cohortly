from django.contrib import admin

from subjects.models import Subject, SubjectMembership

admin.site.register([Subject, SubjectMembership])
