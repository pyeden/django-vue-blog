# macOS 实作笔记

这些是构建过程中真实遇到、值得记下来的问题。不是教程章节，但排查时很有用。

## 1. 中文 slug 的路由
Django 的 `<slug:slug>` 只匹配 ASCII。标题是中文时，`slugify(allow_unicode=True)` 会生成中文 slug，路由匹配不到。解决：
- `ArticleViewSet` 设 `lookup_value_regex = r"[^/.]+"`
- 评论路由用 `<str:slug>`
- 前端跳转用 `encodeURIComponent`

## 2. 登录后的 CSRF
Django `login()` 会轮换 CSRF token。前端登录成功后要重新 `GET /api/auth/csrf/`，读新的 `csrftoken` cookie，再发写请求。否则会出现“明明登录了却 403”。

## 3. 系统代理拖垮 pip
macOS 的系统代理可能指向已经退出的端口。安装依赖时强制直连：

```bash
export no_proxy='*' NO_PROXY='*' HTTP_PROXY='' HTTPS_PROXY='' ALL_PROXY=''
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

## 4. nginx 子路径
- 前端 `base=/djangovueblog/`，后端 API `/djangovueblog/api/`。
- `proxy_pass http://127.0.0.1:8899/api/;` 末尾的 `/` 会去掉 `/djangovueblog/api/` 前缀。
- SPA 刷新要 `try_files $uri $uri/ /djangovueblog/index.html;`。
- 媒体与 collectstatic 用 alias，不要让 Django 在 `DEBUG=False` 下处理静态文件。

## 5. nginx 改完要 reload
`nginx -t` 只检查语法，不会让配置生效。需要 `nginx -s reload`。如果 nginx 由 launchd 以 root 运行，reload 需要管理员权限。

## 6. SQLite 与多 worker
gunicorn 多 worker 写 SQLite 时要注意锁等待。个人博客写入少，3 个 worker 足够；如果写操作变多，换 PostgreSQL 比调 SQLite 更省事。

## 7. 封面与头像 URL
生产环境要设 `DJANGO_MEDIA_URL=/djangovueblog/media/`，否则 `request.build_absolute_uri()` 会生成不带子路径的 URL。nginx 再用 alias 指向数据目录。

## 8. 前端构建不要在低配机器上做
Vite 构建会在几分钟内吃满 CPU。把构建放在开发机，部署机只接收 `dist` 与后端代码，能避免线上服务被构建拖慢。
