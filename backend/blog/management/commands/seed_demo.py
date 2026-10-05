"""Seed a demo blog: admin, demo user, columns, 8 articles and comments.

Admin password comes from DJANGO_ADMIN_PASSWORD. When unset a random one is
generated, printed once, and saved to logs/seed_admin_password.txt (0600).
"""
import os
import secrets
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from blog.models import Article, ArticleColumn
from comments.models import Comment
from notices.models import Notification

ARTICLES = [
    {
        "title": "Django 4.2 项目初始化实战",
        "column": "技术笔记",
        "tags": ["Django", "Python"],
        "body": """# Django 4.2 项目初始化实战

本文记录在 macOS 上从零搭建 Django 4.2 LTS 后端的过程。

## 创建虚拟环境

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install "Django==4.2.16" djangorestframework
```

## 创建项目

```bash
django-admin startproject config .
python manage.py startapp blog
```

## 要点

- 项目包名使用 `config`，应用按领域拆分。
- 数据库默认 SQLite，可用 `DJANGO_DB_PATH` 覆盖。
- 环境变量驱动配置，避免把密钥写进仓库。
""",
    },
    {
        "title": "DRF 序列化器与视图集实践",
        "column": "技术笔记",
        "tags": ["DRF", "API"],
        "body": """# DRF 序列化器与视图集实践

## ModelSerializer

```python
class ArticleSerializer(serializers.ModelSerializer):
    tags = TagsField(required=False)

    class Meta:
        model = Article
        fields = ["id", "title", "slug", "body", "tags", "created"]
```

## ViewSet 路由

```python
router = SimpleRouter()
router.register("articles", ArticleViewSet, basename="article")
```

## 分页

`PageNumberPagination` 默认每页 6 条，支持 `?page_size=` 覆盖。

## 小结

- 读接口与写接口共用序列化器时，注意把作者等字段设为只读。
- 权限用 `IsAuthenticatedOrReadOnly` 加对象级校验。
""",
    },
    {
        "title": "Markdown 服务端渲染与 XSS 清洗",
        "column": "技术笔记",
        "tags": ["Markdown", "安全"],
        "body": """# Markdown 服务端渲染与 XSS 清洗

## 渲染管线

1. `markdown` 扩展：`fenced_code`、`codehilite`、`toc`、`tables`。
2. `bleach.clean` 白名单清洗。
3. 保留 `codehilite` class 与标题 `id`，保证目录可用。

```python
html = markdown.markdown(text, extensions=["fenced_code", "codehilite", "toc"])
safe = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
```

## 目录结构

`toc_tokens` 递归展开为 `{level, text, anchor}` 列表返回前端。

## 安全提示

- 绝不直接 `|safe` 输出用户输入。
- 协议白名单只留 http/https/mailto。
""",
    },
    {
        "title": "Vue 3 + Vite 前端工程搭建",
        "column": "项目实战",
        "tags": ["Vue", "Vite"],
        "body": """# Vue 3 + Vite 前端工程搭建

## 初始化

```bash
npm create vite@latest frontend -- --template vue
cd frontend && npm install
npm install pinia vue-router bootstrap
```

## 目录约定

- `src/api/` 封装 axios 请求。
- `src/stores/` Pinia 状态。
- `src/views/` 页面组件。

## 代理配置

```js
server: {
  proxy: {
    '/api': 'http://127.0.0.1:8000',
  },
}
```

## 注意

开发环境必须带上 `credentials: 'include'`，否则会话 Cookie 不会生效。
""",
    },
    {
        "title": "Session + CSRF 登录设计",
        "column": "技术笔记",
        "tags": ["认证", "安全"],
        "body": """# Session + CSRF 登录设计

## 为什么不用 JWT

个人博客前后端同域部署，Session 更简单，也天然支持后台管理。

## 流程

1. `GET /api/auth/csrf/` 获取 csrftoken。
2. 前端从 Cookie 读取 token，写入 `X-CSRFToken` 请求头。
3. `POST /api/auth/login/` 建立会话。
4. `GET /api/auth/me/` 恢复登录态。

```python
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    def get(self, request):
        return Response({"csrfToken": get_token(request)})
```

## 权限约定

- 未登录写操作返回 401/403。
- 非作者修改、删除返回 403。
""",
    },
    {
        "title": "用 SQLite 也能撑起个人博客",
        "column": "生活随笔",
        "tags": ["SQLite", "运维"],
        "body": """# 用 SQLite 也能撑起个人博客

## 适合的场景

- 单机部署、读多写少。
- 数据量在百万行以内。
- 备份就是拷贝一个文件。

## 开启 WAL

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
```

## 备份脚本

```bash
sqlite3 db.sqlite3 ".backup 'backup-$(date +%F).sqlite3'"
```

## 结论

别过早引入复杂度，先把内容写起来。
""",
    },
    {
        "title": "从零部署 gunicorn + nginx",
        "column": "项目实战",
        "tags": ["部署", "nginx"],
        "body": """# 从零部署 gunicorn + nginx

## 启动 gunicorn

```bash
gunicorn config.wsgi:application \
  --bind 127.0.0.1:8001 \
  --workers 3 \
  --timeout 60
```

## nginx 子路径

```nginx
location /djangovueblog/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 静态资源

- `collectstatic` 产物交给 nginx 直接返回。
- 前端 history 路由需要 `try_files ... /index.html`。

## 检查清单

- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` 与 `CSRF_TRUSTED_ORIGINS` 配置正确
- [ ] 日志轮转生效
""",
    },
    {
        "title": "写作这件小事",
        "column": "生活随笔",
        "tags": ["随笔", "生活"],
        "body": """# 写作这件小事

## 为什么写

写作是把模糊的想法变清晰的过程。博客不必完美，持续更新更重要。

## 我的习惯

- 每周至少一篇，哪怕很短。
- 先用 Markdown 记草稿，再整理成文。
- 标题不超过 20 字。

## 引用

> 种一棵树最好的时间是十年前，其次是现在。

## 下一步

把评论区和通知做顺，让读者愿意留下痕迹。
""",
    },
]


