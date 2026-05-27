# Nexus — 个人模块化平台

> 可长期维护、可自由扩展的个人平台
> 高级感首页 + 笔记/文章 + 服务聚合 + 后续按需扩展

## ✨ 特性

- 🎨 **高级感设计** — 暗色主题、毛玻璃效果、微动效
- 📝 **笔记系统** — Markdown写作、标签、搜索、草稿
- 🔗 **链接聚合** — 服务器服务、外部链接统一管理
- 🔒 **PIN码管理** — 无需用户登录，PIN码解锁编辑权限
- 📱 **响应式** — 完美适配电脑和手机
- 🧩 **模块化** — Django Apps架构，轻松扩展新功能

## 🛠️ 技术栈

- **后端**: Django 5 + Python 3.11
- **数据库**: SQLite（零配置）
- **前端**: Django模板 + HTMX + Tailwind CSS
- **部署**: Docker + Docker Compose

## 🚀 快速开始

### 本地开发

```bash
# 克隆项目
git clone https://github.com/FeliixFeng/nexus.git
cd nexus

# 安装依赖
uv sync

# 数据库迁移
uv run python manage.py migrate

# 创建管理员
uv run python manage.py createsuperuser

# 启动开发服务器
uv run python manage.py runserver
```

访问 http://localhost:8000

### Docker部署

```bash
# 复制环境变量
cp .env.example .env

# 修改.env中的配置
# DJANGO_SECRET_KEY=你的密钥
# NEXUS_PIN=你的PIN码

# 启动服务
docker compose up -d
```

访问 http://your-server:8080

## 📁 项目结构

```
nexus/
├── config/          # Django项目配置
├── nexus_core/      # 核心模块（首页、PIN验证）
├── blog/            # 笔记/文章模块
├── links/           # 链接聚合模块
├── templates/       # 公共模板
├── static/          # 静态文件
├── media/           # 用户上传
└── docker-compose.yml
```

## 🔐 PIN码管理

默认PIN码: `1234`

修改方式：
1. 环境变量: `NEXUS_PIN=你的PIN码`
2. 或修改 `config/settings.py` 中的 `NEXUS_PIN`

## 📦 添加新模块

```bash
# 创建新的Django App
uv run python manage.py startapp your_app

# 在config/settings.py中注册
INSTALLED_APPS = [
    ...
    'your_app',
]

# 配置URL路由
# config/urls.py
urlpatterns = [
    ...
    path('your-app/', include('your_app.urls')),
]
```

## 📄 License

MIT License
