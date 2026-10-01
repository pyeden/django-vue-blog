# Django + Vue 个人博客（MacBook 实作版）规格

## 目标
按 stacklens/django_blog_tutorial 的 43 篇功能路线，在 macOS 上用现代栈重做：
- 后端：Python 3.12 + Django 4.2 LTS + DRF + SQLite
- 前端：Vue 3 + Vite + Pinia + Vue Router + Bootstrap 5
- 部署：https://seres-ai.com/djangovueblog/

## 目录
- backend/  Django 项目 + API
- frontend/ Vue 3 SPA
- docs/     重写教程（按原文章顺序）
- deploy/   nginx / gunicorn / release 脚本

## 后端数据模型
- ArticleColumn: title, slug, created
- Article: author(FK User), title, slug(unique), body(markdown), body_html(rendered), cover(ImageField), column(FK nullable), tags(taggit), total_views, likes, created, updated
- ArticleLike: article(FK), user(FK), created; unique(article,user)
- Comment: article(FK), user(FK), body, parent(FK self nullable), created, active
- Notification: recipient(FK User), actor(FK User nullable), verb, target_article(FK nullable), target_comment(FK nullable), unread, created
- Profile: user(OneToOne), phone, bio, avatar(ImageField)

## API（统一前缀 /api）
认证（Session + CSRF）
- GET  /api/auth/csrf/                 设置 csrftoken cookie
- POST /api/auth/register/             {username,email,password1,password2}
- POST /api/auth/login/                {username,password} -> {user}
- POST /api/auth/logout/
- GET  /api/auth/me/                   -> {user|null}
- POST /api/auth/password-reset/       {email} 发送重置邮件（console backend）
用户资料
- GET/PATCH /api/profile/              {phone,bio}
- POST /api/profile/avatar/            multipart avatar
文章
- GET  /api/articles/                  ?page=&page_size=&search=&column=&tag=&ordering=-created|created|-total_views|-likes
- GET  /api/articles/{slug}/
- POST /api/articles/                  auth；{title,body,column?,tags[]}
- PATCH /api/articles/{slug}/          作者或 staff
- DELETE /api/articles/{slug}/         作者或 staff
- POST /api/articles/{slug}/like/      登录；切换点赞，返回 {liked,likes}
- GET  /api/articles/hot/              按 total_views 前 5
- GET  /api/columns/
- GET  /api/tags/
评论
- GET  /api/articles/{slug}/comments/  返回嵌套树
- POST /api/articles/{slug}/comments/  {body,parent_id?} 登录
- DELETE /api/comments/{id}/           作者或 staff
通知
- GET  /api/notifications/             登录；最近 20 条 + unread_count
- POST /api/notifications/read-all/    登录
- POST /api/notifications/{id}/read/

## 前端页面
- /                 首页：文章列表 + 侧栏（搜索、最热、栏目、标签）
- /article/:slug   详情：Markdown、目录、点赞、评论树、作者操作
- /write, /edit/:slug  写作/编辑（Markdown 编辑 + 预览 + 封面上传）
- /login /register /reset-password
- /profile          资料与头像
- /search?q=        搜索结果
- /column/:slug /tag/:slug 归档
- /notifications    通知中心
- 404

## 验收标准
1. MacBook 本地：后端 `python manage.py test` 全绿；`npm run build` 成功。
2. 冒烟：注册/登录、发文、改文、删文、点赞（幂等）、评论（两级）、通知、搜索、分页、最热、头像上传全部可用。
3. 生产：https://seres-ai.com/djangovueblog/ 首页 200；静态资源 200；API 200；刷新任意前端路由不 404。
4. 安全：未登录写操作 403/401；非作者改删 403；生产 DEBUG=False；CSRF 生效。
5. 教程：docs/ 下按原 43 篇顺序给出重写版，含 macOS 实际命令与差异说明。

## 开发约束
- 所有构建在 MacBook 完成，不在 Mac mini 构建。
- 不把生产密钥写入仓库；用环境变量。
- 生产使用 gunicorn + nginx 子路径，SQLite 文件放在 release 的 data/。

## API 响应形状（前端按此实现）
user: {id, username, email, is_staff, profile:{phone,bio,avatar}}
article list item: {id,title,slug,excerpt,cover,author:{username,avatar},column:{title,slug}|null,tags:["..."],total_views,likes,comment_count,created,updated}
article detail: list item + {body, body_html, toc:[{level,text,anchor}], liked:boolean}
comment tree item: {id,body,user:{username,avatar},created,parent_id,replies:[...]}
notification: {unread_count, results:[{id,verb,actor,article:{title,slug}|null,unread,created}]}
like: {liked,likes}
auth login/register/me: {user}
errors: {detail} 或 {field:[msg]}
