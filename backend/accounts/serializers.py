from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["phone", "bio", "avatar"]

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        url = obj.avatar.url
        return request.build_absolute_uri(url) if request else url


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff", "profile"]

    def get_profile(self, obj):
        profile, _ = Profile.objects.get_or_create(user=obj)
        return ProfileSerializer(profile, context=self.context).data


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password1 = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("用户名已存在。")
        return value

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "两次输入的密码不一致。"})
        validate_password(attrs["password1"])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password1"],
        )
