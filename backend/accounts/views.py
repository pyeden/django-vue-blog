import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            {"user": UserSerializer(user, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "用户名或密码错误。"}, status=status.HTTP_400_BAD_REQUEST
            )
        login(request, user)
        return Response({"user": UserSerializer(user, context={"request": request}).data})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"detail": "已退出登录。"})


class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"user": None})
        return Response({"user": UserSerializer(request.user, context={"request": request}).data})


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        users = User.objects.filter(email__iexact=email, is_active=True) if email else []
        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                subject="密码重置",
                message=(
                    f"你好 {user.username}：\n\n"
                    f"你的密码重置标识为：{uid}-{token}\n"
                    "如非本人操作请忽略此邮件。"
                ),
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
        # Always return 200 so the endpoint cannot be used to enumerate accounts.
        return Response({"detail": "若该邮箱已注册，重置邮件已发送。"})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid") or ""
        token = request.data.get("token") or ""
        password = request.data.get("password") or ""
        try:
            user = User.objects.get(pk=urlsafe_base64_decode(uid).decode())
        except (User.DoesNotExist, ValueError, TypeError, UnicodeDecodeError):
            return Response({"detail": "重置链接无效。"}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "重置链接已失效。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password, user)
        except Exception as exc:
            return Response({"password": list(exc)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"detail": "密码已重置，请重新登录。"})


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password") or ""
        if not request.user.check_password(password):
            return Response({"password": ["密码不正确。"]}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        logout(request)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile, context={"request": request}).data)

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        avatar = request.FILES.get("avatar")
        if avatar is None:
            return Response(
                {"detail": "缺少 avatar 文件。"}, status=status.HTTP_400_BAD_REQUEST
            )
        profile.avatar = avatar
        profile.save(update_fields=["avatar"])
        return Response(ProfileSerializer(profile, context={"request": request}).data)
