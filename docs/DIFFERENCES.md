# 实作差异记录（写作素材）

记录 MacBook / Mac mini 上真实发生过的差异，写教程时直接引用。

## 环境

| 原教程 | 本实作 | 说明 |
| --- | --- | --- |
| Windows 10 | macOS 15.7.2 | 命令、路径、虚拟环境激活方式全变 |
| Python 3.7 | 3.12.2（MacBook，Homebrew） | Django 4.2 LTS 的最低推荐版本区间 |
| `env\Scripts\activate.bat` | `source .venv/bin/activate` | |
| `E:\django_project` | `~/work/django-vue-blog` | |
| Django 2.2 | Django 4.2 LTS | 原教程锁 2.2，本实作锁 4.2 |
| Bootstrap 4 + jQuery | Bootstrap 5 + Vue 3 | 不再用 jQuery 拼 DOM |
| Django 模板 | Vue SPA + DRF JSON | 前后端分离 |

## 实际遇到的问题

1. **Mac mini 直连 GitHub 被墙**：`curl https://github.com` 超时，`brew install python@3.12` 卡在 `brew update`。MacBook 可以直连，所以构建放在 MacBook。
2. **Mac mini 没有 Python 3.12**：系统只有 3.14，Homebrew 安装被 GitHub 卡住。改用 python.org 官方 3.12.10 pkg，`pkgutil --expand-full` 解包后放到 `~/Library/Frameworks`，用 `install_name_tool` 把绝对路径改成 `@executable_path`，再 `codesign -s -` 重签。`python -m venv` 正常，`ssl/sqlite3` 可用。
3. **nginx 8888 使用 PROXY protocol v2**：直接 `curl 127.0.0.1:8888` 返回 000，必须经 frp。验证公网用 `https://seres-ai.com/...`。
4. **子路径部署**：Vue `base=/djangovueblog/`，API `/djangovueblog/api/`，nginx 去掉前缀转发到 gunicorn；媒体与静态分别 alias。SPA 刷新回退到 `/djangovueblog/index.html`。
5. **端口**：gunicorn 8899；不要占用现有 8080/8090/8092/23366/7788。
6. **文件权限**：nginx worker 是 `nobody`，release、dist、media 需要 `a+rX`。

## 原创点

- 把原教程的“模板章节”重解释为“API + Vue 组件”，每章给出对应关系表。
- 用 DRF ViewSet 替代原教程的函数视图/类视图演进，但保留“为什么要类视图”的讲解。
- 点赞用 `ArticleLike` 唯一约束做幂等，而不是单纯 `likes += 1`。
- 评论用自关联 `parent` + 序列化递归，替代 django-mptt。
- 通知用轻量 `Notification` 模型，不引入 django-notifications-hq。
- 部署不是另买 VPS，而是挂到既有 `seres-ai.com` 的 nginx 子路径，走 frp 回源 Mac mini。
