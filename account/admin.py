from django.contrib import admin
from account.models import Profile, PointHistory, Log, Message, MessagePoll

# Register your models here.
admin.site.register(Profile)
admin.site.register(PointHistory)
admin.site.register(Log)
admin.site.register(Message)
admin.site.register(MessagePoll)