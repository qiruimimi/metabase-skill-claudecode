# KMB (Metabase) Skill 使用指南

## 快速开始

### 1. 激活 Skill

在 Claude Code 会话中直接运行 `/kmb-metabase` 即可调用此 Skill。

### 2. 使用脚本工具

```bash
# 查询 Card 数据
python3 ~/.claude/skills/kmb-metabase/scripts/query_card.py 3267 --output table

# 搜索 KMB
python3 ~/.claude/skills/kmb-metabase/scripts/search_kmb.py 转化

# 获取 Collection 下的 Cards
python3 ~/.claude/skills/kmb-metabase/scripts/get_collection_cards.py 396

# 生成 Dashboard 139 报告
python3 ~/.claude/skills/kmb-metabase/scripts/generate_dashboard139_report.py
```

### 3. 快捷命令 (可选)

添加 alias 到 ~/.zshrc 或 ~/.bashrc:

```bash
alias kmb="source ~/.claude/skills/kmb-metabase/scripts/kmb.sh"
```

然后可以使用:
```bash
kmb query 3267
kmb search 转化
kmb collection 396
kmb report
```

---

## Skill 结构

```
kmb-metabase/
├── SKILL.md                          # 主文档（Skill 入口）
├── README.md                         # 本文件（使用指南）
├── references/
│   ├── api-reference.md              # 完整 API 文档
│   ├── dashboard-configs.md          # Dashboard 配置详情
│   └── card-catalog.md               # 常用 Card 目录
├── scripts/
│   ├── core/                         # 统一配置/HTTP/错误处理内核
│   │   ├── config.py
│   │   ├── http.py
│   │   └── errors.py
│   ├── query_card.py                 # Card 数据查询
│   ├── search_kmb.py                 # KMB 搜索
│   ├── get_collection_cards.py       # Collection 查询
│   ├── generate_dashboard139_report.py # 报告生成
│   └── kmb.sh                        # 快捷命令
├── tests/                            # 最小自动化测试
└── reports/                          # 报告输出目录
```

---

## 扩展指南

### 添加新的 Dashboard 支持

1. 在 `references/dashboard-configs.md` 中添加配置
2. 复制 `generate_dashboard139_report.py` 创建新的报告脚本
3. 更新 `SKILL.md` 的快速访问表格

### 添加新的 Card 查询

1. 使用 `query_card.py` 测试 Card ID
2. 如需定制输出，创建新的 Python 脚本
3. 更新 `references/card-catalog.md`

---

## 常见问题

### Q: API Key 在哪里配置？
A: 在 `scripts/core/config.py` 中统一配置 `API_KEY`。

### Q: 如何添加只读 API？
A: 编辑 `references/api-reference.md`，添加新的端点说明。

### Q: 可以支持写操作吗？
A: 当前 Skill 以只读为主，但可以通过扩展脚本支持创建/更新操作。

---

*最后更新: 2026-03-26*
