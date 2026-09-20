# AGENTS.md — Nexus 项目指南

> 本文件供 AI 助手阅读，确保每次开发会话都能理解项目全貌和约定。
> **本项目由 AI 全权管理代码与部署文档；只用主工作区 `~/code/project/nexus`，不使用 git worktree。**

## 项目简介

Nexus 是一个个人模块化门户平台，聚合笔记、链接、动态、学术研究、RSS 等内容。
视觉风格：暗色高级感，首页有星空粒子动画。

## 技术栈

- **后端**：Django 5 + Python 3.11 + SQLite
- **前端**：HTMX + Tailwind CSS (CDN) + 原生 JS
- **生产部署**：Docker Compose @ ivory（飞牛 OS）+ ali1 仅作 FRP/nginx 入口
- **本地开发**：uv + `manage.py runserver`
- **版本控制**：Git + GitHub（仓库：FeliixFeng/nexus）主工作区单副本

## 主机与拓扑（2026-09-20 起）

| 主机 | SSH | 角色 |
|------|-----|------|
| Mac | 本地 | 开发；`~/code/project/nexus`；测试用 SQLite |
| **ivory** | `ssh ivory`（Tailscale `100.116.123.86`，用户 `admin`） | **生产运行时**：Docker 容器 `nexus` |
| **ali1** | `ssh ali1`（`47.121.181.198`） | **入口 only**：域名/证书/nginx + frps；**不再跑 gunicorn nexus** |

```text
用户 → https://felixfeng.online (ali1 nginx)
         ↓ proxy_pass http://127.0.0.1:18000
       frp remotePort 18000
         ↓
       ivory frpc → 127.0.0.1:18000
         ↓
       Docker nexus 容器 :8000（宿主机映射 18000）
```

- 域名：`felixfeng.online`
- 统一业务端口：**18000**（ivory 宿主机映射、frp remote、ali1 nginx 上游一致）
- frp 客户端：ivory 上 `nexus-frpc.service`（systemd，enabled）
- 旧 ali1 服务：`/etc/systemd/system/nexus.service` 已 **stop + disable**，目录 `/data/app/nexus/` 保留作备份
- nginx 旧配置备份：`ali1:/data/backup/nginx-default.bak`

## 生产路径（ivory，数据盘）

```text
/vol1/apps/nexus/                 ← 项目根（代码 + compose）
├── Dockerfile.ivory              ← 生产镜像（pip + 清华源，不用 ghcr uv）
├── docker-compose.yml            ← ports 18000:8000，挂载 data/
├── data/
│   ├── db.sqlite3                ← 生产数据库（唯一生产数据源）
│   ├── nexus.env                 ← 生产配置（勿命名 .env，避免 compose 解析 $）
│   └── media/                    ← 上传媒体
└── backups/                      ← 本机备份/日志
```

- Docker Root：`/vol1/docker`（fnOS 数据盘，**不要写系统盘**）
- 容器名：`nexus`
- fnOS Docker 应用中心可管理该容器

## 数据隔离（硬规则）

| 位置 | 数据 | 用途 |
|------|------|------|
| Mac `~/code/project/nexus/db.sqlite3` | 本地测试库 | 开发，可随时重置 |
| **ivory** `data/db.sqlite3` | **生产库** | 唯一对外内容源 |
| ali1 `/data/app/nexus/db.sqlite3` | 历史快照 | 只读备份，不回写 |

1. **禁止** rsync/scp 同步 `db.sqlite3`、`nexus.env`、`.env` 在 Mac ↔ ivory 之间做双向/日常同步
2. 部署 **只推代码**
3. 若需用生产数据做本地实验：从 ivory **单向 scp** 拷到 Mac，**永不回传**
4. 生产配置与本地 `.env` 独立；生产 `DJANGO_DEBUG=False`

## 配置管理

- 本地：`.env`（gitignored），参考 `.env.example`
- 生产：ivory `data/nexus.env` → 容器内挂载为 `/app/.env`
- `settings.py` 通过 `python-dotenv` 加载 `BASE_DIR/.env`
- **不要在代码里硬编码密钥、PIN、token**
- 配置键：`DJANGO_SECRET_KEY`、`DJANGO_DEBUG`、`DJANGO_ALLOWED_HOSTS`、`NEXUS_PIN`、`NEXUS_API_KEY`、`RSS_PROXY_URL`
- 生产 compose **不要** 把含 `$` 的 SECRET 放在名为 `.env` 的 compose 同级文件里（会被变量插值）；使用 `data/nexus.env`

