from django.db import models
from users.models import User


# Create your models here.
class Tracker(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="Пользователи",
    )
    place = models.CharField(max_length=100)
    time = models.TimeField()
    action = models.CharField(max_length=100)
    pleasant_tracker = models.BooleanField(default=False)
    tracker_stacking = models.ForeignKey(to="self", null=True, blank=True, on_delete=models.SET_NULL)
    periodicity = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=100, null=True, blank=True)
    completion_time = models.PositiveIntegerField()
    publicness = models.BooleanField(default=False)
