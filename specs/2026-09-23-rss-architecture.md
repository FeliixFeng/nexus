# Nexus RSS 阅读器 — 架构方向草案

> 日期：2026-09-23
> 状态：**讨论阶段，未实现**
> 关联：`specs/2026-09-20-nexus-baseline-v1.md`

## 一、定位

Nexus 新增独立 Tab：`/rss/`，作为信息聚合入口。

- **不是**博客、不是笔记仓库（笔记继续用 Obsidian）
- **是**信息聚合 + 智能过滤 + 每日要闻
- 提高使用率：用户每天打开 Nexus 的理由从"看链接"变成"看今日要闻"

## 二、整体架构

```
Luna (海外)                    Ivory (国内)
┌─────────────┐               ┌──────────────┐
│ FastAPI     │  ←── API ──  │ Django       │
│ SQLite      │  (API Key)    │ SQLite       │
│ 抓 RSS      │               │ AI 处理      │
│ 定时抓取    │               │ 定时拉取     │
└─────────────┘               └──────────────┘
```

**职责分离**：
- **Luna 端**：抓取所有信源（国内 + 海外），存原始数据，暴露 API
- **Ivory 端**：从 Luna 拉取数据，做 AI 处理（摘要/分类/打分），存处理后数据，展示 UI

**为什么两边分离**：
- 海外信源（Hacker News、YouTube）需要 Luna 抓取
- AI 处理在国内便宜（阿里云百炼）
- 隔离故障：Luna 挂了 Nexus 还能展示缓存；Ivory 挂了数据堆积在 Luna 不丢
- 可迁移：信源调整只改 Luna，Ivory 不动

## 三、Luna 端设计

### 技术栈
- FastAPI（自带异步、类型校验、OpenAPI 文档）
- SQLite（缓存抓取结果，30 天保留）
- feedparser（RSS 解析）
- httpx（异步 HTTP）

### 核心数据表

```sql
feed_item (
  id TEXT PRIMARY KEY,           -- hash(url) 去重
  source TEXT,                   -- 机器之心 / HN / ...
  source_type TEXT,              -- rss / api / youtube
  title TEXT,
  url TEXT,
  content TEXT,                  -- 原文
  published_at TIMESTAMP,
  fetched_at TIMESTAMP,
  processed_by_ivory BOOLEAN,    -- 是否已被 Ivory 拉走
  created_at TIMESTAMP
)
```

### API 接口
- `GET /api/feeds?limit=50&unprocessed=1` — 拉最新未处理条目
- `GET /api/feeds?source=xxx` — 按源拉
- `POST /api/refresh` — 手动触发抓取
- `GET /api/status` — 健康检查

所有接口需 `api_key` 认证。

## 四、Ivory 端设计

### 新增 Django 模型

```python
class FeedItem(models.Model):
    source, title, url, content
    summary       # AI 生成摘要
    category      # AI 分类
    score         # AI 打分 (1-10)
    published_at, fetched_at, processed_at
    is_read
```

### 处理流程
1. 定时拉 Luna 的 `/api/feeds`（未处理条目）
2. 存 SQLite（按 url 去重）
3. 调用 AI：生成摘要 → 分类 → 打分
4. 回调 Luna 标记 processed
5. 展示到 UI

## 五、频率策略

| 任务 | 频率 | 说明 |
|:-----|:-----|:-----|
| Luna 抓取 | 凌晨 5 点 + 下午 18 点 | 早晚各一次 |
| Ivory 拉取 | 早上 6 点 + 晚上 20 点 | 拉完就 AI 处理 |
| 手动刷新 | 用户触发 | 立刻拉一次 |

**为什么不用 Webhook**：
- 实现复杂（回调、重试、认证）
- 公网端口暴露有安全风险
- RSS 是消费场景，早晚各一次够用，不用实时

**保留手动刷新**：用户想主动拉时可以触发，实现成本低、体验好。

## 六、信息源规划（分阶段）

### 第一阶段（基础）
- 机器之心、量子位 — AI 新闻
- GitHub Trending — 开源
- 安全内参 — 安全事件
- 阮一峰周刊 — 综合技术

### 第二阶段（后续加）
- Hacker News — 英文新闻（Luna 抓）
- YouTube 频道（通过 RSSIFY 转 RSS）
- arXiv cs.AI — 论文（研究生相关）
- V2EX 热门 — 社区

### 第三阶段（远期）
- 学术期刊（计算机学报、软件学报等）
- Twitter/X（反爬成本高，暂缓）
- 个人博客收藏

## 七、AI 处理

### 三个任务
1. **摘要**：每条新闻 50 字摘要
2. **分类**：AI/安全/开源/工具/论文
3. **打分**：1-10 分，低于阈值（比如 <6）过滤掉

### 模型选择（待定）
- 候选：智谱 GLM 4.7 Flash（免费额度有限）
- 兜底：阿里云百炼 glm-5.2（付费但便宜，稳定）

### 内容展示三层结构
```
┌─────────────────────────────────────┐
│ [摘要] 50 字快速了解                 │
├─────────────────────────────────────┤
│ [关键段落] 100-200 字看到具体内容     │
├─────────────────────────────────────┤
│ [原文链接] → 查看完整报道             │
└─────────────────────────────────────┘
```

## 八、过滤标准

"有营养"的定义：
- **必须关注**：研究方向相关（大模型、NLP、计算机教育）
- **应该关注**：行业趋势、安全事件、工具/开源
- **可以关注**：新论文、GitHub Trending
- **不要**：八卦、营销软文、同质化新闻、娱乐

打分规则：AI 类 >= 7 分保留，安全类 >= 6 分，其他 >= 8 分。

## 九、暂不做

- 博客/笔记恢复（Obsidian 已够用）
- Webhook 推送（轮询够用）
- 期刊订阅（后续阶段）
- Twitter 抓取（反爬成本高）
- 复杂 embedding 去重（后续优化）

## 十、后续待定

- Luna 服务部署方式（Docker vs 直接 systemd）
- 数据库迁移策略（从 SQLite 升级？）
- 用户偏好学习（手动打标 → AI 学习）
- 同事件多源合并（embedding 相似度）
- 推送策略（微信/邮件每日摘要）

---

**下一步**：定信源清单 + AI 处理流程细节 + 数据库 schema
