from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "verb", "actor", "article", "unread", "created"]

    def get_actor(self, obj):
        return obj.actor.username if obj.actor else None

    def get_article(self, obj):
        if not obj.target_article:
            return None
        return {"title": obj.target_article.title, "slug": obj.target_article.slug}