class Command(BaseCommand):
    help = "创建演示数据：admin、demo 用户、3 个栏目、8 篇文章与评论"

    @transaction.atomic
    def handle(self, *args, **options):
        admin_password = os.environ.get("DJANGO_ADMIN_PASSWORD")
        generated = False
        if not admin_password:
            admin_password = secrets.token_urlsafe(18)
            generated = True

        admin, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if admin_created:
            admin.email = "admin@example.com"
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.SUCCESS("已创建 admin 用户。"))
        elif os.environ.get("DJANGO_ADMIN_PASSWORD"):
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write("admin 已存在，密码已按环境变量更新。")
        else:
            self.stdout.write("admin 已存在，保留原密码。")

        if generated:
            self.stdout.write(f"admin 随机密码（仅显示一次）：{admin_password}")
            password_file = Path(settings.BASE_DIR) / "logs" / "seed_admin_password.txt"
            password_file.parent.mkdir(parents=True, exist_ok=True)
            password_file.write_text(admin_password + "\n", encoding="utf-8")
            os.chmod(password_file, 0o600)
            self.stdout.write(f"随机密码已写入受保护文件：{password_file.resolve()}")

        demo, demo_created = User.objects.get_or_create(
            username="demo", defaults={"email": "demo@example.com"}
        )
        if demo_created:
            demo.set_password("demo12345")
            demo.save()
        self.stdout.write(self.style.SUCCESS("demo 账号：demo / demo12345"))

        columns = {}
        for title, slug in [
            ("技术笔记", "tech-notes"),
            ("生活随笔", "life-notes"),
            ("项目实战", "project-practice"),
        ]:
            column, _ = ArticleColumn.objects.get_or_create(
                slug=slug, defaults={"title": title}
            )
            columns[title] = column
        self.stdout.write(f"栏目就绪：{len(columns)} 个")

        authors = [admin, demo]
        created_articles = 0
        articles = []
        for index, item in enumerate(ARTICLES):
            article = Article.objects.filter(title=item["title"]).first()
            if article is None:
                article = Article.objects.create(
                    author=authors[index % 2],
                    title=item["title"],
                    body=item["body"],
                    column=columns[item["column"]],
                )
                article.tags.set(item["tags"])
                created_articles += 1
            articles.append(article)
        self.stdout.write(f"文章就绪：新增 {created_articles} 篇，总计 {len(articles)} 篇")

        # Comments (and notifications for the article author).
        if articles and not Comment.objects.filter(article=articles[0]).exists():
            first = articles[0]
            root = Comment.objects.create(
                article=first,
                user=demo,
                body="写得很清楚，虚拟环境和项目结构这块很有帮助！",
            )
            if first.author_id != demo.id:
                Notification.objects.create(
                    recipient=first.author,
                    actor=demo,
                    verb="commented",
                    target_article=first,
                    target_comment=root,
                )
            reply = Comment.objects.create(
                article=first,
                user=first.author,
                body="谢谢支持，后面会继续补部署细节。",
                parent=root,
            )
            if first.author_id != root.user_id:
                Notification.objects.create(
                    recipient=root.user,
                    actor=first.author,
                    verb="commented",
                    target_article=first,
                    target_comment=reply,
                )
        if len(articles) > 1 and not Comment.objects.filter(article=articles[1]).exists():
            Comment.objects.create(
                article=articles[1],
                user=demo,
                body="DRF 的分页参数能否支持前端自定义每页数量？",
            )
        self.stdout.write(self.style.SUCCESS("演示数据生成完成。"))
