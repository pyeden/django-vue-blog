import base64

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Article, ArticleColumn, ArticleLike

PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class ArticleApiTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="S3cure!Passw0rd")
        self.other = User.objects.create_user(username="other", password="S3cure!Passw0rd")
        self.staff = User.objects.create_user(
            username="staff", password="S3cure!Passw0rd", is_staff=True
        )
        self.client = APIClient()
        self.column = ArticleColumn.objects.create(title="技术", slug="tech")

    def make_article(self, title="Hello World", author=None, **kwargs):
        article = Article.objects.create(
            author=author or self.author,
            title=title,
            body=kwargs.pop("body", "内容 **加粗**"),
            **kwargs,
        )
        return article

    def test_slug_auto_generated_and_unique(self):
        first = self.make_article("Hello World")
        second = self.make_article("Hello World")
        self.assertEqual(first.slug, "hello-world")
        self.assertEqual(second.slug, "hello-world-2")

    def test_slug_supports_chinese_titles(self):
        article = self.make_article("你好 Django")
        self.assertTrue(article.slug)
        self.assertIn("django", article.slug)

    def test_list_default_page_size_is_six(self):
        for index in range(8):
            self.make_article(f"Post {index}")
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 8)
        self.assertEqual(len(data["results"]), 6)

    def test_list_page_size_override_and_page(self):
        for index in range(7):
            self.make_article(f"Post {index}")
        response = self.client.get("/api/articles/?page_size=3&page=2")
        data = response.json()
        self.assertEqual(len(data["results"]), 3)
        self.assertIsNotNone(data["previous"])

    def test_search_filter(self):
        self.make_article("Django 入门")
        self.make_article("Vue 实战")
        response = self.client.get("/api/articles/?search=Django")
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Django 入门")

    def test_column_and_tag_filter(self):
        tagged = self.make_article("Tagged", column=self.column)
        tagged.tags.add("python", "django")
        self.make_article("No tag")
        by_column = self.client.get("/api/articles/?column=tech").json()
        self.assertEqual(by_column["count"], 1)
        by_tag = self.client.get("/api/articles/?tag=django").json()
        self.assertEqual(by_tag["count"], 1)
        self.assertEqual(by_tag["results"][0]["slug"], tagged.slug)

    def test_ordering_by_views(self):
        low = self.make_article("Low")
        high = self.make_article("High")
        Article.objects.filter(pk=high.pk).update(total_views=50)
        Article.objects.filter(pk=low.pk).update(total_views=1)
        data = self.client.get("/api/articles/?ordering=-total_views").json()
        self.assertEqual(data["results"][0]["title"], "High")

    def test_list_item_shape(self):
        article = self.make_article("Shape", column=self.column)
        article.tags.add("python")
        item = self.client.get("/api/articles/").json()["results"][0]
        for field in [
            "id", "title", "slug", "excerpt", "cover", "author", "column",
            "tags", "total_views", "likes", "comment_count", "created", "updated",
        ]:
            self.assertIn(field, item)
        self.assertEqual(item["author"]["username"], "author")
        self.assertEqual(item["column"], {"title": "技术", "slug": "tech"})
        self.assertEqual(item["tags"], ["python"])
        self.assertEqual(item["comment_count"], 0)

    def test_anonymous_cannot_create(self):
        response = self.client.post(
            "/api/articles/", {"title": "Nope", "body": "x"}, format="json"
        )
        self.assertIn(response.status_code, (401, 403))

    def test_author_can_create_with_tags_and_column(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.post(
            "/api/articles/",
            {
                "title": "新文章",
                "body": "# 标题\n\n正文",
                "column": "tech",
                "tags": ["django", "test"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertTrue(data["slug"])
        self.assertEqual(data["author"]["username"], "author")
        self.assertEqual(data["column"]["slug"], "tech")
        self.assertEqual(sorted(data["tags"]), ["django", "test"])
        self.assertEqual(len(data["toc"]), 1)

    def test_cover_upload_on_create(self):
        self.client.force_authenticate(user=self.author)
        cover = SimpleUploadedFile("cover.png", PNG_1PX, content_type="image/png")
        response = self.client.post(
            "/api/articles/",
            {"title": "带封面", "body": "正文", "cover": cover},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertIn("/media/covers/", response.json()["cover"])
        self.assertTrue(Article.objects.get(title="带封面").cover)

    def test_non_author_cannot_update_or_delete(self):
        article = self.make_article()
        self.client.force_authenticate(user=self.other)
        patch = self.client.patch(
            f"/api/articles/{article.slug}/", {"title": "Hacked"}, format="json"
        )
        self.assertEqual(patch.status_code, 403)
        delete = self.client.delete(f"/api/articles/{article.slug}/")
        self.assertEqual(delete.status_code, 403)

    def test_author_and_staff_can_update(self):
        article = self.make_article()
        self.client.force_authenticate(user=self.author)
        patch = self.client.patch(
            f"/api/articles/{article.slug}/", {"title": "Updated"}, format="json"
        )
        self.assertEqual(patch.status_code, 200, patch.content)

        other_article = self.make_article("Staff target")
        self.client.force_authenticate(user=self.staff)
        staff_patch = self.client.patch(
            f"/api/articles/{other_article.slug}/", {"title": "Managed"}, format="json"
        )
        self.assertEqual(staff_patch.status_code, 200, staff_patch.content)

    def test_author_can_delete(self):
        article = self.make_article()
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(f"/api/articles/{article.slug}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())

    def test_like_toggle_is_idempotent(self):
        article = self.make_article()
        self.client.force_authenticate(user=self.other)
        first = self.client.post(f"/api/articles/{article.slug}/like/")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(first.json(), {"liked": True, "likes": 1})
        self.assertEqual(ArticleLike.objects.filter(article=article).count(), 1)

        second = self.client.post(f"/api/articles/{article.slug}/like/")
        self.assertEqual(second.json(), {"liked": False, "likes": 0})
        self.assertEqual(ArticleLike.objects.filter(article=article).count(), 0)

        third = self.client.post(f"/api/articles/{article.slug}/like/")
        self.assertEqual(third.json(), {"liked": True, "likes": 1})

    def test_like_requires_login(self):
        article = self.make_article()
        response = self.client.post(f"/api/articles/{article.slug}/like/")
        self.assertIn(response.status_code, (401, 403))

    def test_like_unique_constraint(self):
        article = self.make_article()
        ArticleLike.objects.create(article=article, user=self.other)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ArticleLike.objects.create(article=article, user=self.other)

    def test_detail_renders_markdown_toc_and_increments_views(self):
        body = "# 大标题\n\n## 小节\n\n```python\nprint('hi')\n```\n\n|a|b|\n|-|-|\n|1|2|"
        article = self.make_article("Render", body=body)
        response = self.client.get(f"/api/articles/{article.slug}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("codehilite", data["body_html"])
        self.assertIn("print", data["body_html"])
        self.assertEqual(len(data["toc"]), 2)
        self.assertEqual(data["toc"][0]["text"], "大标题")
        self.assertTrue(data["toc"][0]["anchor"])
        self.assertEqual(data["total_views"], 1)
        self.assertEqual(data["liked"], False)

        again = self.client.get(f"/api/articles/{article.slug}/")
        self.assertEqual(again.json()["total_views"], 2)

    def test_detail_liked_flag(self):
        article = self.make_article()
        self.client.force_authenticate(user=self.other)
        self.client.post(f"/api/articles/{article.slug}/like/")
        data = self.client.get(f"/api/articles/{article.slug}/").json()
        self.assertTrue(data["liked"])

    def test_markdown_xss_is_sanitized(self):
        article = self.make_article(
            "XSS", body='<script>alert("x")</script>\n\n正常内容 <b onclick="evil()">加粗</b>'
        )
        response = self.client.get(f"/api/articles/{article.slug}/")
        html = response.json()["body_html"]
        self.assertNotIn("<script", html)
        self.assertNotIn("onclick", html)

    def test_hot_returns_top_five_by_views(self):
        for index in range(6):
            article = self.make_article(f"Hot {index}")
            Article.objects.filter(pk=article.pk).update(total_views=index * 10)
        response = self.client.get("/api/articles/hot/")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]["title"], "Hot 5")
        views = [item["total_views"] for item in results]
        self.assertEqual(views, sorted(views, reverse=True))

    def test_columns_and_tags_endpoints(self):
        article = self.make_article("Endpoint", column=self.column)
        article.tags.add("python")
        columns = self.client.get("/api/columns/")
        self.assertEqual(columns.status_code, 200)
        self.assertEqual(columns.json()[0]["slug"], "tech")
        self.assertEqual(columns.json()[0]["article_count"], 1)
        tags = self.client.get("/api/tags/")
        self.assertEqual(tags.status_code, 200)
        self.assertEqual(tags.json()[0]["name"], "python")

    def test_tag_filter_accepts_slug_case_insensitive(self):
        tagged = self.make_article("Cased Tag")
        tagged.tags.add("Django")
        by_slug = self.client.get("/api/articles/?tag=django").json()
        self.assertEqual(by_slug["count"], 1)
        self.assertEqual(by_slug["results"][0]["slug"], tagged.slug)
        by_name = self.client.get("/api/articles/?tag=Django").json()
        self.assertEqual(by_name["count"], 1)

    def test_missing_article_returns_404(self):
        self.assertEqual(self.client.get("/api/articles/nope/").status_code, 404)
