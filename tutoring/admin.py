from django.contrib import admin

from tutoring.models import Session, SessionParticipant

admin.site.register([Session, SessionParticipant])
