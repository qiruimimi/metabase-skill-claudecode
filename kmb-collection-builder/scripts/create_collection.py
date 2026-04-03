#!/usr/bin/env python3
"""Create or reuse KMB collections with the shared HTTP transport."""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "kmb-metabase" / "scripts" / "lib"))

from kmb import API_HOST as DEFAULT_API_HOST, get_json, post_json, format_error


API_HOST = DEFAULT_API_HOST
API_KEY = None


def collection_exists(name, parent_id=None):
    """检查指定 parent 下是否已存在同名 Collection"""
    try:
        collections = get_json("/api/collection")

        for col in collections:
            if col.get("name") == name:
                if parent_id is None or col.get("parent_id") == parent_id:
                    return col.get("id")
        return None
    except Exception as e:
        print(f"⚠️  检查 Collection 是否存在时出错: {e}")
        return None


def create_collection(name, parent_id=None, description=None):
    """创建 Collection"""
    payload = {
        "name": name,
        "description": description or f"Collection: {name}"
    }
    if parent_id:
        payload["parent_id"] = parent_id

    return post_json("/api/collection", payload)


def main():
    global API_KEY, API_HOST

    parser = argparse.ArgumentParser(description="创建 Metabase Collection")
    parser.add_argument("--name", required=True, help="Collection 名称")
    parser.add_argument("--parent-id", type=int, help="父 Collection ID")
    parser.add_argument("--description", help="Collection 描述")
    parser.add_argument("--api-key", help="Metabase API Key")
    parser.add_argument("--api-host", default=API_HOST, help="Metabase API Host")
    parser.add_argument("--skip-if-exists", action="store_true",
                        help="如果 Collection 已存在则跳过创建，返回现有 ID")
    parser.add_argument("--output", choices=["json", "id"], default="json",
                        help="输出格式: json(完整信息) 或 id(仅 ID)")

    args = parser.parse_args()

    # 设置 API 配置
    API_HOST = args.api_host
    API_KEY = args.api_key or os.environ.get("KMB_API_KEY")

    try:
        # 检查是否已存在
        existing_id = collection_exists(args.name, args.parent_id)
        if existing_id:
            if args.skip_if_exists:
                print(f"ℹ️  Collection '{args.name}' 已存在 (ID: {existing_id})")
                if args.output == "id":
                    print(existing_id)
                else:
                    print(json.dumps({
                        "id": existing_id,
                        "name": args.name,
                        "status": "exists"
                    }, indent=2))
                sys.exit(0)
            else:
                print(f"❌ 错误: Collection '{args.name}' 已存在 (ID: {existing_id})", file=sys.stderr)
                print("使用 --skip-if-exists 复用现有 Collection", file=sys.stderr)
                sys.exit(1)

        # 创建 Collection
        result = create_collection(args.name, args.parent_id, args.description)
        collection_id = result.get("id")

        print(f"✅ 创建成功: {args.name} (ID: {collection_id})")
        if args.output == "id":
            print(collection_id)
        else:
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ 错误: {format_error(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