## 项目结构（仓库）

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
├── links/                     ← 链接聚合模块
├── research/                  ← 学术研究模块
├── monitor/                   ← 监控探针脚本
├── templates/                 ← 统一模板
├── static/                    ← 静态文件
├── .env / .env.example        ← 本地敏感配置（生产用 data/nexus.env）
├── db.sqlite3                 ← 仅本地测试（不提交、不部署）
├── pyproject.toml / uv.lock
├── Dockerfile                 ← 通用/备用
├── Dockerfile.ivory           ← 生产镜像定义（以 ivory 上为准，改动需同步）
├── docker-compose.yml         ← 仓库内模板；生产 compose 在 ivory
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

## 权限模型

- **浏览**：所有人可访问，无需登录
- **编辑**：6 位 PIN 解锁
- **无用户系统**；PIN 过 cookie + session，有效期 7 天
- API：PIN（浏览器）或 `X-Nexus-Key` header

## 开发约定

- 视图函数为主（不用 class-based views）
- 模板继承 `base.html`，`{% include %}` 复用组件
- Tailwind CDN + 独立 CSS
- HTMX 返回 HTML fragment，`hx-swap="outerHTML"`
- **主工作区直接改**；提交写清「为什么」；AI 可自主 commit 文档与代码（用户已授权全权管理）

### 数据库操作（本地）
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py shell
```

## 本地开发

```bash
cd ~/code/project/nexus
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

## 生产部署（ivory）

```bash
# 1) 只同步代码到 ivory（排除数据与密钥）
rsync -avz \
  --exclude 'data/' --exclude '.env' --exclude 'db.sqlite3' \
  --exclude '.venv/' --exclude '__pycache__/' --exclude '.git/' \
  --exclude 'staticfiles/' \
  ~/code/project/nexus/ ivory:/vol1/apps/nexus/

# 2) 重建并重启容器
ssh ivory 'cd /vol1/apps/nexus && sudo docker compose up -d --build'

# 3) 验收
# 内网: curl http://100.116.123.86:18000/
# 公网: curl https://felixfeng.online/
```

**不要** rsync 覆盖 ivory 上的 `data/db.sqlite3` 与 `data/nexus.env`。

### ali1 入口（一般不动）

- nginx 站点：`/etc/nginx/sites-enabled/default`
- `felixfeng.online` → `proxy_pass http://127.0.0.1:18000`
- frps 配置：`/etc/frp/frps.toml`（`vhostHTTPPort=9000` 等与 nexus tcp 18000 并存）
- ivory frpc 配置：`/var/apps/frpc/shares/frpc/default/frpc.toml` 中 `ivory-nexus`

### 回滚（仅当 ivory 不可用）

```bash
# ali1 nginx 改回本机
# proxy_pass http://127.0.0.1:8000;
ssh ali1 'systemctl start nexus.service'
# 旧代码与旧库仍在 /data/app/nexus/
```

## frp / 常驻服务（ivory）

- `nexus-frpc.service`：systemd 托管 frpc，配置含 `ivory-code-server` + `ivory-nexus`
- 若 fnOS 应用中心再启动一份 frpc 可能抢 `127.0.0.1:7400`，以 **systemd 这份** 为准
- 查看：`ssh ivory 'systemctl status nexus-frpc; sudo docker ps'`

## 快捷键

- `/`：聚焦搜索框
- `E`：打开 PIN 输入
- `Esc`：关闭弹窗

## 当前功能清单

- 首页：Bento Grid（时间、服务器、笔记、服务、动态）
- 笔记：Markdown + 代码高亮 + 标签 + 搜索
- 链接聚合、动态 Now/Activity、学术模块、服务器监控、RSS
- PIN 编辑、星空粒子、移动端导航、快捷键、PWA 相关修复

## AI 工作约定（本项目）

1. 读写代码与文档：**只用** `~/code/project/nexus` 主工作区
2. **不创建** git worktree
3. 改完文档/代码可自行 `git commit`；`git push` 仅在用户明确要求时执行
4. 部署变更优先改文档与脚本；实际生产操作按本节命令执行，且**不覆盖生产数据文件**
5. 会话开始先读本文件，避免沿用已废弃的「ali1 gunicorn 部署」假设
