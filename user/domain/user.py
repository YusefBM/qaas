from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid_utils.compat import uuid7


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
