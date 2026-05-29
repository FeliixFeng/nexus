# AGENTS.md — Nexus 项目指南

> 本文件供 AI 助手阅读，确保每次开发会话都能理解项目全貌和约定。
> 最后更新：2026-05-27

## 项目简介

Nexus 是一个个人模块化门户平台，聚合个人服务链接、笔记、动态等内容。
视觉风格：暗色高级感，首页有星空粒子动画。

## 技术栈

- **后端**：Django 5 + Python 3.11 + SQLite
- **前端**：HTMX + Tailwind CSS 4 + 原生 JS
- **部署**：Docker（可选），目前用 Django 开发服务器
- **包管理**：uv（不用 pip）
- **版本控制**：Git + GitHub（仓库：FeliixFeng/nexus）

## 启动项目

```bash
cd ~/projects/nexus
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## 项目结构

```
nexus/
├── AGENTS.md              ← 你正在读的这个文件
├── PLAN.md                ← 整体规划（概念设计、目标、里程碑）
├── .env                   ← 敏感配置（不提交）
├── .env.example           ← 配置模板（提交）
├── config/
│   ├── settings.py        ← Django 配置（敏感值从 .env 读取）
│   ├── urls.py            ← 路由：'/' nexus_core, '/blog/' blog, '/links/' links
│   └── wsgi.py
├── nexus_core/            ← 核心应用（首页、笔记、动态）
│   ├── models.py          ← Note, Activity 模型
│   ├── views.py           ← home, notes, note_detail, activities 视图
│   ├── templatetags/
│   │   └── markdown_extras.py  ← Markdown 渲染 + Pygments 代码高亮
│   └── admin.py
├── blog/                  ← 博客应用（暂空，预留）
├── links/                 ← 链接应用
│   ├── models.py          ← Link 模型
│   ├── views.py           ← links 视图
│   └── admin.py
├── templates/
│   ├── base.html          ← 基础模板（导航、PIN弹窗、页脚）
│   ├── components/
│   │   ├── navbar.html    ← 导航栏 + 移动端抽屉侧边栏
│   │   └── pin_modal.html ← PIN 解锁模态框
│   └── nexus_core/
│       ├── home.html      ← 首页 Bento Grid
│       ├── notes.html     ← 笔记列表
│       ├── note_detail.html ← 笔记详情
│       └── activities.html  ← 动态/活动页面
├── static/
│   ├── css/
│   │   ├── base.css       ← 全局样式（导航、prose、PIN、回到顶部）
│   │   └── home.css       ← 首页专属样式（Bento、卡片、动画、光球）
│   ├── js/
│   │   ├── base.js        ← 全局逻辑（导航、时钟、快捷键、PIN验证）
│   │   └── home.js        ← 首页动画（星空、粒子、星座连线、光球、鼠标视差）
│   └── vendor/
│       └── gsap/          ← GSAP 3.13.1（CDN 回退，目录 gitignored）
└── db.sqlite3             ← SQLite 数据库（不提交）
```

## 配置管理

- 敏感信息放 `.env`（已 gitignored），参考 `.env.example`
- `settings.py` 通过 `python-dotenv` 加载 `.env`
- **绝对不要在代码里硬编码密钥、PIN、token**
- 当前敏感配置：`DJANGO_SECRET_KEY`、`NEXUS_PIN`

## 权限模型

- **浏览**：所有人可访问所有页面，无需登录
- **编辑**：输入 6 位 PIN 码解锁编辑功能（弹窗输入框）
- **无用户系统**：没有注册/登录，没有独立后台
- **编辑方式**：页面内联编辑（HTMX），不跳转 /admin/
- PIN 验证通过 cookie（`nexus_pin`）+ session 记录，有效期 24 小时

## 开发约定

### 代码风格
- Django 后端保持简单，视图函数为主（不用 class-based views）
- 模板继承 `base.html`，用 `{% include %}` 复用组件
- CSS 全局样式放 `base.css`，页面专属样式放对应文件
- JS 全局逻辑放 `base.js`，页面专属逻辑放对应文件
- Tailwind 用 CDN，自定义样式用 `<style>` 标签或独立 CSS 文件

### 模板继承
```html
{% extends 'base.html' %}
{% load static %}
{% load markdown_extras %}

{% block title %}页面标题{% endblock %}
{% block extra_head %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_js %}{% endblock %}
```

### 数据库操作
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell  # Django shell 操作数据
```

### HTMX 编辑模式
- 编辑按钮在页面底部，PIN 解锁后才显示
- 用 `hx-get` / `hx-post` / `hx-put` / `hx-delete` 操作
- 返回 HTML fragment（不用 JSON API）
- 用 `hx-swap="outerHTML"` 替换节点

## 设计约束

1. **好看优先**：视觉效果 > 功能复杂度
2. **暗色主题**：深灰/黑色背景，紫蓝渐变点缀
3. **响应式**：桌面端大字体撑满，移动端右侧抽屉侧边栏（w-44）
4. **不用传统后台管理**：所有编辑内联在页面上
5. **不用左侧菜单**：移动端用右侧抽屉
6. **简洁实用**：不加花哨不实用的功能

## 部署架构

```
用户 → felixfeng.online (阿里云 nginx)
         ↓ 反代到 :9000
       frp tunnel (阿里云 frps → solar frpc)
         ↓ 转发到 :8000
       Django on solar (100.118.12.82)
```

- **solar**：开发服务器，Django 运行在这里
- **阿里云 (47.121.181.198)**：nginx + frps，域名入口
- **域名**：`felixfeng.online`（Nexus 主站）
- 正式部署时换 gunicorn + systemd，目前用 `runserver`

## 常用数据操作

```python
# Django shell
from nexus_core.models import Note, Activity
from links.models import Link

# 添加链接
Link.objects.create(name='名称', url='https://...', icon='🔗', category='分类', sort_order=0)

# 添加笔记
Note.objects.create(title='标题', content='Markdown 内容')

# 添加动态
Activity.objects.create(content='动态内容', icon='📌', sort_order=0)

# 删除
Link.objects.filter(name='名称').delete()
```

## 快捷键

- `/`：聚焦搜索框
- `E`：打开 PIN 输入
- `Esc`：关闭弹窗

## 当前功能清单

- ✅ 首页：Bento Grid（时间、笔记、服务、动态四张卡片）
- ✅ 笔记页：Markdown 渲染 + 代码高亮
- ✅ 链接页：3列卡片 + hover 发光
- ✅ 活动/动态页：可编辑的活动列表
- ✅ PIN 码编辑权限
- ✅ 星空粒子动画 + 鼠标视差
- ✅ 导航栏滚动隐藏/毛玻璃
- ✅ 移动端右侧抽屉侧边栏
- ✅ 回到顶部按钮
- ✅ 快捷键支持

## 待开发

- 笔记搜索功能
- 标签/分类系统
- 语录轮换做成可编辑
- 正式部署（gunicorn + systemd）
- 可能的未来模块：书签、RSS、天气等
