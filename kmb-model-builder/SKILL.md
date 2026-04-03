---
name: kmb-model-builder
description: |
  Metabase Model 创建原子 skill。基于 SQL 或 `migration_plan.json` 创建 Model，
  并返回 `model_id`。
origin: KMB-Skill
dependencies:
  - scripts/lib/kmb
---

# Model 构建 Skill

## When to Use

- 已有 Model SQL，需要落地到 Metabase。
- 迁移流程已完成 SQL 分析，准备创建 Model。

## Required Inputs

- `collection_id`
- 以下三者满足其一即可: `sql_file`, `sql`, `config_file`
- 可选: `name`, `database`

## If Inputs Missing

- `collection_id` 缺失时必须询问。
- SQL 与配置文件都缺失时，回退到 `kmb-sql-analyzer`。
- `name` 未给时，可从配置或 SQL 主题推导 `Model: <业务名>`。
- `database` 未给时使用默认数据库配置。

## Execution Steps

1. 校验输入来自已分析的 Model SQL 或 `migration_plan.json`。
2. 检查 Model SQL 是否符合要求：无多余 `GROUP BY`、I/S 表处理正确、日期与 CASE 字段已预处理。
   - 命中 `_s_d` 表时，必须同时满足：
     - `STR_TO_DATE(ds, '%Y%m%d') AS ds_time`
     - `WHERE ds = DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '%Y%m%d')`
   - `scripts/create_model.py` 会对这条规则做硬校验，不满足就拒绝创建。
3. 调用 `scripts/create_model.py` 创建 Model。
4. 记录返回的 `model_id`。
5. 调用 `/api/card/{id}/query` 验证 Model 可运行。

## Outputs

- `model_id`
- 创建结果摘要
- 验证结果

## Recommended Check

手写 SQL 时，先做预检查：

```bash
python3 scripts/create_model.py \
  --name "Model: 示例" \
  --sql-file model.sql \
  --collection 485 \
  --validate-only
```

## Failure Handling

- 创建失败时返回 API 错误与输入摘要。
- 验证失败时标记该 Model 不可交付，不继续假设后续成功。

## Do Not

- 不重新设计建模方案。
- 不在 Question 层重复写应当在 Model 层完成的清洗逻辑。

## Escalation / Hand-off

- 创建成功后交给 `kmb-question-builder`。
- 若 SQL 本身不满足 Model 粒度要求，回退到 `kmb-sql-analyzer`。
