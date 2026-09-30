# 内容精简 v2 — 入口控量 + 日报唯一产物

> 日期：2026-09-29
> 状态：**✅ 已上线（2026-09-30）**：本地+ivory 验证通过、06:00 cron 已挂并验证；待办仅剩 lunar 24h 流量终验（2026-09-30T12:32Z 后数 `since=2026-09-29T12:32:00Z`）
> 关联：`specs/2026-09-23-rss-architecture.md`

## 实现后记（2026-09-30 上线时写）

- 降级链最终形态（三层）：智谱 1301 内容过滤常被正文 excerpt 触发 → **先带 excerpt，被拦自动去 excerpt 重试一次** → 仍失败才走纯标题 fallback
- 输出格式：**Markdown 直出**（JSON 被证伪：长 body 缺分隔符必炸），解析 `# title` / `> lead` / `## 分组`
- 覆盖率双保险：模型只写 14/31 实测存在 → `_linkify_titles()`（bold 标题反查回填链接，含截断标题前缀匹配）+ `_complete_coverage()`（漏写条目按领域回填，保证 100%）
- 端到端验证：本地 31/31、ivory 26/26、全路由 200、`item_ids` 与真实链接一致
- 早期流量信号（基线后 15.5h）：HN 7 条 → 外推 ≈10.8/天，命中预估 10-12（过滤前 38/天）

## 进度（2026-09-29 收工快照）

**已完成**
- lunar：HN 源 `?points=200` 已上线观测（备份 `feeds.toml.bak-points`；基线 2026-09-29T12:32Z，24h 后用 `since=2026-09-29T12:32:00Z` 验收）
- 代码全部改完：`llm.py`（删打分链 → `generate_daily_brief()` + 降级）、`data.py`（每源限额 3/3/2 + `purge_old_items(7d)` + `items_for_brief(24h/40条)`）、`pull_and_process`（拉取→限额→日报→清理）、`urls/views/模板`（首页=日报时间流，删待读/全部路由和模板）
- `manage.py check` 通过、无需迁移；端到端跑通（限额生效：InfoQ -25/量子位 -16/少数派 -9）

**卡点（明日第一件事）**
- `--force-brief` 走降级：LLM 返回合法收尾的 JSON 但 body 行缺分隔符 → `JSONDecodeError`（实测 raw 1169 chars，非截断；输入 24k chars/40 条，调用 40s）
- **已定修法**：放弃 JSON 输出，改让模型直接产 Markdown 日报（`# ` 标题 + 引用 lead + 分组正文），只做行解析；改 `generate_daily_brief()` 约 30 行，改完跑一次验证（40s/次，勿循环重试）
- 顺带确认：prompt 已改"必须覆盖全部条目"（上一版只选 7/40 条），新解析路径下需验证覆盖率

**待办**
1. 修 Markdown 解析 → 本地验证一次（含降级路径 + lsp_diagnostics）
2. 部署 ivory（rsync 排除 `data/`）+ 线上手跑验证
3. root crontab 挂 06:00 `sudo docker exec` pull（日志 `data/pull.log`，注意上次 docker socket 权限报错）
4. lunar 24h 流量验收
- backlog：GitHub 热榜独立日报（`feeds.toml` 现成 disabled 源，建议 weekly/all，用户指示"记着先不做"）

## 一、背景与问题

09-23 上线后暴露"内容太多"：

- hub 每天流入 **~80 条**（HN 占 ~70%，55/天；InfoQ 8.8、量子位 6.8、少数派 3.2）
- ivory 逐条 LLM 打分（80 条 ≈ 10 次串行调用，慢）；THRESHOLDS 打分 86% 过线，形同虚设
- `featured_items()` 无上限、`pending_items()` 写死 80、**永不清库**
- 精选/待读/全部三列表翻起来累，日报反而是附属品

## 二、定稿方案

**核心倒置：日报是唯一产物，筛选在入口完成，LLM 只做总结。**

