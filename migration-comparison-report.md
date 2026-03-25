# 迁移对比报告: 旧版本 vs V1.0 新版本

## 对比概览

| 维度 | 旧版本 | V1.0 新版本 | 改进 |
|------|--------|-------------|------|
| **组织结构** | 分散在根 Collection | 独立子 Collection | ✅ 资源隔离 |
| **命名规范** | 无版本号 | V1.0 - XXX 前缀 | ✅ 版本管理 |
| **架构设计** | 直接创建 Questions | Model → Question → Dashboard | ✅ 分层复用 |
| **SQL 引用** | 直接写底层 SQL | 使用 {{#model_id}} | ✅ 可维护性 |

---

## 详细对比

### 1. 组织结构

**旧版本 (之前)**
```
Collection 485 (Traffic)
├── Question 4972 (Daily Paid Revenue) - 已存在，复用
├── Question 5003 (Revenue账单分层) - 新创建，散落在根目录
└── Dashboard 406 - 更新，与其他 Dashboard 混在一起
```

**V1.0 新版本**
```
Collection 490 (【55074】Revenue用户分层)
├── Model 5005 (V1.0 - Revenue Invoice Base)
├── Question 5006 (V1.0 - Daily Paid Revenue)
├── Question 5007 (V1.0 - Revenue账单分层)
└── Dashboard 411 (V1.0 - 【55074】Revenue用户分层 Dashboard)
```

**改进点**:
- 所有相关资源在同一个 Collection 中
- 便于权限管理和资源查找
- 清晰的资源边界

---

### 2. 架构设计

**旧版本 (直接 SQL)**
```sql
-- Question 直接写底层 SQL
SELECT ... FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
WHERE ds = ...
```

**V1.0 新版本 (Model 分层)**
```sql
-- Step 1: Model 定义基础数据
SELECT pay_success_day, user_id, amt_usd, ... 
FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
WHERE ds = ...

-- Step 2: Question 引用 Model
SELECT ... 
FROM (SELECT * FROM {{#model_id}}) AS model_data
GROUP BY ...
```

**改进点**:
- Model 层封装底层表结构
- Questions 基于 Model，逻辑清晰
- 底层表变更只需修改 Model

---

### 3. 版本管理

**旧版本**
- 无版本标识
- 难以追踪变更历史
- 无法回滚

**V1.0 新版本**
- 所有资源带版本前缀: `V1.0 - XXX`
- 便于版本追踪
- 未来可以创建 V2.0 迭代

---

### 4. Skill 实践发现

#### 发现 1: Model 引用语法
**问题**: `{{#model_id}}` 在原生 SQL 中无法直接解析
**解决**: 使用子查询方式 `(SELECT * FROM {{#model_id}}) AS model_data`
**更新 Skill**: 在 `rules/api-standards.md` 中补充 Model 引用最佳实践

#### 发现 2: Model 创建参数
**问题**: Model 也需要 `display` 和 `visualization_settings` 字段
**解决**: 添加 `display: "table"` 和空 `visualization_settings: {}`
**更新 Skill**: 在 `SKILL.md` 的 Model 创建示例中补充

#### 发现 3: 子 Collection 创建
**问题**: API 支持直接在创建时指定 `parent_id`
**解决**: 使用 `POST /api/collection` 带 `parent_id` 参数
**更新 Skill**: 在 API 端点速查表中补充

#### 发现 4: 批量添加卡片
**问题**: 需要先获取已有 dashcards，再追加新卡片
**解决**: GET Dashboard → 提取已有 cards → 追加新 cards → PUT 更新
**更新 Skill**: 在 Dashboard 卡片管理章节补充完整流程

---

## 待改进点 (V2.0 方向)

1. **参数化**: 添加时间参数支持（开始日期、结束日期）
2. **在约用户数**: 新版本暂未包含原 SQL 中的在约用户数统计（涉及 UNION ALL）
3. **过滤条件**: 原 SQL 支持的多维过滤（国家、SKU 等）暂未实现
4. **自动化**: 可以添加脚本自动对比新旧版本数据一致性

---

## Skill 更新建议

基于本次迁移实践，建议更新以下内容到 skill:

### 1. SKILL.md
- [ ] 在 API 端点速查表中添加 Collection 创建 API
- [ ] 在 Model 创建示例中补充 `display` 和 `visualization_settings`
- [ ] 在 Dashboard 卡片管理中添加"批量追加卡片"的完整流程

### 2. rules/api-standards.md
- [ ] 补充 Model 引用的正确语法
- [ ] 补充子 Collection 创建方法
- [ ] 补充批量更新 Dashboard 的最佳实践

### 3. 新增 migration-checklist.md
- [ ] 创建迁移检查清单模板
- [ ] 包含版本命名、架构设计、数据验证等检查项
