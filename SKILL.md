---
name: kmb-metabase
description: |
  KMB (Metabase) 数据平台操作指南与自动化工具集。用于：
  (1) 查询和分析 Metabase Card/Dashboard 数据
  (2) 自动化日报/周报生成与播报
  (3) 数据探索与指标监控
  (4) API 调用与数据处理
  (5) 创建和管理 Metabase 资源
  适用于需要对 KMB 系统进行数据查询、报告生成或自动化操作的任务。
---

# KMB (Metabase) 数据平台 Skill

企业内部 Metabase 数据平台（KMB）的数据迁移与重构工具集。

> **定位**: 面向开发/数据工程师，专注于**小站数据迁移**和**Metabase 资源重构**（Model/Question/Dashboard）。
>
> **Iron Law（铁律）**: 默认优先直接调用 Metabase API（curl）；允许复用仓库内 `scripts/` 与 `scripts/core/`；禁止新建重型 SDK/客户端框架。

## 与其他 Metabase Skill 的区别

| 维度 | 本 Skill | 通用 Metabase Skill |
|------|---------|-------------------|
| **目标用户** | 开发/数据工程师 | 业务分析人员 |
| **核心任务** | 数据迁移、资源重构、自动化 | 即席查询、数据探查 |
| **工作方式** | 脚本化、批量化、自动化 | 交互式、单点查询 |
| **SQL 策略** | 重构 SQL，创建可复用 Model | 直接查询，关注结果 |
| **输出成果** | Dashboard、Model、Question、迁移记录卡 | 查询结果、数据报告 |

## 快速访问

| 资源 | 链接/位置 |
|------|----------|
| KMB 平台 | `https://kmb.qunhequnhe.com` |
| API 文档 | `references/api-reference.md` |
| **MBQL 最佳实践** | `references/mbql-best-practices.md` |
| Dashboard 配置 | `references/dashboard-configs.md` |
| **迁移指南 (完整版)** | `references/migration-guide.md` |
| **小站数据** | `space-data/` 目录 |
| 常用脚本 | `scripts/` 目录 |

## 规范优先级（SSOT）

当多个文档描述存在差异时，按以下顺序判定：

1. `rules/*`（强约束，必须遵守）
2. `references/*`（实现参考与实践经验）
3. `SKILL.md` 示例片段（快速上手示例）

其中 API 细节以 `rules/api-standards.md` 为准，MBQL 设计细节以 `references/mbql-best-practices.md` 为准。

## 核心配置

### API 认证
默认配置位于 `scripts/core/config.py`：

```bash
API_HOST="https://kmb.qunhequnhe.com"
API_KEY="mb_xxx..."
```

### 常用 Dashboard
| Dashboard | ID | 用途 |
|-----------|-----|------|
| 投放词数据总览 | 139 | GA投放词分析 |
| COOHOM折扣体系 | 254 | 折扣转化分析 |
| Revenue用户分层（新）迁移 | 494 | 收入账单分层分析 |

---

## 使用场景

### 场景1: 查询 Card 数据

```bash
# 使用内置脚本查询 Card 数据
python3 ~/.claude/skills/kmb-metabase/scripts/query_card.py 3267

# 或使用 curl
curl -sL \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -X POST "https://kmb.qunhequnhe.com/api/card/3267/query" \
  -d '{"parameters":[],"constraints":{"max-results":100}}'
```

### 场景2: Dashboard 操作 ⭐

#### 创建 Dashboard
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/dashboard" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Dashboard",
    "description": "Dashboard description",
    "collection_id": 5,
    "parameters": []
  }'
```

#### 通过 PUT 更新 Dashboard（添加卡片）
```bash
curl -X PUT "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {
        "id": -1,
        "card_id": 45,
        "row": 0,
        "col": 0,
        "size_x": 6,
        "size_y": 4,
        "parameter_mappings": [],
        "visualization_settings": {}
      }
    ]
  }'
```

#### 批量更新 Dashboard 卡片（推荐）
```bash
curl -X PUT "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "dashcards": [
      {
        "id": -1,
        "card_id": 45,
        "row": 0,
        "col": 0,
        "size_x": 6,
        "size_y": 4
      },
      {
        "id": -2,
        "card_id": 46,
        "row": 0,
        "col": 6,
        "size_x": 12,
        "size_y": 6
      }
    ]
  }'
