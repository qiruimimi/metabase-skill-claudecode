# KMB Skill 更新报告

> ⚠️ 历史记录（2026-03-19），不作为当前规范基线。
> 当前执行规范以 `rules/*` 为准，实践参考以 `references/*` 为准。

## 更新时间
2026-03-19

## 参考来源
GitLab: `beiyan/claude-code-test` - Metabase Skill

## 更新内容

### 1. SKILL.md 主要更新

#### 新增内容
- **Iron Law（铁律）**: 在开头添加了工具约束声明
  - （当时版本）强调 curl 优先调用 API
  - （当时版本）强调避免创建 SDK、库或复杂客户端
  - 保持简洁、验证、交互三大原则

#### 新增章节
1. **API 调用规范**
   - 认证方式（必须使用 X-API-Key）
   - Collection 层级结构（location vs parent_id）⭐
   - Dashboard 卡片管理（PUT 方法、负数 ID）⭐
   - 创建查询的最佳实践（当时版本：原生 SQL 优先；当前基线：默认 Model + MBQL）⭐

2. **错误处理与诊断**
   - HTTP 401 - 认证失败
   - HTTP 403 - 权限不足
   - HTTP 404 - 资源不存在
   - HTTP 500 - 服务器错误
   - 连接失败

3. **反模式（常见错误）**
   - 12 个常见错误及正确做法对照表

### 2. 新增 rules/ 目录

创建了 4 个规则文件：

| 文件 | 内容 |
|------|------|
| `rules/constraints.md` | 工具约束（Iron Law）详细说明 |
| `rules/api-standards.md` | API 调用标准、Collection 层级、Dashboard 卡片管理 |
| `rules/error-handling.md` | 详细错误处理与诊断流程 |
| `rules/red-flags.md` | 危险信号清单及处理流程 |

### 3. 关键改进点

#### Collection 层级结构
- **发现**: Metabase 使用 `location` 字段而非 `parent_id` 表示层级关系
- **应用**: 添加了详细的查询方法和示例

#### Dashboard 卡片添加
- **发现**: 必须使用 PUT 方法更新整个 Dashboard，不能用 POST
- **应用**: 添加了详细的 API 调用示例和关键要点

#### 查询创建
- **发现**: 原生 SQL 在复杂场景更灵活（当前基线：默认 Model + MBQL，复杂场景回退原生 SQL）
- **应用**: 添加了决策树和最佳实践说明

#### 错误处理
- **发现**: 需要详细的错误诊断步骤
- **应用**: 添加了 HTTP 401/403/404/500 的诊断流程

#### 反模式
- **发现**: 常见错误模式需要明确列出
- **应用**: 添加了 12 个常见错误及正确做法对照表

## 文件结构对比

### 更新前
```
kmb-skill/
├── SKILL.md
├── README.md
├── references/
│   ├── api-reference.md
│   ├── mbql-best-practices.md
│   ├── dashboard-configs.md
│   ├── card-catalog.md
│   └── migration-guide.md
├── scripts/
└── space-data/
```

### 更新后
```
kmb-skill/
├── SKILL.md (更新)
├── README.md
├── references/
│   ├── api-reference.md
│   ├── mbql-best-practices.md
│   ├── dashboard-configs.md
│   ├── card-catalog.md
│   └── migration-guide.md
├── rules/ (新增)
│   ├── constraints.md
│   ├── api-standards.md
│   ├── error-handling.md
│   └── red-flags.md
├── scripts/
└── space-data/
```

## 建议后续优化

1. **交互式对话**: 当前 skill 是指令式风格，可考虑增加交互式菜单（如原 skill 的 /metabase 命令）
2. **配置管理**: 当前 API key 硬编码，可考虑添加配置文件支持
3. **文档缓存**: 原 skill 有 WebFetch 文档更新功能，可考虑添加
4. **更多示例**: 可添加更多实际使用示例和模板

## 总结

本次更新从 GitLab 的 metabase skill 中汲取了以下精华：
- ✅ Iron Law（铁律）约束
- ✅ Collection 层级结构的正确理解
- ✅ Dashboard 卡片管理的正确方法
- ✅ 当时版本以原生 SQL 优先推进复杂迁移，当前已对齐为默认 Model + MBQL、复杂场景回退原生 SQL
- ✅ 详细的错误处理流程
- ✅ 常见错误模式（反模式）

这些改进使我们的 skill 更加完整、规范和实用。
