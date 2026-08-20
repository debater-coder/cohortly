from django.contrib import admin

from subjects.models import Subject, SubjectMembership, Topic

admin.site.register([Subject, SubjectMembership, Topic])