```

#### 从 Dashboard 删除卡片
```bash
curl -X DELETE "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/cards/${dashcard_id}" \
  -H "X-API-Key: mb_xxx..."
```

#### 复制 Dashboard
```bash
curl -X POST "https://kmb.qunhequnhe.com/api/dashboard/${dashboard_id}/copy" \
  -H "X-API-Key: mb_xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Copy of Dashboard",
    "description": "Copied dashboard",
    "collection_id": 5
  }'
```

### 场景3: 小站数据查询（离线分析）

使用 `space_sql_mapper.py` 分析小站导出的数据（目录树 → 页面 → SQL）：

```bash
cd ~/.claude/skills/kmb-metabase/scripts

# 1. 按关键词搜索页面
python3 space_sql_mapper.py search "Weekly Data"
# → pageId=34433

# 2. 查看页面详情（含图表列表）
python3 space_sql_mapper.py page 34433
# → 包含10个图表，如 graphId=41236

# 3. 查看图表 SQL 详情
python3 space_sql_mapper.py graph 41236

# 4. 只提取 SQL（可用于迁移到 KMB）
python3 space_sql_mapper.py sql 41236

# 5. 显示完整目录树
python3 space_sql_mapper.py tree
```

**数据规模**: 412个页面，1,738个图表/SQL查询

### 场景4: 生成日报/周报

```bash
# 执行 Dashboard 139 日报并写入报告文件
python3 ~/.claude/skills/kmb-metabase/scripts/generate_dashboard139_report.py \
  --output ~/.claude/skills/kmb-metabase/reports/dashboard139_$(date +%Y%m%d).md

# 查看生成的报告
cat ~/.claude/skills/kmb-metabase/reports/dashboard139_$(date +%Y%m%d).md
```

### 场景5: 小站 → KMB 数据迁移

> ⚠️ **这是一个复杂任务，需要 LLM 自主思考分阶段执行**

小站（Space）到 KMB 的迁移**不是简单脚本可以完成**的，涉及：
- SQL 语义理解 → MBQL 转换
- Model 分层设计（Table / SQL / Model）
- Metrics 业务抽象
- 可视化重建

**详细迁移指南**: `references/migration-guide.md`

**固定迁移 SOP（快速执行卡）**:

1. **边界确认**
   - 锁定 source pageId/source dashboard/target collection
   - 明确“所有新资产必须落在目标 collection”

2. **源结构抽取**
   - 用 `space_sql_mapper.py` + `space-data/page_map.json` 抽取 SQL 与前端配置（graphType、legend、轴）

3. **依赖先迁**
   - 先迁 Model/Helper，再迁主 Question
   - 创建后立即重写 `card__<src_id>` 引用

4. **主卡迁移与可视化回填**
   - dataset_query 与 visualization_settings 分别对齐源端逻辑

5. **Dashboard 全量回填**
   - 仅使用 `PUT /api/dashboard/:id`
   - 新 dashcard 使用负数 ID

6. **SOP 硬闸门（任一失败禁止交付）**
   - 引用残留为 0
   - `/api/card/:id/query` 全量通过
   - 关键卡抽样一致（列/前 N 行/行数）
   - dashboard 参数与卡片数量对齐

7. **清理与交付**
   - 归档中间态资产
   - 输出映射表 + 校验表 + markdown 迁移记录卡
   - **迁移记录卡要求**：在目标 collection 新建独立 Dashboard（命名 `【P<pageId>】迁移记录卡`），并用 text dashcard 写入 markdown 记录内容（至少包含：资产映射、硬闸门结果、回滚信息）

**详细说明**:
- 完整流程：`references/migration-guide.md`
- 交付闸门：`rules/api-standards.md`（迁移校验最小清单）
- 阻断信号：`rules/red-flags.md`

**关键决策点**（LLM 需自主判断）:
1. 这个查询应该直接建 Question，还是新建 Model？
2. 哪些计算应该抽象为 Metrics？
3. SQL 中的聚合如何准确转换为 MBQL？

---

### 场景6: 探索数据

```bash
# 搜索相关内容
curl -sL \
  -H "x-api-key: ${API_KEY}" \
  "${API_HOST}/api/search?q=转化" | jq '.data'
