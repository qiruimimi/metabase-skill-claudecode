#!/usr/bin/env python3
"""
验证迁移的数据一致性

用法:
    python validate_migration.py --graph-id 75252 --question-id 6529 --date-range "2026-03-01~2026-03-07"
"""

import argparse
import json
import sys
import os

# 添加 core 模块路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'core'))

from core.http import get_json, post_json


def run_question_query(question_id: int, limit: int = 10) -> dict:
    """运行 Question 查询"""
    url = f"/api/card/{question_id}/query"
    payload = {"constraints": {"max-results": limit}}
    return post_json(url, payload)


def get_question_config(question_id: int) -> dict:
    """获取 Question 配置"""
    return get_json(f"/api/card/{question_id}")


def compare_results(space_result: list, kmb_result: list, tolerance: float = 0.01) -> dict:
    """
    对比小站和 KMB 的结果
    返回对比报告
    """
    report = {
        "space_rows": len(space_result),
        "kmb_rows": len(kmb_result),
        "row_match": False,
        "column_match": False,
        "data_match": False,
        "differences": []
    }

    # 检查行数
    report["row_match"] = report["space_rows"] == report["kmb_rows"]

    if not report["row_match"]:
        report["differences"].append(f"行数不一致: 小站={report['space_rows']}, KMB={report['kmb_rows']}")
        return report

    if report["space_rows"] == 0:
        report["differences"].append("双方都没有数据")
        return report

    # 检查列数
    space_cols = len(space_result[0]) if space_result else 0
    kmb_cols = len(kmb_result[0]) if kmb_result else 0
    report["column_match"] = space_cols == kmb_cols

    if not report["column_match"]:
        report["differences"].append(f"列数不一致: 小站={space_cols}, KMB={kmb_cols}")

    # 逐行对比数值
    mismatched_rows = []
    for i, (s_row, k_row) in enumerate(zip(space_result, kmb_result)):
        row_diffs = []
        for j, (s_val, k_val) in enumerate(zip(s_row, k_row)):
            # 数值对比（允许浮点精度差异）
            if isinstance(s_val, (int, float)) and isinstance(k_val, (int, float)):
                if abs(s_val - k_val) > tolerance:
                    row_diffs.append(f"列{j}: {s_val} vs {k_val}")
            elif s_val != k_val:
                row_diffs.append(f"列{j}: {s_val} vs {k_val}")

        if row_diffs:
            mismatched_rows.append(f"行{i+1}: {', '.join(row_diffs)}")

    report["data_match"] = len(mismatched_rows) == 0
    if mismatched_rows:
        report["differences"].extend(mismatched_rows[:5])  # 最多显示5行差异

    return report


def print_comparison_report(report: dict):
    """打印对比报告"""
    print("\n" + "="*60)
    print("数据对比报告")
    print("="*60)

    print(f"\n✓ 行数对比: {report['space_rows']} vs {report['kmb_rows']} {'✅' if report['row_match'] else '❌'}")
    print(f"✓ 列数对比: {'✅' if report['column_match'] else '❌'}")
    print(f"✓ 数据对比: {'✅' if report['data_match'] else '❌'}")

    if report["differences"]:
        print("\n❌ 发现差异:")
        for diff in report["differences"]:
            print(f"   - {diff}")
    else:
        print("\n✅ 数据完全一致!")

    print("="*60)

    return report["row_match"] and report["column_match"] and report["data_match"]


def main():
    parser = argparse.ArgumentParser(description='验证小站到 KMB 的数据一致性')
    parser.add_argument('--graph-id', required=True, help='小站 graph ID')
    parser.add_argument('--question-id', required=True, type=int, help='KMB Question ID')
    parser.add_argument('--date-range', default='', help='日期范围 (如: 2026-03-01~2026-03-07)')
    parser.add_argument('--limit', type=int, default=10, help='对比行数 (默认: 10)')

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"迁移验证: graphId={args.graph_id} → questionId={args.question_id}")
    print(f"{'='*60}")

    # 1. 获取 Question 配置
    print("\n1. 获取 KMB Question 配置...")
    config = get_question_config(args.question_id)
    print(f"   ✓ {config.get('name')}")

    # 2. 运行 KMB Question
    print(f"\n2. 运行 KMB Question (limit={args.limit})...")
    kmb_result = run_question_query(args.question_id, args.limit)
    kmb_rows = kmb_result.get('data', {}).get('rows', [])
    print(f"   ✓ 返回 {len(kmb_rows)} 行")

    # 3. 提示用户运行小站 SQL
    print(f"\n3. 请在小站运行以下 SQL (相同筛选条件):")
    print("-"*60)
    print(f"-- graphId: {args.graph_id}")
    print(f"-- 日期范围: {args.date_range or '默认'}")
    print(f"-- 请复制 space_sql_mapper.py sql {args.graph_id} 获取的 SQL")
    print(f"-- 并添加相同的日期筛选条件和 LIMIT {args.limit}")
    print("-"*60)

    print("\n4. 等待小站结果...")
    print("   请手动输入小站 SQL 结果 (JSON 格式):")
    print("   示例: [[\"2026-03-01\", 100, 200], [\"2026-03-02\", 150, 250]]")
    print("   或按回车跳过对比:")

    user_input = input("\n小站结果: ").strip()

    if not user_input:
        print("   ⏭️  跳过对比")
        return

    try:
        space_rows = json.loads(user_input)
        if not isinstance(space_rows, list):
            print("   ❌ 输入格式错误，应为列表")
            return
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON 解析错误: {e}")
        return

    # 4. 对比结果
    print("\n5. 对比结果...")
    report = compare_results(space_rows, kmb_rows)
    is_match = print_comparison_report(report)

    if is_match:
        print("\n✅ 验证通过! Question 可以交付。")
        sys.exit(0)
    else:
        print("\n❌ 验证失败! 需要修复 Question 配置。")
        sys.exit(1)


if __name__ == '__main__':
    main()
