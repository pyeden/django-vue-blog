from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from blog.models import Article

from .models import Notification


class NotificationApiTests(TestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(
            username="author", password="S3cure!Passw0rd"
        )
        self.actor = User.objects.create_user(username="demo", password="demo12345")
        self.article = Article.objects.create(
            author=self.recipient, title="Hello", body="正文"
        )
        self.client = APIClient()

    def make_notification(self, unread=True):
        return Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            verb="commented",
            target_article=self.article,
            unread=unread,
        )

    def test_requires_login(self):
        response = self.client.get("/api/notifications/")
        self.assertIn(response.status_code, (401, 403))

    def test_list_shape_and_unread_count(self):
        self.make_notification()
        self.make_notification(unread=False)
        self.client.force_authenticate(user=self.recipient)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["unread_count"], 1)
        self.assertEqual(len(data["results"]), 2)
        item = data["results"][0]
        self.assertEqual(
            set(item.keys()), {"id", "verb", "actor", "article", "unread", "created"}
        )
        self.assertEqual(item["actor"], "demo")
        self.assertEqual(item["article"], {"title": "Hello", "slug": self.article.slug})

    def test_list_only_returns_own_notifications(self):
        other = User.objects.create_user(username="other", password="S3cure!Passw0rd")
        Notification.objects.create(recipient=other, verb="commented")
        self.client.force_authenticate(user=self.recipient)
        self.assertEqual(self.client.get("/api/notifications/").json()["unread_count"], 0)

    def test_mark_one_read(self):
        notification = self.make_notification()
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post(f"/api/notifications/{notification.id}/read/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["unread"])
        notification.refresh_from_db()
        self.assertFalse(notification.unread)

    def test_cannot_mark_other_users_notification(self):
        notification = self.make_notification()
        stranger = User.objects.create_user(username="stranger", password="S3cure!Passw0rd")
        self.client.force_authenticate(user=stranger)
        response = self.client.post(f"/api/notifications/{notification.id}/read/")
        self.assertEqual(response.status_code, 404)

    def test_read_all(self):
        self.make_notification()
        self.make_notification()
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post("/api/notifications/read-all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["unread_count"], 0)
        self.assertEqual(
            Notification.objects.filter(recipient=self.recipient, unread=True).count(), 0
        )
