#!/bin/bash
# KMB Skill 自动更新脚本
# 用于将实战经验沉淀到 skill 中

SKILL_DIR="$HOME/.claude/skills/kmb-metabase"
MEMORY_DIR="$HOME/.claude/projects"

echo "=== KMB Skill 自动更新 ==="
echo "Skill 目录: $SKILL_DIR"
echo ""

# 检查最近的 memory 文件
echo "1. 检查最近的实战经验..."
latest_memory=$(ls -t $MEMORY_DIR/2026-*.md 2>/dev/null | head -5)
echo "最近 memory 文件:"
echo "$latest_memory"
echo ""

# 检查需要更新的文件
echo "2. 检查 Skill 文件状态..."
echo ""
echo "references/migration-guide.md:"
wc -l $SKILL_DIR/references/migration-guide.md

echo ""
echo "references/migration-guide-v2.md:"
wc -l $SKILL_DIR/references/migration-guide-v2.md

echo ""
echo "3. 更新检查清单:"
echo "  [ ] 是否有新的迁移案例需要添加?"
echo "  [ ] 是否有新的问题修复方法需要记录?"
echo "  [ ] 是否有新的 API 用法需要补充?"
echo "  [ ] 是否有新的脚本需要添加?"
echo ""

# 显示快速更新命令
echo "4. 快速更新命令:"
echo ""
echo "# 追加实战经验到 migration-guide-v2.md"
echo "cat >> $SKILL_DIR/references/migration-guide-v2.md << 'EOF'"
echo "## 新增实战案例 (日期)"
echo "..."
echo "EOF"
echo ""
echo "# 更新 SKILL.md 的快速访问"
echo "# 编辑 $SKILL_DIR/SKILL.md"
echo ""

# 记录更新日志
echo "5. 记录更新..."
echo "$(date '+%Y-%m-%d %H:%M') - Skill 检查完成" >> $SKILL_DIR/memory/update.log 2>/dev/null || true

echo ""
echo "=== 完成 ==="
echo "提示: 使用 'kmb-skill-update' 命令可再次运行此检查"
