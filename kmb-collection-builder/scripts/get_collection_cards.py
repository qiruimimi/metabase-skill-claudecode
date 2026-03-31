#!/usr/bin/env python3
"""
获取 Collection 下的所有 Cards

Usage:
    python3 get_collection_cards.py <collection_id>

Examples:
    python3 get_collection_cards.py 396
"""

import argparse
import json
import sys

from core.http import get_json
from core.errors import KMBError, format_error


def get_collection_items(collection_id: int):
    """获取 Collection Items"""
    return get_json(f"/api/collection/{collection_id}/items")


def get_collection_info(collection_id: int):
    """获取 Collection 详情"""
    try:
        return get_json(f"/api/collection/{collection_id}")
    except KMBError:
        return None


def main():
    parser = argparse.ArgumentParser(description='获取 Collection 下的所有 Cards')
    parser.add_argument('collection_id', type=int, help='Collection ID')
    parser.add_argument('--raw', action='store_true', help='输出原始 JSON')

    args = parser.parse_args()

    # 获取 Collection 信息
    info = get_collection_info(args.collection_id)
    if info:
        print(f"Collection: {info.get('name', 'Unknown')} (ID: {args.collection_id})")
        print(f"Location: {info.get('location', 'N/A')}\n")

    # 获取 Items
    try:
        result = get_collection_items(args.collection_id)
    except KMBError as e:
        print(f"Error: {format_error(e)}", file=sys.stderr)
        sys.exit(1)

    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    items = result.get('data', [])
    total = result.get('total', len(items))

    print(f"共 {total} 个 item:\n")

    # 按类型分组
    cards = [i for i in items if i.get('model') == 'card']
    dashboards = [i for i in items if i.get('model') == 'dashboard']
    datasets = [i for i in items if i.get('model') == 'dataset']

    if dashboards:
        print("【Dashboards】")
        for d in dashboards:
            print(f"  [{d.get('id')}] {d.get('name')}")
        print()

    if cards:
        print("【Cards】")
        for c in cards:
            print(f"  [{c.get('id')}] {c.get('name')}")
        print()

    if datasets:
        print("【Datasets】")
        for ds in datasets:
            print(f"  [{ds.get('id')}] {ds.get('name')}")
        print()


if __name__ == '__main__':
    main()
