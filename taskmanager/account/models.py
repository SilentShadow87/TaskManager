from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


UserModel = get_user_model()

class ProfileModel(models.Model):
    user = models.OneToOneField(UserModel, related_name='profile', on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    is_premium_member = models.BooleanField(default=False)

