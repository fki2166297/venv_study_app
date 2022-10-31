from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    icon = models.ImageField(verbose_name='アイコン', upload_to='account_icons/', null=True, blank=True, default='')

    class Meta:
        verbose_name_plural = 'CustomUser'
