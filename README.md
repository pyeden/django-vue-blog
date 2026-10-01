# Django + Vue 个人博客（MacBook 实作版）

按 `stacklens/django_blog_tutorial` 的功能路线，在 macOS 上重做的一套个人博客：

- **后端**：Python 3.12 + Django 4.2 LTS + Django REST Framework + SQLite
- **前端**：Vue 3 + Vite + Pinia + Vue Router + Bootstrap 5
- **部署**：gunicorn + nginx 子路径，线上地址 <https://seres-ai.com/djangovueblog/>

原教程是 Django 模板 + Bootstrap 4；本实作改成前后端分离，功能对齐，但代码、结构、界面和部署方式都是重新实现的。完整重写教程在 [`docs/`](docs/README.md)。

## 功能

文章 CRUD、Markdown 渲染与代码高亮、封面、栏目、标签、分页、搜索、最热、浏览量、点赞、两级评论、通知、用户注册/登录/资料/头像、密码重置、Django 后台、自动化测试、日志、子路径部署。

## 本地启动

### 后端

```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 <http://127.0.0.1:5173>。开发环境把 `/api` 代理到 8000。

## 测试

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

## 生产部署

见 [`docs/40.部署.md`](docs/40.部署.md) 和 `deploy/` 下的脚本。

## 目录

```text
backend/   Django 项目与 API
frontend/  Vue 3 SPA
docs/      重写教程（43 章）
deploy/    nginx / gunicorn / release
```
