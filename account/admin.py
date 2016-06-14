from django.contrib import admin
from account.models import Profile, PointHistory, Log

# Register your models here.
admin.site.register(Profile)
admin.site.register(PointHistory)
admin.site.register(Log)