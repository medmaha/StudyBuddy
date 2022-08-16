from django.db import models
from django.utils import timezone

from base.models import Message, Room, Groups, Topic



class Activity(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
    conversations = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)

    activity_message = models.CharField(max_length=100, blank=True)
    date_issued = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural = 'Activities'

    @property
    def message(self):
        return self.activity_message

    def __str_(self):
        return self.content_object

    
class RoomActivity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True)
    messages = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    groups = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
    activity_message = models.CharField(max_length=100, null=True, blank=True)
    date_issued = models.DateField(default=timezone.now)


    def __str__(self) :
        if self.messages:
            return self.messages.body[:20]
        if self.groups:
            return self.groups.name
