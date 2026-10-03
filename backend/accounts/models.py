from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"
