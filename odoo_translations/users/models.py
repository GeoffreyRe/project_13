from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(max_length=80, unique=True)
    username = models.CharField(max_length=80, null=False, blank=False)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username']