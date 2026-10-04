from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from blog.models import Article
from notices.models import Notification

from .models import Comment


class CommentApiTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="S3cure!Passw0rd")
        self.commenter = User.objects.create_user(username="demo", password="demo12345")
        self.other = User.objects.create_user(username="other", password="S3cure!Passw0rd")
        self.article = Article.objects.create(
            author=self.author, title="Hello", body="正文"
        )
        self.client = APIClient()

    def post_comment(self, body="不错", parent_id=None):
        payload = {"body": body}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        return self.client.post(
            f"/api/articles/{self.article.slug}/comments/", payload, format="json"
        )

    def test_comment_on_chinese_slug_article(self):
        article = Article.objects.create(author=self.author, title="中文标题", body="正文")
        self.assertNotEqual(article.slug, "")
        self.client.force_authenticate(user=self.commenter)
        path = f"/api/articles/{quote(article.slug)}/comments/"
        response = self.client.post(path, {"body": "中文路径评论"}, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        tree = self.client.get(path).json()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["body"], "中文路径评论")

    def test_anonymous_cannot_comment(self):
        response = self.post_comment()
        self.assertEqual(response.status_code, 401)

    def test_create_comment_and_notify_author(self):
        self.client.force_authenticate(user=self.commenter)
        response = self.post_comment("很有帮助")
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data["body"], "很有帮助")
        self.assertEqual(data["user"]["username"], "demo")
        self.assertIsNone(data["parent_id"])
        self.assertEqual(data["replies"], [])

        notification = Notification.objects.get(recipient=self.author)
        self.assertEqual(notification.actor, self.commenter)
        self.assertEqual(notification.verb, "commented")
        self.assertEqual(notification.target_article, self.article)
        self.assertEqual(notification.target_comment_id, data["id"])
        self.assertTrue(notification.unread)

    def test_self_comment_does_not_notify(self):
        self.client.force_authenticate(user=self.author)
        response = self.post_comment("作者自己留言")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 0)

    def test_two_level_comment_tree(self):
        self.client.force_authenticate(user=self.commenter)
        root = self.post_comment("根评论").json()
        self.client.force_authenticate(user=self.other)
        reply = self.post_comment("回复", parent_id=root["id"])
        self.assertEqual(reply.status_code, 201, reply.content)
        self.assertEqual(reply.json()["parent_id"], root["id"])

        tree = self.client.get(f"/api/articles/{self.article.slug}/comments/").json()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["id"], root["id"])
        self.assertEqual(len(tree[0]["replies"]), 1)
        self.assertEqual(tree[0]["replies"][0]["body"], "回复")

    def test_reply_to_reply_is_normalized_to_root(self):
        self.client.force_authenticate(user=self.commenter)
        root = self.post_comment("根").json()
        reply = self.post_comment("一级回复", parent_id=root["id"]).json()
        self.client.force_authenticate(user=self.other)
        deep = self.post_comment("回复的回复", parent_id=reply["id"])
        self.assertEqual(deep.status_code, 201)
        self.assertEqual(deep.json()["parent_id"], root["id"])

        tree = self.client.get(f"/api/articles/{self.article.slug}/comments/").json()
        self.assertEqual(len(tree[0]["replies"]), 2)
        self.assertTrue(all(not item["replies"] for item in tree[0]["replies"]))

    def test_parent_from_another_article_rejected(self):
        other_article = Article.objects.create(
            author=self.author, title="Other", body="x"
        )
        foreign = Comment.objects.create(
            article=other_article, user=self.other, body="foreign"
        )
        self.client.force_authenticate(user=self.commenter)
        response = self.post_comment("越界回复", parent_id=foreign.id)
        self.assertEqual(response.status_code, 400)

    def test_delete_permissions(self):
        comment = Comment.objects.create(
            article=self.article, user=self.commenter, body="待删除"
        )
        self.client.force_authenticate(user=self.other)
        forbidden = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_authenticate(user=self.commenter)
        deleted = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(deleted.status_code, 204)
        comment.refresh_from_db()
        self.assertFalse(comment.active)
        tree = self.client.get(f"/api/articles/{self.article.slug}/comments/").json()
        self.assertEqual(tree, [])

    def test_staff_can_delete_any_comment(self):
        staff = User.objects.create_user(
            username="staff", password="S3cure!Passw0rd", is_staff=True
        )
        comment = Comment.objects.create(
            article=self.article, user=self.commenter, body="违规"
        )
        self.client.force_authenticate(user=staff)
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, 204)
