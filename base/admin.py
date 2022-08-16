from django.contrib import admin

# Register your models here.

from .models import Topic, Room, Groups, Message
# admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Room)
admin.site.register(Groups)
admin.site.register(Message)
