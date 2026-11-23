from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    tg_chat_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telegram Chat ID")

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
    ]
