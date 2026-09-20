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
- **部署**: Docker @ ivory（飞牛数据盘）+ ali1 FRP/nginx 入口

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

### 生产部署（简述）

生产不在本机。当前形态：

- **运行时**：`ssh ivory` → `/vol1/apps/nexus`，Docker 容器 `nexus`，宿主机端口 **18000**
- **入口**：`https://felixfeng.online`（ali1 nginx → frp `127.0.0.1:18000`）
- **数据**：生产库/配置在 ivory `data/db.sqlite3`、`data/nexus.env`（与本地测试库隔离）
- **同步代码**：rsync 排除 `data/`、`.env`、`db.sqlite3` 后 `docker compose up -d --build`

详见 `AGENTS.md`。

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
