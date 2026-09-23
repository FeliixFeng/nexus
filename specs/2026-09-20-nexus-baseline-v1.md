# [S1] Nexus 基线 v1 — 个人聚合门户

日期：2026-09-20  
状态：用户已批准，进入实现；验收前不 git 提交。

## [S2] 定位

个人聚合门户（Personal Hub）：自用入口 + 状态展示 + 偶尔对外展示。  
不是博客站，不是笔记仓库。笔记写作以本地为准。

## [S3] 基线范围

### 导航（原 4 项；2026-09-23 修订见下）

首页 · 链接 · 状态 · 其他

> **修订（2026-09-23，已实现）**：一级导航改为五项 **首页 · 资讯 · 链接 · 状态 · 其他**；新增 `/rss/` 资讯（原「不做 RSS 入口」废止）。权威表述见 `AGENTS.md` + `specs/2026-09-23-rss-architecture.md`。

### 模块

| 模块 | 路由 | 职责 |
|------|------|------|
| Home | `/` | 身份、常用链接摘要、状态摘要 |
| Links | `/links/` | 服务 / 项目 / 外链 |
| Status | `/status/`（兼容 `/now/`） | Now + 里程碑 |
| Other | `/other/` | 关于、使用说明、个性化、基础设施、扩展位 |

### 产品面一刀切（不做）

- 笔记列表 / 阅读站 / RSS 入口
- 服务器监控 UI
- 科研模块入口
- 小工具箱（仅「其他」扩展位文案）

`blog`、`research`、`monitor` 代码可留仓库，**不进主导航与首页**。

## [S4] 数据

- 生产：ivory SQLite `data/db.sqlite3`；本地测试库独立。
- 可选后续：ali1 MySQL；**基线不实现**。
- 表结构可改；旧数据不挡设计。核心模型：`Link`、`NowItem`、`Activity`。
- 关于/说明/扩展位：模板静态；个性化：localStorage。
- 链接图标：`Link.icon_file` → `static/icons/links/` 本地文件；无文件时 `icon` emoji 回退。不运行时拉 favicon。

## [S5] 样式基线

- 深色画布 + 靛蓝强调 `#6366f1`
- 统一 token（`static/css/base.css` `:root`）
- 统一页面壳、卡片、导航高亮、空状态
- 动效可「弱化」（localStorage `nexus_reduced_motion=1`）
- 首页语录可关（localStorage `nexus_quote_off=1`）

## [S6] 页面需求

### Home

- Hero：名字 + 一句定位
- 可选语录（可被个性化关闭）
- 卡片：常用链接、进行中状态、里程碑摘要
- 无监控、无笔记墙

### Links

- 按服务 / 项目 / 外链分组卡片
- PIN 编辑能力保留（既有）

### Status

- 进行中（NowItem）
- 里程碑（Activity）
- 标题用「状态」

### Other

- 关于
- 使用说明（PIN）
- 个性化：语录开关、弱化动效
- 基础设施（静态）
- 扩展位：应用聚合 · 小工具（未启用）

## [S7] 开发与部署范式

- 主工作区 `~/code/project/nexus`，不用 worktree
- 权威文档：`AGENTS.md` + 本 spec
- 文档-only：可 push，不部署
- 运行代码：验收通过后再 commit/push，并 rsync + `docker compose up -d --build` 至 ivory
- **禁止** rsync 覆盖 `data/db.sqlite3`、`data/nexus.env`

## [S8] 验收

1. 导航五项（首页·资讯·链接·状态·其他），桌机/手机一致（2026-09-23 修订）  
2. 一级页无空壳监控/科研/笔记站（RSS 已由资讯 Tab 取代）  
3. 首页可见身份、链接、状态  
4. 强调色与卡片样式统一  
5. 「其他」四类内容齐全  
6. 本地 `manage.py check` + 页面 200  
7. ivory 部署后公网可打开（用户验收用；代码未要求先 commit）

## [S9] 实现顺序

1. spec + AGENTS  
2. token/导航/页面壳  
3. Home / Links / Status / Other  
4. 移除监控与 RSS 等入口  
5. 本地验证 → ivory 部署（不 commit）→ 用户验收  
