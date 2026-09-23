# Nexus — 个人聚合门户

> 自用链接入口 + 状态展示 + 偶尔对外展示  
> **不是博客站、不是笔记仓库**（笔记写作以 Obsidian 本地为准）

当前形态见基线 spec：[`specs/2026-09-20-nexus-baseline-v1.md`](specs/2026-09-20-nexus-baseline-v1.md)  
AI 协作规则见 [`AGENTS.md`](AGENTS.md)（权威文档，改 IA/流程必须同步更新）。

## ✨ 特性

- 🏠 **五项导航** — 首页 · 资讯 · 链接 · 状态 · 其他，桌机/手机一致
- 📰 **资讯** — 精选 / 待读 / 全部 + 日报（当前 mock 数据，待接 rss-hub）
- 🔗 **链接聚合** — 服务器服务、外部链接统一管理，仓库内本地图标
- 📡 **状态展示** — Now（进行中）+ 里程碑时间线
- 🔒 **PIN 码管理** — 无需用户登录，6 位 PIN 解锁页面编辑
- 🎨 **深色设计** — 靛蓝强调色、统一设计 token、响应式
- 🧩 **模块化** — Django Apps 架构，按需扩展（见规格路线图）

## 🛠️ 技术栈

- **后端**: Django 5 + Python 3.11
- **数据库**: SQLite（零配置）
- **前端**: Django 模板 + HTMX + Tailwind CDN
- **部署**: Docker @ ivory（飞牛）`:18000` + ali1 FRP/nginx 入口

## 🚀 快速开始

### 本地开发

```bash
cd ~/code/project/nexus

# 安装依赖
uv sync

# 数据库迁移
uv run python manage.py migrate

# 启动开发服务器
uv run python manage.py runserver
```

访问 http://localhost:8000

### 生产部署

生产不在本机，当前拓扑：

- **运行时**: `ssh ivory` → `/vol1/apps/nexus`，Docker 容器 `nexus`，宿主机端口 **18000**
- **入口**: `https://felixfeng.online`（ali1 nginx → frp → `127.0.0.1:18000`）
- **数据**: ivory `data/db.sqlite3`、`data/nexus.env`（与本地测试库隔离，**禁止 Mac ↔ ivory 同步**）
- **发布流程**: 规则详见 `AGENTS.md`（验收前不 commit；rsync 排除 `data/`、`.env`、`db.sqlite3`）

## 📁 项目结构

```
nexus/
├── specs/           # 需求/设计（权威规格，先读这里）
├── config/          # Django 项目配置
├── nexus_core/      # 壳 + 首页/状态/其他 + NowItem/Activity
├── links/           # 链接聚合（Link）
├── rss/             # 资讯：精选/待读/全部（mock → 待接 hub）
├── blog/            # 休眠：不进导航
├── research/        # 休眠
├── monitor/         # agent 脚本，无产品 UI
├── templates/       # 公共模板
├── static/          # 样式/图标/静态资源
└── docker-compose.yml
```

> `PLAN.md` 为早期规划草稿，**已被 `specs/` 取代**，仅作历史参考。

## 🔐 PIN 码管理

浏览免登录；编辑需 6 位 PIN（cookie/session），API 亦接受 `X-Nexus-Key`。

- 环境变量: `NEXUS_PIN=你的PIN码`
- 或修改 `config/settings.py` 中的 `NEXUS_PIN`

## 📦 添加新模块

```bash
uv run python manage.py startapp your_app
# 注册到 config/settings.py 的 INSTALLED_APPS
# 配置 config/urls.py 路由
```

改导航/IA 前必须先更新 `AGENTS.md` + 相关 spec。

## 📄 License

MIT License
