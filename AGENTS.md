# AGENTS.md — Nexus 项目指南

> 本文件供 AI 阅读。本项目 AI 全权管理；**只用主工作区** `~/code/project/nexus`，不使用 git worktree。  
> 基线需求见 `specs/2026-09-20-nexus-baseline-v1.md`（已批准）。

## 项目简介

Nexus 是**个人聚合门户**：常用链接、个人状态、关于/设置收纳。  
**不是博客站、不是笔记仓库**；笔记写作以本地为准，站上基线不做笔记产品。

## 技术栈

- Django 5 + Python 3.11 + **SQLite**
- HTMX + Tailwind CDN + 项目 CSS token
- 生产：Docker @ ivory（飞牛）` :18000`；ali1 仅 nginx + frps + frp 入口
- 包管理：uv（本地）；生产镜像见 `Dockerfile.ivory`

## 机器访问（怎么连）

均配置为 SSH 免密（密钥见本机 `~/.ssh/config`）；**具体硬件/系统配置不写入本文档，需要时上机自查**。

| 别名 | 角色 | 连接方式 | 备注 |
|------|------|----------|------|
| `ali1` | 公网入口（nginx/frps/证书） | `ssh ali1`（root@47.121.181.198） | 域名 `*.felixfeng.online` 终点 |
| `ivory` | 生产应用（Nexus/Docker） | `ssh ivory`（admin@Tailscale `100.116.123.86`） | Mac 需在 Tailscale 网内 |
| `lunar` | 海外抓取端（RSS 相关） | `ssh lunar`（feng@104.208.64.31，密钥 `~/.ssh/lunar.pem`） | 注意别名是 **lunar** 不是 luna |

lunar 上 RSS 服务：

- 代码仓库：`https://github.com/FeliixFeng/rss-hub`（private，与 nexus 分开）
- 路径 `/home/feng/app/rss-hub`（systemd `rss-hub`，端口 **8080**）
- 接口：`/health`、`/api/v1/{items,sources,status,refresh,sources/reload}`，统一 `{ok, server_time, ...}` 壳
- 认证：请求头 `X-API-Key`，key 在远端 `/home/feng/app/rss-hub/.env`（`RSS_API_KEY`，不入库）
- 信源/接口/存储契约见仓库 `README.md`
- 调试：`ssh lunar` 后 `systemctl status rss-hub`；改 `feeds.toml` 后 `POST /api/v1/sources/reload` 或 restart

补充：

- 上机查看配置用常规命令即可（`uname -a`、`free -h`、`docker ps`、`systemctl`、`nginx -T` 等），**不把机器规格抄进仓库文档**
- 遇到其他机器，同样只记录 SSH 别名/用途，规格上机自查
- frp/nginx 中的 token、密码等**禁止**写入任何仓库文档

## 生产拓扑

```text
用户 → https://felixfeng.online (ali1 nginx)
         ↓ proxy_pass http://127.0.0.1:18000
       frp → ivory Docker nexus 容器 :8000（宿主机 18000）
```

| 主机 | 角色 |
|------|------|
| Mac `~/code/project/nexus` | 开发 + 本地测试 SQLite |
| ivory `/vol1/apps/nexus` | 生产代码 + `data/db.sqlite3` + `data/nexus.env` |
| ali1 | 域名/证书/nginx/frps；**不跑 gunicorn nexus** |

- frpc：ivory `nexus-frpc.service`，代理 `ivory-nexus` 18000→18000
- 旧 ali1 服务已 stop+disable；数据在 `/data/app/nexus/` 备份

## 信息架构（基线）

一级导航仅：**首页 · 链接 · 状态 · 其他**

| 页面 | 路由 | 模板 |
|------|------|------|
| 首页 | `/` | `nexus_core/home.html` |
| 链接 | `/links/` | `links/list.html` |
| 状态 | `/status/` | `nexus_core/status.html` |
| 其他 | `/other/` | `nexus_core/other.html` |

**产品面不暴露：** 笔记/阅读/RSS、监控、科研。相关 app 可休眠。

## 项目结构

```text
nexus/
├── specs/                     # 需求/设计（基线 v1）
├── config/                    # settings / urls
├── nexus_core/                # 壳 + Home + Status + Other
├── links/                     # 入口链接
├── blog/                      # 休眠：可分享详情能力，不进导航
├── research/                  # 休眠
├── monitor/                   # agent 脚本，无产品 UI
├── templates/
│   ├── base.html
│   ├── components/navbar.html
│   ├── nexus_core/            # home, status, other
│   └── links/
├── static/css/base.css        # 设计 token + 全局
└── specs/2026-09-20-nexus-baseline-v1.md
```

## 数据

- 生产 SQLite：`ivory:/vol1/apps/nexus/data/db.sqlite3`
- 本地：`~/code/project/nexus/db.sqlite3`（测试，可弃）
- **禁止** Mac ↔ ivory 同步 `db.sqlite3` / `nexus.env` / `.env`
- 配置：本地 `.env`；生产 `data/nexus.env`（挂载为容器 `/app/.env`）
- 可选后续：ali1 MySQL 新建库；基线不做
- 核心表：`Link`、`NowItem`、`Activity`；表结构可改
- **链接图标**：`Link.icon_file` 存 `static/icons/links/` 下文件名（如 `github.svg`）；优先本地图标，空则用 `icon` 字符 emoji。新增服务：把图标放进该目录并写 `icon_file`，**不要**运行时外网拉取

## 权限

- 浏览免登录；编辑用 6 位 PIN（cookie/session）
- API：PIN 或 `X-Nexus-Key`

## 样式基线

- Token 见 `static/css/base.css` `:root`
- 强调色靛蓝系；卡片/导航/间距统一用 token 与 `.page-shell` 等全局类
- 禁止每页另起一套设计语言
- 个性化：`localStorage` 键 `nexus_quote_off`、`nexus_reduced_motion`

## 开发范式

1. 先读本文件 + `specs/` 中相关基线  
2. 改功能前短 spec（或更新基线 spec）；用户要求验收的批次 **验收前不 commit**  
3. 主工作区直接改；提交信息写清原因  
4. **文档-only** → push 可选，不部署  
5. **运行代码** → 用户验收后 commit+push，再：

```bash
rsync -avz \
  --exclude 'data/' --exclude '.env' --exclude 'db.sqlite3' \
  --exclude '.venv/' --exclude '__pycache__/' --exclude '.git/' \
  --exclude 'staticfiles/' \
  ~/code/project/nexus/ ivory:/vol1/apps/nexus/

ssh ivory 'cd /vol1/apps/nexus && sudo docker compose up -d --build'
```

6. 验收：`https://felixfeng.online/` 与 `/links/` `/status/` `/other/`

## 本地开发

```bash
cd ~/code/project/nexus
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

## 回滚

ali1 nginx 改回 `127.0.0.1:8000` 并 `systemctl start nexus.service`（旧目录仍在）。

## 约定摘要

| 事项 | 规则 |
|------|------|
| 工作区 | 仅主工作区 |
| 导航 | 四项，改 IA 必须改本文件 + spec |
| 数据库 | 基线 SQLite |
| 笔记 | 基线无产品入口 |
| 监控/RSS/科研 | 基线无 UI |
| push | 用户明确要求或验收通过后的代码批次 |