```

---

## MBQL 最佳实践

创建或编辑 Question 时，参考以下最佳实践：

### 🎯 核心原则：Model 层预处理，Question 层消费

> **铁律：能用 SQL 在 Model 层解决的，不要在 Question 层用 MBQL 折腾！**

| 操作 | 正确做法（Model SQL） | 错误做法（Question MBQL） |
|------|---------------------|------------------------|
| **CASE WHEN 分类** | SQL 中预计算 `频道`、`频道排序` | 在 MBQL 用复杂的 `case` 表达式 |
| **日期转换** | `STR_TO_DATE(ds, '%Y%m%d') AS 所在日` | 在 MBQL 中动态转换 |
| **中文别名** | SQL 中直接用中文别名 | 在 MBQL 中维护字段映射 |
| **Group By** | SQL 中 `GROUP BY day, uri` | `breakout` 字段和 SQL 不一致 |
| **排序** | 预计算数字排序字段（1-8） | 在 MBQL 中写复杂排序逻辑 |

### 条件聚合 - 使用 `case` 而非 `if`
```json
// ✅ 正确
["sum", ["case", [[["=", ["field", 123], "A"], ["field", 456]]]]]

// ❌ 错误 - MBQL 不支持 if
["sum", ["expression", "if(category = 'A', amount, 0)"]]
```

### 转化率计算 - 在 aggregation 中直接除法
```json
// ✅ 正确 - 在 aggregation 层计算
{
  "aggregation": [
    ["/", ["sum", ["field", 100]], ["sum", ["field", 101]]]
  ]
}

// ❌ 错误 - 避免在 expression 中定义
{
  "expressions": {
    "conversion_rate": ["/", ["field", 100], ["field", 101]]
  }
}
```

### 时间字段 - Model 层预处理
- 在 Model 中定义 `week_start`, `month_start` 等字段
- Question 中直接使用预处理字段，避免重复转换

### 可视化设计 - 参考 Dashboard 700
- **精简指标**: 只展示 3-5 个核心指标
- **双 Y 轴**: 金额类左轴，比率类右轴
- **面积图**: 用于展示累积趋势或占比变化

完整最佳实践文档: `references/mbql-best-practices.md`

---

## API 调用规范

为避免文档漂移，API/约束/错误处理细节统一维护在规则与参考文档中：

- API 调用标准：`rules/api-standards.md`
- 工具约束（Iron Law）：`rules/constraints.md`
- 错误处理与诊断：`rules/error-handling.md`
- 危险信号与止损：`rules/red-flags.md`
- MBQL 设计实践：`references/mbql-best-practices.md`
- 完整 API 端点：`references/api-reference.md`

执行建议：
1. 先按 `rules/api-standards.md` 确认端点、方法与请求体。
2. 查询设计遵循“默认必须 Model + MBQL；`UNION ALL` 拆分为多个 Question、动态时间使用增量数据 + Dashboard 筛选、缺字段先在 Model 预加工；仅在完全无法解决且明确记录原因时才允许原生 SQL 例外”。
3. 创建/更新后立即验证可运行性（如 `/api/card/:id/query`）。

---

## 脚本工具

### query_card.py
查询指定 Card 的数据。
```bash
python3 scripts/query_card.py <card_id> [--limit 100] [--output json|csv|table]
```

### space_sql_mapper.py
**小站数据查询工具** - 分析离线导出的小站数据，建立目录树 → 页面 → SQL 的映射。

```bash
# 搜索页面
python3 scripts/space_sql_mapper.py search <关键词>

# 查看页面详情
python3 scripts/space_sql_mapper.py page <pageId>

# 查看图表/SQL详情
python3 scripts/space_sql_mapper.py graph <graphId>

# 只输出SQL（可用于迁移）
python3 scripts/space_sql_mapper.py sql <graphId>

