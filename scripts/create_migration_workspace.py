#!/usr/bin/env python3
"""
自动创建迁移工作目录结构

用法:
    python create_migration_workspace.py --page-id 34433 [--root-collection 545]

功能:
    1. 根据小站 page 路径，在 KMB 中逐级创建 Collection
    2. 最终创建 【pageId】pageName - 日期 - 模型 的工作目录
    3. 返回最终的 collection_id 用于后续资源创建
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple

# 添加 core 模块路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'core'))

from core.config import API_HOST, API_KEY
from core.http import get_json, post_json

# 数据目录
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(SKILL_DIR, 'space-data')


def load_page_data() -> dict:
    """加载小站 page 数据"""
    with open(f'{DATA_DIR}/page_map.json', 'r') as f:
        return json.load(f)


def get_page_path_chain(page_id: str, page_map: dict) -> List[Tuple[str, str]]:
    """
    获取 page 的完整路径链
    返回: [(folder_name, page_id), ...] 从根到父级
    """
    chain = []
    current_id = str(page_id)
    visited = set()

    while current_id in page_map and current_id not in visited:
        visited.add(current_id)
        page = page_map[current_id]

        # 跳过根页面
        if page['parentId'] == -1:
            break

        chain.append((page['pageName'], current_id))

        # 向上查找父级
        parent_id = str(page['parentId'])
        if parent_id in page_map:
            current_id = parent_id
        else:
            break

    # 反转，让根在前面
    chain.reverse()
    return chain


def find_or_create_collection(name: str, parent_id: int, description: str = "") -> int:
    """
    查找或创建 Collection
    返回 collection_id
    """
    # 先搜索是否已存在
    url = f"/api/collection?parent_id={parent_id}"
    result = get_json(url)

    if result and 'data' in result:
        for col in result['data']:
            if col.get('name') == name:
                print(f"    ✅ 已存在: {name} (id={col['id']})")
                return col['id']

    # 不存在则创建
    url = f"/api/collection"
    payload = {
        "name": name,
        "description": description,
        "parent_id": parent_id,
        "authority_level": None
    }

    result = post_json(url, payload)
    if result and 'id' in result:
        print(f"    🆕 新创建: {name} (id={result['id']})")
        return result['id']
    else:
        print(f"    ❌ 创建失败: {name}")
        print(f"       错误: {result}")
        return None


def create_workspace(page_id: str, root_collection_id: int = 545) -> Optional[int]:
    """
    创建完整的迁移工作目录
    返回最终的工作目录 collection_id
    """
    print(f"\n{'='*60}")
    print(f"迁移工作目录创建: pageId={page_id}")
    print(f"{'='*60}")

    # 加载 page 数据
    page_map = load_page_data()

    if page_id not in page_map:
        print(f"❌ pageId={page_id} 不存在于 page_map.json")
        return None

    page = page_map[page_id]
    page_name = page['pageName']
    full_path = page['path']

    print(f"小站路径: {full_path}")
    print(f"\n创建层级:")

    # 获取路径链
    path_chain = get_page_path_chain(page_id, page_map)

    # 逐级创建/获取 Collection
    current_parent_id = root_collection_id
    created_collections = []

    for idx, (folder_name, pid) in enumerate(path_chain[:-1], 1):  # 不包括当前 page
        col_id = find_or_create_collection(
            name=folder_name,
            parent_id=current_parent_id,
            description=f"小站迁移目录 (自动创建)"
        )

        if col_id is None:
            print(f"❌ 创建失败，中断")
            return None

        created_collections.append((folder_name, col_id))
        current_parent_id = col_id

    # 最终父级是 path_chain 的倒数第二个（page 的父级）
    # 如果没有父级（直接挂在根下），就用 root_collection_id
    if len(path_chain) >= 2:
        final_parent_id = created_collections[-1][1] if created_collections else root_collection_id
    else:
        final_parent_id = root_collection_id

    # 创建最终工作目录
    today = datetime.now().strftime('%Y%m%d')
    workspace_name = f"【{page_id}】{page_name} - {today} - 模型"
    workspace_desc = f"小站 page/{page_id} 迁移工作目录\n原始路径: {full_path}"

    print(f"\n最终工作目录:")
    workspace_id = find_or_create_collection(
        name=workspace_name,
        parent_id=final_parent_id,
        description=workspace_desc
    )

    if workspace_id:
        print(f"\n{'='*60}")
        print(f"✅ 工作目录已准备就绪: collection_id={workspace_id}")
        print(f"{'='*60}")
        print(f"\n后续使用:")
        print(f"  export TARGET_COLLECTION={workspace_id}")
        print(f"  # 然后创建 Model/Question/Dashboard 都使用此 collection_id")

    return workspace_id


def main():
    parser = argparse.ArgumentParser(
        description='自动创建小站迁移的 KMB Collection 目录结构'
    )
    parser.add_argument(
        '--page-id', '-p',
        required=True,
        help='小站 page ID (如: 34433)'
    )
    parser.add_argument(
        '--root-collection', '-r',
        type=int,
        default=545,
        help='KMB 根 Collection ID (默认: 545)'
    )

    args = parser.parse_args()

    workspace_id = create_workspace(args.page_id, args.root_collection)

    if workspace_id:
        print(f"\n🎯 最终 collection_id: {workspace_id}")
        sys.exit(0)
    else:
        print("\n❌ 创建工作目录失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
