# 设计说明

## 目标

做一个能长期写、能安心读的个人博客：写作端足够顺手，阅读端足够安静，部署能挂在一个既有域名的子路径下。

## 技术选择

- 后端：Django 4.2 LTS + DRF。Django 提供用户、权限、后台和 ORM；DRF 提供 JSON API。
- 前端：Vue 3 + Vite。页面是 SPA，构建产物可以直接交给 nginx。
- 数据库：SQLite。个人博客的写入量很低，单文件备份足够；需要时再换 PostgreSQL。
- 认证：Django Session + CSRF。没有引入 JWT，避免前端存 token 的额外风险。

## 数据模型

- `ArticleColumn`：栏目，文章的一对多归档。
- `Article`：标题、slug、Markdown 源文、渲染后的 HTML、封面、栏目、标签、浏览量、点赞数、作者、时间。
- `ArticleLike`：用户与文章的唯一关联，保证点赞幂等。
- `Comment`：文章评论，自关联 `parent`，两级树。
- `Notification`：评论通知，记录接收者、触发者、文章和评论。
- `Profile`：用户扩展资料（电话、简介、头像），与 `User` 一对一。

## API 形状

统一前缀 `/api`：

- `auth/csrf/`、`auth/register/`、`auth/login/`、`auth/logout/`、`auth/me/`
- `auth/password-reset/`、`auth/password-reset/confirm/`、`auth/delete/`
- `profile/`、`profile/avatar/`
- `articles/`（列表/创建）、`articles/{slug}/`（详情/改/删）
- `articles/{slug}/like/`、`articles/{slug}/cover/`、`articles/hot/`
- `columns/`、`tags/`
- `articles/{slug}/comments/`、`comments/{id}/`
- `notifications/`、`notifications/read-all/`、`notifications/{id}/read/`
- `health/`

分页默认 6；列表支持 `search`、`column`、`tag`、`ordering`。文章详情返回 `body_html` 和 `toc`。

## 前端结构

- `views/`：首页、详情、写作、编辑、认证、资料、归档、通知、404。
- `components/`：文章卡片、侧栏、目录、评论树、编辑器、封面上传、标签输入。
- `stores/`：认证、通知、栏目/标签元数据、toast。
- `api/`：axios 客户端与 CSRF 处理。

## 部署

MacBook 上构建；产物同步到 Mac mini。gunicorn 监听 `127.0.0.1:8899`，launchd 守护；nginx 把 `/djangovueblog/` 指向前端 dist，把 `/djangovueblog/api/` 转发给 gunicorn。媒体与 collectstatic 由 nginx alias 提供，SPA 路由回退到 `index.html`。

## 不做什么

不做多租户、不做实时协作、不做复杂推荐；先把写作、阅读、评论这条主链路做扎实。