```
lunar feeds.toml:  hnrss.org/frontpage?points=200     ← 入口砍 HN（已完成，观测中）
                   + 中文源不限（ivory 侧限额）
        ↓ hub 每小时轮询攒着（不动）
ivory 每天 06:00 拉一次:
  1. pull 入库
  2. 每源每日限额: InfoQ≤3 量子位≤3 少数派≤2（其余不限）→ 总量 ~20/天
  3. 全部新条目一次喂 LLM → 主日报（总起 + 分组 + 逐条一句话 + 原链）
  4. FeedItem 只留 7 天，purge
        ↓
首页 = 日报时间流。精选/待读/全部三列表、逐条打分、featured 全部移除。
```

### 决策记录

| 决定 | 选择 | 理由 |
|------|------|------|
| HN 热度过滤 | `?points=200`（lunar 配置） | 回溯 8 天 304 条实测：38/天 → 13/天（上界）；≥200 = 前 1/3 位置 |
| 中文源控量 | ivory 拉取后每源限额 | 中文 RSS 无热度参数；限额是硬保证 |
| LLM 职责 | 每天 1 次总结，不逐条打分 | 打分 86% 过线无区分度；一次调用替代 ~10 次，根除"慢" |
| 列表页 | 三列表移除，首页只剩日报流 | 用户拍板"每天一个日报就够"；hub 是全量存档，ivory 不需要替它存档 |
| 拉取频率 | 每天 06:00 一次 | 日报是天粒度；一次拉齐 24h，边界清晰 |
| 保留 | 原始 FeedItem 7 天 | 留调试兜底；日报永久堆叠不清理 |
| 失败降级 | LLM 失败 → 纯标题列表日报 | 时间流不断档 |

### 预期效果

```
入口: 80/天 → ~20/天（HN 10-12 + 中文限额 ~10）
LLM:  每天 2 次调用（本期只做主日报 1 次）
库:   FeedItem ≤7 天滚动；DailyBrief 永久
页面: 日报时间流，读完即走
```

## 三、lunar 侧变更（已完成，观测中）

- `feeds.toml` HN url → `https://hnrss.org/frontpage?points=200`（备份 `feeds.toml.bak-points`）
- `POST /api/v1/sources/reload` 生效，`POST /api/v1/refresh` 验证通过
- 基线：reload 时刻 2026-09-29T12:32Z；当天 00:00→12:32 拉入 42 条（HN16/InfoQ17/量子位5/少数派4）
- **待办**：挂 24h 后用 `since=2026-09-29T12:32:00Z` 数真实单日入口流量验收
- 边界：只改配置 + reload，未动 rss-hub 代码（Phase 1 冻结不违反）

## 四、Backlog（本期不做）

- **GitHub 热榜独立日报**：源已备好（`feeds.toml` 现有 `GitHub Trending`，disabled）。
  实测 `weekly/all` 18 条/周（~2.6/天）vs `daily/all` 8-25/天；
  建议 weekly + 有新增才生成，与主日报解耦独立预算。用户指示：记着，先不做。

## 五、实现范围（本期）

- `rss/data.py`：pull 后每源限额；新增 `purge_old_items(days=7)`
- `rss/llm.py`：新增 `generate_daily_brief()`（一次调用出全文日报，失败降级）；
  移除 `score_items` / `process_unprocessed` / `THRESHOLDS` 打分链与 `ensure_daily_brief` 旧逻辑
- `rss/management/commands/pull_and_process.py`：拉取 → 限额 → 日报 → 清理 单流程
- `rss/views.py` + 模板：首页改日报时间流；移除 精选/待读/全部 路由
- 模型：`DailyBrief` 已有 `body`/`lead`/`item_ids`，无需迁移（`FeedItem.score/featured` 字段保留不删列，仅不再写入）
- cron：ivory root crontab 单条 06:00 `sudo docker exec … pull_and_process --llm`
