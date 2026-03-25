#!/usr/bin/env python3
"""
KMB 搜索工具

Usage:
    python3 search_kmb.py <keyword>

Examples:
    python3 search_kmb.py 转化
    python3 search_kmb.py "LTV/CAC"
"""

import argparse
import json
import sys

from core.http import get_json
from core.errors import KMBError, format_error


def search_kmb(keyword: str):
    """搜索 KMB 内容"""
    return get_json("/api/search", {"q": keyword})


def format_results(data: dict):
    """格式化搜索结果"""
    items = data.get('data', [])
    total = data.get('total', len(items))

    print(f"找到 {total} 个结果:\n")

    # 按类型分组
    by_type = {}
    for item in items:
        model = item.get('model', 'unknown')
        if model not in by_type:
            by_type[model] = []
        by_type[model].append(item)

    # 打印分组结果
    for model, model_items in sorted(by_type.items()):
        print(f"\n【{model.upper()}】({len(model_items)})")
        print("-" * 40)
        for item in model_items[:10]:  # 每类最多显示10个
            item_id = item.get('id', 'N/A')
            name = item.get('name', 'Unnamed')
            collection = item.get('collection', {}).get('name', 'No Collection')
            print(f"  [{item_id}] {name}")
            if collection != 'No Collection':
                print(f"      └─ Collection: {collection}")

        if len(model_items) > 10:
            print(f"  ... 还有 {len(model_items) - 10} 个结果")


def main():
    parser = argparse.ArgumentParser(description='KMB 搜索工具')
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('--raw', action='store_true', help='输出原始 JSON')

    args = parser.parse_args()

    try:
        result = search_kmb(args.keyword)
    except KMBError as e:
        print(f"Error: {format_error(e)}", file=sys.stderr)
        sys.exit(1)

    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        format_results(result)


if __name__ == '__main__':
    main()
