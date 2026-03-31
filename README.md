# KMB Metabase Skills

KMB (Metabase) 数据平台操作指南与自动化工具集。目标是让 agent 以渐进式、可组合、低上下文负担的方式完成查询、建模、迁移与交付。

## 物理目录

当前仓库的单一真相目录模型为真实物理路径：

```text
~/.claude/skills/
├── README.md
├── agents/rules/
├── scripts/lib/kmb/
├── manifests/install-modules.json
├── kmb-metabase/
├── kmb-space-query/
├── kmb-sql-analyzer/
├── kmb-model-builder/
├── kmb-question-builder/
├── kmb-viz-config/
├── kmb-dashboard-builder/
├── kmb-collection-builder/
└── kmb-migration/
```

## 逻辑分层 vs 物理目录

逻辑分层用于理解职责，不代表额外目录层级。

- 根导航层: `kmb-metabase`
- 共享规则层: `agents/rules`, `scripts/lib/kmb`
- 原子能力层: `kmb-space-query`, `kmb-sql-analyzer`, `kmb-model-builder`, `kmb-question-builder`, `kmb-viz-config`, `kmb-dashboard-builder`, `kmb-collection-builder`
- 场景编排层: `kmb-migration`

新增模块时，直接放在 `~/.claude/skills/<skill-name>/` 下；不要再引入 `skills/core/`、`skills/extended/` 一类与实际路径不一致的目录表达。

## 渐进式加载规则

1. 先读取当前任务对应 skill 的 `SKILL.md`。
2. 只在当前 skill 明确要求时再读取共享规则、参考文档或离线数据。
3. 遇到 API 细节时进入 `agents/rules/` 或 `kmb-metabase/references/`。
4. 遇到 MBQL 设计细节时优先读取 `kmb-metabase/references/mbql-best-practices.md`。
5. 禁止为一次简单任务预加载全部 `references/`、`rules/`、`space-data/` 文档。

## Pipeline

```text
上游获取 -> 核心分析 -> 下游执行

kmb-space-query
  -> kmb-sql-analyzer
  -> kmb-model-builder
  -> kmb-question-builder
  -> kmb-viz-config
  -> kmb-dashboard-builder

可选编排:
  kmb-collection-builder
  kmb-migration
```

## 模块职责

| 模块 | 类型 | 说明 |
|------|------|------|
| `kmb-metabase` | 根导航 | 提供总入口、SSOT、下钻规则 |
| `kmb-space-query` | 原子 | 查询小站页面、图表、SQL、目录树 |
| `kmb-sql-analyzer` | 原子 | 分析 SQL，输出 `migration_plan.json` |
| `kmb-model-builder` | 原子 | 创建 Model，输出 `model_id` |
| `kmb-question-builder` | 原子 | 创建 MBQL Question，输出 `question_id/card_id` |
| `kmb-viz-config` | 原子 | 更新图表可视化配置 |
| `kmb-dashboard-builder` | 原子 | 创建 Dashboard 并添加卡片，输出 `dashboard_id` |
| `kmb-collection-builder` | 原子 | 创建或更新 Collection，输出 `collection_id` |
| `kmb-migration` | Workflow | 编排迁移全过程，产出资产映射和验收结果 |

## 安装配置

- `minimal`: `agents/rules`, `scripts/lib/kmb`
- `standard`: `minimal` + 全部原子 skill
- `full`: `standard` + `kmb-migration`

详见 `manifests/install-modules.json`。

## 规则优先级 (SSOT)

当多个文档描述存在差异时，按以下顺序判定：

1. `agents/rules/*`
2. 当前 skill 的 `SKILL.md`
3. `kmb-metabase/references/*`
4. 示例片段与历史记录

## 贡献约束

1. 新 skill 必须使用统一执行协议章节：`When to Use`、`Required Inputs`、`If Inputs Missing`、`Execution Steps`、`Outputs`、`Failure Handling`、`Do Not`、`Escalation / Hand-off`。
2. 新 skill 必须补 `config.json`，至少声明 `role`、`inputs`、`outputs`、`depends_on`、`reads`、`scripts`、`requires_env`。
3. 不在原子 skill 中写跨模块业务编排；需要 orchestration 时创建 workflow skill。
