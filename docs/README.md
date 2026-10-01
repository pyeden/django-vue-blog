# 在 MacBook 上重做 Django + Vue 个人博客

这不是对原教程的逐字搬运，而是我在 MacBook 上把 `stacklens/django_blog_tutorial` 的 43 篇内容重新实现一遍后，按实际代码、实际报错、实际命令写下的版本。

## 和原教程的关系

- 功能路线一致：从创建 app、Model、CRUD、登录注册，到分栏、标签、评论、通知、点赞、测试、日志、部署。
- 技术栈按今天的习惯重做：
  - 原教程：Windows 10 + Python 3.7 + Django 2.2 + Bootstrap 4 + Django 模板。
  - 本实作：macOS + Python 3.12 + Django 4.2 LTS + DRF + SQLite；前端 Vue 3 + Vite + Pinia + Bootstrap 5。
- 原教程里“写模板、模板过滤器、Ajax 拼 HTML”的章节，在前后端分离后分别落到 Vue 组件、API 序列化、axios 请求上；每章都会说明对应关系。

## 章节索引

| # | 原文章 | 本实作章节 | 对应实现 |
| --- | --- | --- | --- |
| 01 | 前言 | [01.为什么重做](01.为什么重做.md) | 项目定位 |
| 02 | 教程的开发环境 | [02.macOS 开发环境](02.macOS开发环境.md) | Homebrew Python 3.12、Node、venv |
| 03 | 创建app | [03.创建 Django 项目与 app](03.创建项目与app.md) | config + blog/accounts/comments/notices |
| 04 | 编写Model | [04.数据模型](04.数据模型.md) | Article/Column/Comment/Profile |
| 05 | View视图初探 | [05.第一个 API 与后台](05.第一个API与后台.md) | DRF + admin |
| 06 | View及Template | [06.列表 API 与 Vue 首页](06.列表API与Vue首页.md) | ArticleListAPI + HomeView |
| 07 | 使用Bootstrap改写模板 | [07.前端布局](07.前端布局.md) | Bootstrap 5 + 设计系统 |
| 08 | 编写文章详情页面 | [08.文章详情](08.文章详情.md) | slug 详情 + Markdown |
| 09 | 使用Markdown书写文章 | [09.Markdown 渲染](09.Markdown渲染.md) | markdown + bleach + 高亮 |
| 10 | 发布新的文章 | [10.写作与发布](10.写作与发布.md) | 编辑器 + 封面上传 |
| 11 | 删除文章 | [11.安全删除](11.安全删除.md) | 权限 + 确认弹窗 |
| 12 | 更新文章 | [12.编辑文章](12.编辑文章.md) | PATCH + 权限 |
| 13 | 用户的登录和退出 | [13.登录与退出](13.登录与退出.md) | Session + CSRF |
| 14 | 用户的注册 | [14.注册](14.注册.md) | 注册 API + 校验 |
| 15 | 用户的删除 | [15.删除账号](15.删除账号.md) | 自删 + 级联 |
| 16 | 重置用户密码 | [16.重置密码](16.重置密码.md) | 邮件令牌 |
| 17 | 拓展用户信息 | [17.用户资料](17.用户资料.md) | Profile |
| 18 | 上传头像 | [18.头像上传](18.头像上传.md) | ImageField + multipart |
| 19 | 文章分页 | [19.分页](19.分页.md) | DRF Pagination |
| 20 | 浏览量 | [20.浏览量](20.浏览量.md) | F() 原子自增 |
| 21 | 最热文章 | [21.最热文章](21.最热文章.md) | ordering + 侧栏 |
| 22 | 搜索文章 | [22.搜索](22.搜索.md) | Q 对象 + 高亮 |
| 23 | 文章目录 | [23.文章目录](23.文章目录.md) | markdown toc + 滚动高亮 |
| 24 | 评论 | [24.评论](24.评论.md) | Comment 模型 + 表单 |
| 25 | 课间休息 | [25.课间休息](25.课间休息.md) | 阶段复盘 |
| 26 | 基于类的视图 | [26.ViewSet](26.ViewSet.md) | DRF ViewSet |
| 27 | 文章栏目 | [27.栏目](27.栏目.md) | Column 外键 |
| 28 | 文章标签 | [28.标签](28.标签.md) | django-taggit |
| 29 | 文章标题图 | [29.封面图](29.封面图.md) | 图片处理 |
| 30 | 富文本编辑器 | [30.Markdown 编辑器](30.Markdown编辑器.md) | 编辑器 + 预览 |
| 31 | 四个重要的小功能 | [31.四个小功能](31.四个小功能.md) | 回到顶部/粘性侧栏/页脚/图标 |
| 32 | 多级评论 | [32.多级评论](32.多级评论.md) | parent 外键 + 树 |
| 33 | 消息通知 | [33.通知](33.通知.md) | Notification |
| 34 | 锚点定位 | [34.锚点](34.锚点.md) | heading id |
| 35 | 第三方登录 | [35.GitHub 登录](35.GitHub登录.md) | OAuth（可选） |
| 36 | 自动化测试 | [36.测试](36.测试.md) | Django TestCase |
| 37 | 日志记录 | [37.日志](37.日志.md) | LOGGING + 轮转 |
| 38 | 模板过滤器和标签 | [38.前端格式化](38.前端格式化.md) | Vue 过滤器/组件 |
| 39 | 点赞功能 | [39.点赞](39.点赞.md) | ArticleLike 幂等 |
| 40 | 将项目部署到云服务器 | [40.部署](40.部署.md) | gunicorn + nginx 子路径 |
| 41 | 期末总结 | [41.总结](41.总结.md) | 复盘 |
| 42 | 小功能集合贴 | [42.快捷导航](42.快捷导航.md) | 上下篇/快捷入口 |
| 43 | 读者常见问题 | [43.常见问题](43.常见问题.md) | 实作 FAQ |

## 运行本项目

见 [02.macOS开发环境](02.macOS开发环境.md) 与仓库根目录 `README.md`（代码完成后补）。
