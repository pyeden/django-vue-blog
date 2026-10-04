from rest_framework import serializers

from .models import Comment


class CommentUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile or not profile.avatar:
            return None
        request = self.context.get("request")
        url = profile.avatar.url
        return request.build_absolute_uri(url) if request else url


class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)
    parent_id = serializers.IntegerField(source="parent.id", read_only=True, allow_null=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "body", "user", "created", "parent_id", "replies"]

    def get_replies(self, obj):
        children = obj.replies.filter(active=True).select_related("user", "user__profile")
        return CommentSerializer(children, many=True, context=self.context).data


class CommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)