# 显示完整目录树
python3 scripts/space_sql_mapper.py tree
```

**数据文件位置**: `space-data/` 目录

### 其他脚本
- `search_kmb.py` - 搜索 KMB 内容
- `get_collection_cards.py` - 获取 Collection 下所有 Cards

### 运行测试
```bash
cd ~/.claude/skills/kmb-metabase
python3 -m unittest discover -s tests -p 'test_*.py'
```

---

## 扩展指南

### 添加新的 Dashboard 支持

1. 在 `references/dashboard-configs.md` 中添加 Dashboard 配置
2. 创建对应的报告生成脚本 `scripts/generate_<name>_report.py`（复用 `scripts/core/*`）
3. 更新本 SKILL.md 的快速访问表格

### 添加新的 Card 查询

1. 确定 Card ID 和所需参数
2. 使用 `query_card.py` 测试查询
3. 如需定制化输出，创建新的脚本

---

## 故障排查

### 401 Unauthorized
- 检查 API Key 是否有效
- 确认请求头格式正确

### 403 Forbidden
- 确认有权限访问该资源
- 联系管理员确认权限配置

### 数据为空
- 检查 Card ID 是否正确
- 确认日期参数范围
- 检查 Dashboard 过滤器设置

---

## 错误处理与诊断

### HTTP 401 - 认证失败
```
API key 无效或已过期
诊断步骤：
→ 检查 API key 是否正确拷贝（注意空格）
→ 在 Metabase 设置中验证 API key 状态
→ 尝试重新生成 API key
```

### HTTP 403 - 权限不足
```
当前 API key 没有执行此操作的权限
诊断步骤：
→ 检查 Metabase 中该 API key 的权限设置
→ 确认操作是否需要管理员权限
→ 考虑使用具有更高权限的 API key
```

### HTTP 404 - 资源不存在
```
资源不存在（Dashboard ID: 123）
诊断步骤：
→ 验证 ID 是否正确
→ 该资源可能已被删除
→ 运行列表命令查看现有资源
```

### HTTP 500 - 服务器错误
```
Metabase 服务器错误
诊断步骤：
→ 检查 Metabase 服务器日志
→ 稍后重试
→ 如果持续失败，联系 Metabase 管理员
```

### 连接失败
```
无法连接到 Metabase
诊断步骤：
→ 检查 URL 是否正确（https://kmb.qunhequnhe.com，无尾部斜杠）
→ 确认 Metabase 服务正在运行
→ 测试网络连接: curl -I ${HOST}
```

---

## 反模式（常见错误）

| ❌ 错误 | 为什么错 | ✅ 正确做法 |
|--------|---------|-----------|
| 使用 Query Builder (type: "query") 处理复杂 SQL | 在 JOIN/CTE/窗口函数等场景若直接硬写易失控 | 先在 Model 预加工并将 `UNION ALL` 拆分成多个 MBQL Question；仅在完全无法解决且有记录时用原生 SQL 例外 |
| 引用错误: `metabase.question_XXX` | 数据库名错误，导致查询失败 | 使用实际表名（原生 SQL）或 `card__ID` |
| POST 到 `/api/dashboard/:id/cards` | 此端点不存在，API 会返回 404 | 使用 PUT `/api/dashboard/:id` 更新 dashcards 数组 |
| 添加卡片时使用正数或省略 ID | 验证错误，Metabase 无法识别新卡片 | 新卡片必须使用负数 ID (-1, -2, -3...) |
| 创建 Python/Node SDK | 违反工具约束（Iron Law）并增加维护负担 | 优先 curl，或复用 `scripts/core` 能力 |
| 不验证配置 | 无效配置会导致后续所有操作失败 | 必须调用 `/api/user/current` 验证 |
| 不验证查询是否能运行 | 创建后才发现错误 | 创建后立即用 `/api/card/:id/query` 测试 |
| 显示完整 JSON | 信息过载 | 简洁摘要关键字段 |
| 使用 Session token | API key 更安全、无需登录 | 使用 X-API-Key header |
| 一次问所有问题 | 不友好 | 逐步交互式对话 |
| 只说"权限错误" | 不够 helpful | 提供 2-3 个诊断步骤 |

---

## 参考资料

- `references/api-reference.md` - 完整 API 文档
- `references/mbql-best-practices.md` - **MBQL 编写最佳实践**
- `references/dashboard-configs.md` - Dashboard 配置详情
- `references/card-catalog.md` - 常用 Card 目录
- `references/migration-guide.md` - **小站 → KMB 迁移指南**
- `rules/constraints.md` - **工具约束（Iron Law）**
- `rules/api-standards.md` - **API 调用标准**
- `rules/error-handling.md` - **错误处理与诊断**
- `rules/red-flags.md` - **危险信号（Red Flags）**
- `space-data/` - **小站离线数据**（目录树映射、SQL查询）
- `scripts/` - 可执行脚本集合
