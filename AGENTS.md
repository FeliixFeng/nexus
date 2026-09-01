# AGENTS.md — Nexus 项目指南

> 本文件供 AI 助手阅读，确保每次开发会话都能理解项目全貌和约定。

## 项目简介

Nexus 是一个个人模块化门户平台，聚合笔记、链接、动态、学术研究、RSS 等内容。
视觉风格：暗色高级感，首页有星空粒子动画。

## 技术栈

- **后端**：Django 5 + Python 3.11 + SQLite
- **前端**：HTMX + Tailwind CSS (CDN) + 原生 JS
- **部署**：systemd + gunicorn (非 Docker)
- **包管理**：uv
- **版本控制**：Git + GitHub（仓库：FeliixFeng/nexus）

## 项目结构

```
nexus/
├── config/                    ← Django 项目配置
│   ├── settings.py            ← 配置（敏感值从 .env 读取）
│   ├── urls.py                ← 主路由
│   └── wsgi.py
├── nexus_core/                ← 核心模块（首页、动态、监控、RSS、阅读）
│   ├── models.py              ← NowItem, Activity
│   ├── views.py               ← 首页、动态页
│   ├── api_views.py           ← NowItem, Activity CRUD API
│   ├── monitor_views.py       ← 服务器监控
│   ├── rss_views.py           ← RSS 阅读器
│   ├── read_views.py          ← 阅读聚合页
│   └── pin_utils.py           ← PIN 认证工具
├── blog/                      ← 博客/笔记模块
│   ├── models.py              ← Post, Tag
│   ├── views.py               ← 文章列表、详情、CRUD
│   ├── api_views.py           ← 笔记 API（导入、CRUD）
│   └── templatetags/
│       └── markdown_extras.py ← Markdown 渲染 + Pygments 代码高亮
├── links/                     ← 链接聚合模块
│   ├── models.py              ← Link
│   ├── views.py               ← 链接列表
│   └── api_views.py           ← 链接 API
├── research/                  ← 学术研究模块
│   ├── models.py              ← Paper, Experiment
│   └── views.py               ← 论文/实验 CRUD
├── monitor/                   ← 监控探针脚本（独立部署到各服务器）
│   └── monitor_agent.py
├── templates/                 ← 统一模板目录
│   ├── base.html              ← 基础模板
│   ├── components/            ← 公共组件（navbar, pin_modal）
│   ├── nexus_core/            ← 核心模块模板
│   ├── blog/                  ← 博客模板
│   ├── links/                 ← 链接模板
│   └── research/              ← 学术模块模板
├── static/                    ← 静态文件
│   ├── css/                   ← base.css, custom.css, home.css
│   ├── js/                    ← base.js, home.js
│   ├── favicon.svg
│   └── manifest.json
├── .env                       ← 敏感配置（不提交）
├── .env.example               ← 配置模板
├── db.sqlite3                 ← SQLite 数据库（不提交）
├── pyproject.toml             ← uv 项目配置
├── Dockerfile                 ← Docker 配置（备用）
├── docker-compose.yml         ← Docker Compose（备用）
├── nexus.service              ← systemd 服务文件
├── start_nexus.sh             ← 服务重启脚本
├── AGENTS.md                  ← 本文件
└── PLAN.md                    ← 整体规划
```

## Django Apps

| App | 职责 | 模型 | 主要视图 |
|-----|------|------|----------|
| nexus_core | 首页、动态、监控、RSS、阅读 | NowItem, Activity | home, now_page, monitor, rss, read |
| blog | 博客/笔记 | Post, Tag | post_list, post_detail, CRUD |
| links | 链接聚合 | Link | link_list |
| research | 学术研究 | Paper, Experiment | paper CRUD, experiment CRUD |

## 配置管理

- 敏感信息放 `.env`（已 gitignored），参考 `.env.example`
- `settings.py` 通过 `python-dotenv` 加载 `.env`
- **绝对不要在代码里硬编码密钥、PIN、token**
- 当前敏感配置：`DJANGO_SECRET_KEY`、`NEXUS_PIN`、`NEXUS_API_KEY`

## 权限模型

- **浏览**：所有人可访问所有页面，无需登录
- **编辑**：输入 6 位 PIN 码解锁编辑功能
- **无用户系统**：没有注册/登录，没有独立后台
- PIN 验证通过 cookie + session，有效期 7 天
- API 认证：支持 PIN（浏览器）或 X-Nexus-Key header（程序化调用）

## 开发约定

### 代码风格
- Django 后端保持简单，视图函数为主（不用 class-based views）
- 模板继承 `base.html`，用 `{% include %}` 复用组件
- Tailwind 用 CDN，自定义样式用独立 CSS 文件

### 模板继承
```html
{% extends 'base.html' %}
{% load static %}

{% block title %}页面标题{% endblock %}
{% block extra_css %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_js %}{% endblock %}
```

### HTMX 编辑模式
- 编辑按钮在页面底部，PIN 解锁后才显示
- 用 `hx-get` / `hx-post` / `hx-put` / `hx-delete` 操作
- 返回 HTML fragment（不用 JSON API）
- 用 `hx-swap="outerHTML"` 替换节点

### 数据库操作
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

## 部署架构

```
用户 → felixfeng.online (阿里云 nginx)
         ↓ 反代到 :8000
       Django on ali1 (47.121.181.198)
```

- **ali1**：阿里云服务器，运行 nginx + gunicorn
- **域名**：`felixfeng.online`
- **服务管理**：`systemctl restart nexus.service`
- gunicorn 开启了 `--reload`，代码更新后自动生效

## 本地开发

```bash
# 克隆代码
gh repo clone FeliixFeng/nexus ~/code/projects/nexus
cd ~/code/projects/nexus

# 安装依赖
uv venv && uv pip install -r pyproject.toml

# 本地运行
python manage.py runserver
```

## 部署同步

```bash
# 同步代码到服务器（排除 .env, db, venv, pycache, .git）
rsync -avz --exclude '.env' --exclude 'db.sqlite3' --exclude '.venv' --exclude '__pycache__' --exclude '.git' ~/code/projects/nexus/ root@ali1:/data/app/nexus/

# gunicorn --reload 会自动生效，无需重启
```

## 快捷键

- `/`：聚焦搜索框
- `E`：打开 PIN 输入
- `Esc`：关闭弹窗

## 当前功能清单

- 首页：Bento Grid（时间、服务器、笔记、服务、动态五张卡片）
- 笔记页：Markdown 渲染 + 代码高亮 + 标签筛选 + 搜索
- 链接页：3列卡片 + hover 发光
- 动态页：NowItem + Activity 里程碑
- 学术模块：论文管理 + 实验日志
- 服务器监控：CPU/内存/磁盘/Docker 容器状态
- RSS 阅读器：多源聚合 + 代理支持
- PIN 码编辑权限
- 星空粒子动画 + 鼠标视差
- 导航栏滚动隐藏/毛玻璃
- 移动端底部导航栏
- 回到顶部按钮
- 快捷键支持
