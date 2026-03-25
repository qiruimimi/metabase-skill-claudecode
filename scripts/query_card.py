#!/usr/bin/env python3
"""
KMB Card 数据查询工具

Usage:
    python3 query_card.py <card_id> [--limit 100] [--output json|csv|table]

Examples:
    python3 query_card.py 3267
    python3 query_card.py 3267 --limit 50 --output csv
    python3 query_card.py 3267 --output table
"""

import argparse
import json
import csv
import sys
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# 配置
API_HOST = "https://kmb.qunhequnhe.com"
API_KEY = "mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="


def query_card(card_id: int, limit: int = 10000):
    """查询 Card 数据"""
    url = f"{API_HOST}/api/card/{card_id}/query"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "parameters": [],
        "constraints": {"max-results": limit}
    }).encode('utf-8')

    req = Request(url, data=data, headers=headers, method='POST')

    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        try:
            error_body = json.loads(e.read().decode('utf-8'))
            print(f"Details: {error_body}", file=sys.stderr)
        except:
            pass
        sys.exit(1)


def format_as_table(data: dict):
    """格式化为表格输出"""
    rows = data.get('data', {}).get('rows', [])
    cols = data.get('data', {}).get('cols', [])

    if not rows or not cols:
        print("No data returned")
        return

    # 获取列名
    headers = [col.get('name', f"Col_{i}") for i, col in enumerate(cols)]

    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows[:100]:  # 只计算前100行
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # 打印表头
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # 打印数据
    for row in rows:
        print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))

    if len(rows) > 100:
        print(f"\n... ({len(rows) - 100} more rows)")


def format_as_csv(data: dict):
    """格式化为 CSV 输出"""
    rows = data.get('data', {}).get('rows', [])
    cols = data.get('data', {}).get('cols', [])

    if not rows or not cols:
        return

    headers = [col.get('name', f"Col_{i}") for i, col in enumerate(cols)]

    writer = csv.writer(sys.stdout)
    writer.writerow(headers)
    writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='KMB Card 数据查询工具')
    parser.add_argument('card_id', type=int, help='Card ID')
    parser.add_argument('--limit', type=int, default=10000, help='返回数据条数限制 (默认: 10000)')
    parser.add_argument('--output', type=str, default='json', choices=['json', 'csv', 'table'],
                        help='输出格式 (默认: json)')
    parser.add_argument('--pretty', action='store_true', help='JSON 美化输出')

    args = parser.parse_args()

    # 查询数据
    result = query_card(args.card_id, args.limit)

    # 格式化输出
    if args.output == 'json':
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))
    elif args.output == 'csv':
        format_as_csv(result)
    elif args.output == 'table':
        format_as_table(result)


if __name__ == '__main__':
    main()
