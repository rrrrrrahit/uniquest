from django.contrib import admin
from .models import Profile, Course, Grade, ScheduleEntry

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Grade)
admin.site.register(ScheduleEntry)
