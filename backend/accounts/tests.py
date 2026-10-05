import base64

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Profile

PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class ProfileSignalTests(TestCase):
    def test_profile_created_with_new_user(self):
        user = User.objects.create_user(username="alice", password="S3cure!Passw0rd")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_created_for_superuser(self):
        user = User.objects.create_superuser(
            username="root", email="root@example.com", password="S3cure!Passw0rd"
        )
        self.assertEqual(user.profile.user_id, user.id)

    def test_profile_is_not_duplicated(self):
        user = User.objects.create_user(username="bob", password="S3cure!Passw0rd")
        user.first_name = "Bob"
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_profile_and_returns_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password1": "S3cure!Passw0rd",
                "password2": "S3cure!Passw0rd",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data["user"]["username"], "newbie")
        self.assertIn("profile", data["user"])
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertTrue(Profile.objects.filter(user__username="newbie").exists())

        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["user"]["username"], "newbie")

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "mismatch",
                "password1": "S3cure!Passw0rd",
                "password2": "Different!Passw0rd",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_logout_me(self):
        User.objects.create_user(username="demo", password="demo12345")
        login = self.client.post(
            "/api/auth/login/", {"username": "demo", "password": "demo12345"}, format="json"
        )
        self.assertEqual(login.status_code, 200, login.content)
        self.assertEqual(login.json()["user"]["username"], "demo")
        self.assertEqual(login.json()["user"]["profile"]["phone"], "")

        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.json()["user"]["username"], "demo")

        logout = self.client.post("/api/auth/logout/")
        self.assertEqual(logout.status_code, 200)
        self.assertIsNone(self.client.get("/api/auth/me/").json()["user"])

    def test_login_invalid_credentials(self):
        User.objects.create_user(username="demo", password="demo12345")
        response = self.client.post(
            "/api/auth/login/", {"username": "demo", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_me_anonymous(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["user"])

    def test_csrf_endpoint_sets_cookie(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_profile_requires_auth(self):
        response = self.client.patch("/api/profile/", {"bio": "hi"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_profile_patch_and_avatar_upload(self):
        user = User.objects.create_user(username="demo", password="demo12345")
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            "/api/profile/", {"phone": "13800000000", "bio": "你好"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["phone"], "13800000000")

        avatar = SimpleUploadedFile("avatar.png", PNG_1PX, content_type="image/png")
        upload = self.client.post("/api/profile/avatar/", {"avatar": avatar}, format="multipart")
        self.assertEqual(upload.status_code, 200, upload.content)
        self.assertIn("avatar", upload.json())
        self.assertIsNotNone(upload.json()["avatar"])

    def test_password_reset_always_200(self):
        response = self.client.post(
            "/api/auth/password-reset/", {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
