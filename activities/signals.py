from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Activity, RoomActivity

from base.models import (
    Topic,
    Room,
    Groups,
    Message
)


@receiver(post_save, sender=Topic)
def new_topic_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            topic=instance,
            activity_message= 'Created a new topic'
        )

        
@receiver(post_save, sender=Room)
def new_room_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
           room=instance,
           activity_message='Start a new room'
        )


@receiver(post_save, sender=Groups,)
def new_group_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            group=instance,
            activity_message='Opens a new group'
        )

        RoomActivity.objects.create(
            room=instance.room, groups=instance,
            activity_message='Creates a new group'
        )


@receiver(post_save, sender=Message)
def new_topic_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            conversations = instance,
            activity_message = f'Replid to {instance.group.name}'
        )

        RoomActivity.objects.create(
            room=instance.group.room, messages=instance,
            activity_message='Reacted to'
        )

