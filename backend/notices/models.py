from django.contrib.auth.models import User
from django.db import models

from blog.models import Article


class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="acted_notifications"
    )
    verb = models.CharField(max_length=50)
    target_article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    target_comment = models.ForeignKey(
        "comments.Comment", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    unread = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.recipient} <- {self.actor}: {self.verb}"
