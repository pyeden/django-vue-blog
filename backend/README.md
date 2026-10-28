# Django + Vue 个人博客 · 后端（macOS 实作版）

Python 3.12 + Django 4.2 LTS + Django REST Framework + SQLite 的后端 API。
所有数据模型与接口形状以仓库根目录 `SPEC.md` 为准。

## 环境要求

- macOS（Apple Silicon 示例使用 Homebrew Python）
- Python 3.12：`/opt/homebrew/bin/python3.12`
- 可选：`sqlite3`（备份用）

## 首次安装

```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 本地启动

```bash
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo          # 可选：生成演示数据
python manage.py runserver 127.0.0.1:8000
```

前端开发服务器（Vite，默认 5173）会把 `/api` 代理到 8000；
后端默认放行 `http://localhost:5173` / `http://127.0.0.1:5173` 的 CORS 与 CSRF 来源。
若端口不同，用环境变量覆盖（见下）。

### 认证流程

1. `GET /api/auth/csrf/` 获取 `csrftoken` Cookie。
2. 写请求携带 `X-CSRFToken` 请求头，并设置 `credentials: 'include'`。
3. `POST /api/auth/login/` / `POST /api/auth/register/` 建立 Session。
4. `GET /api/auth/me/` 获取当前用户。

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | 开发占位 key | 生产必须设置 |
| `DJANGO_DEBUG` | `True` | 生产设为 `False` |
| `DJANGO_ALLOWED_HOSTS` | 开发 `*`；生产 `localhost,127.0.0.1` | 逗号分隔 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | 逗号分隔，含协议 |
| `DJANGO_CORS_ALLOWED_ORIGINS` | 同上 | 逗号分隔 |
| `DJANGO_DB_PATH` | `backend/db.sqlite3` | SQLite 文件路径 |
| `DJANGO_LOG_LEVEL` | `INFO` | 日志级别 |
| `DJANGO_EMAIL_BACKEND` | console backend | 生产可换成 SMTP |
| `DJANGO_SECURE_COOKIES` | 生产 `True` | 控制 Secure Cookie |
| `DJANGO_ADMIN_PASSWORD` | 未设置则随机生成 | `seed_demo` 的 admin 密码 |

日志同时输出到 console 与 `logs/app.log`（5 MB × 3 轮转）。

## 测试

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

覆盖：注册/登录/me、Profile 信号、文章 CRUD 权限、slug 唯一、点赞幂等、
评论两级树与通知、搜索/筛选/分页、Markdown 渲染与 XSS 清洗、通知已读。

## 演示数据

```bash
export DJANGO_ADMIN_PASSWORD='你的密码'   # 可选
python manage.py seed_demo
```

- `admin`：超级用户。未提供 `DJANGO_ADMIN_PASSWORD` 时随机生成密码，
  仅在命令输出中打印一次，并写入 `logs/seed_admin_password.txt`（权限 0600）。
- `demo` / `demo12345`：普通测试用户。
- 3 个栏目、8 篇中文 Markdown 文章、示例评论与通知。
- 命令可重复执行，不会重复创建文章/评论。

## 生成迁移

```bash
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py check
```

## 生产部署（gunicorn）

```bash
cd backend
source .venv/bin/activate
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='从密钥管理系统注入'
export DJANGO_ALLOWED_HOSTS='seres-ai.com,www.seres-ai.com'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://seres-ai.com'
export DJANGO_CORS_ALLOWED_ORIGINS='https://seres-ai.com'
export DJANGO_DB_PATH='/path/to/release/data/db.sqlite3'

python manage.py migrate
python manage.py collectstatic --noinput

gunicorn config.wsgi:application \
  --bind 127.0.0.1:8001 \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
```

nginx 子路径示例：

```nginx
location /djangovueblog/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

静态资源由 nginx 指向 `backend/staticfiles/`，媒体文件指向 `backend/media/`（或 release 对应目录）。
前端 history 路由需 `try_files $uri $uri/ /djangovueblog/index.html`。

## 目录结构

```
backend/
├── config/            # settings / urls / wsgi / asgi
├── accounts/          # Profile、认证、资料、头像
├── blog/              # 栏目、文章、点赞、Markdown 渲染、seed_demo
├── comments/          # 两级评论
├── notices/           # 通知
├── logs/              # app.log（轮转）
├── media/             # 上传文件（封面、头像）
├── manage.py
├── requirements.txt
└── db.sqlite3         # 默认 SQLite（可用 DJANGO_DB_PATH 覆盖）
```

## API 速览

统一前缀 `/api`，响应形状见 `SPEC.md`。

- 认证：`auth/csrf/`、`auth/register/`、`auth/login/`、`auth/logout/`、`auth/me/`、`auth/password-reset/`
- 资料：`profile/`（GET/PATCH）、`profile/avatar/`（POST multipart）
- 文章：`articles/`（列表/创建）、`articles/{slug}/`（详情/改/删）、`articles/{slug}/like/`、`articles/hot/`
- 栏目/标签：`columns/`、`tags/`
- 评论：`articles/{slug}/comments/`（GET 树 / POST）、`comments/{id}/`（DELETE）
- 通知：`notifications/`、`notifications/read-all/`、`notifications/{id}/read/`

分页默认 `page_size=6`，可用 `?page_size=` 覆盖（上限 50）。
文章列表支持 `search`、`column`、`tag`、`ordering`（`created`、`total_views`、`likes` 等）。
