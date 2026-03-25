### 场景5: 小站 → KMB 数据迁移（核心功能）

> ⚠️ **这是本 Skill 的核心场景，涉及数据架构重构**

小站（Space）到 KMB 的迁移**不是简单复制 SQL**，而是需要：
- **语义理解**: 分析原 SQL 的业务逻辑
- **架构重构**: 设计 Model 分层（Table / SQL / Model）
- **指标抽象**: 识别可复用的 Metrics
- **可视化重建**: 在 KMB 中还原 Dashboard

**详细迁移指南**: `references/migration-guide.md`

**标准迁移流程**:

```bash
# 阶段 1: 分析原小站 SQL 结构
python3 scripts/space_sql_mapper.py graph <graphId>
# → 输出：SQL、配置、依赖关系

# 阶段 2: 设计 KMB 数据架构
# → 判断：是否需要新建 Model？
# → 判断：哪些字段需要预处理？
# → 判断：如何划分 Metric？

# 阶段 3: 创建 Model（基础层）
curl -X POST "${HOST}/api/card" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "type": "model",
    "name": "Model: XXX基础数据",
    "dataset_query": {
      "type": "native",
      "native": {"query": "SELECT ... FROM table WHERE ds = ..."}
    }
  }'

# 阶段 4: 创建 Question（指标层）
# → 基于 Model 创建聚合查询
# → 配置可视化参数

# 阶段 5: 组装 Dashboard（应用层）
# → 创建 Dashboard
# → 批量添加 Questions 到 Dashboard
# → 配置布局（size_x, size_y, row, col）
```

**关键决策点**:
1. 这个查询应该直接建 Question，还是新建 Model？
   - 简单查询 → 直接 Question
   - 多表关联/复杂逻辑 → 先建 Model

2. 如何设计 Model 分层？
   - 基础层：原始数据清洗
   - 指标层：聚合计算
   - 应用层：Dashboard 展示

3. SQL 中的聚合如何准确转换？
   - 分区字段（ds）→ 原生 SQL 处理
   - 条件聚合 → MBQL `case` 表达式
   - 时间维度 → Model 层预处理 week/month 字段
