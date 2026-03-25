#!/bin/bash
# KMB Skill 快捷命令
# 
# 使用方式: source kmb.sh <command> [args]
#
# 命令:
#   query <card_id>    - 查询 Card 数据
#   search <keyword>   - 搜索 KMB
#   collection <id>    - 获取 Collection Cards
#   report [date]      - 生成 Dashboard 139 报告

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    query)
        python3 "$SCRIPT_DIR/query_card.py" "${@:2}"
        ;;
    search)
        python3 "$SCRIPT_DIR/search_kmb.py" "${@:2}"
        ;;
    collection)
        python3 "$SCRIPT_DIR/get_collection_cards.py" "${@:2}"
        ;;
    report)
        python3 "$SCRIPT_DIR/generate_dashboard139_report.py" "${@:2}"
        ;;
    *)
        echo "KMB Skill 快捷命令"
        echo ""
        echo "Usage: source kmb.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  query <card_id>       - 查询 Card 数据"
        echo "  search <keyword>      - 搜索 KMB"
        echo "  collection <id>       - 获取 Collection Cards"
        echo "  report [date]         - 生成 Dashboard 139 报告"
        echo ""
        echo "Examples:"
        echo "  source kmb.sh query 3267"
        echo "  source kmb.sh search 转化"
        echo "  source kmb.sh collection 396"
        ;;
esac
