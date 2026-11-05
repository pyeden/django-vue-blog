# 纸上集 · Django + Vue 个人博客

一个从零实现的个人博客：Django 负责内容、权限和 API，Vue 负责阅读与写作的界面。

- **后端**：Python 3.12 + Django 4.2 LTS + Django REST Framework + SQLite
- **前端**：Vue 3 + Vite + Pinia + Vue Router + Bootstrap 5
- **线上**：<https://seres-ai.com/djangovueblog/>
- **教程**：[`docs/`](docs/README.md)

## 功能

文章 CRUD、Markdown 渲染与代码高亮、封面、栏目、标签、分页、搜索、最热、浏览量、点赞（服务端幂等）、两级评论、通知、注册/登录/资料/头像/密码重置/删除账号、Django 后台、自动化测试、日志、子路径部署。

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

## 目录

```text
backend/   Django 项目与 API
frontend/  Vue 3 SPA
docs/      从零构建教程（15 章）
deploy/    nginx / gunicorn / release
DESIGN.md  数据模型与 API 设计
```

演示账号：`demo / demo12345`。管理员 `admin` 的密码只保存在部署机的数据目录，不写入仓库。
