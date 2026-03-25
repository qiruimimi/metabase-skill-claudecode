#!/usr/bin/env python3
"""
Space SQL Mapper - 目录树 → 页面 → SQL 查询工具

用法:
    python space_sql_mapper.py search <关键词>       # 按路径名搜索页面
    python space_sql_mapper.py page <pageId>         # 查看页面详情及图表
    python space_sql_mapper.py graph <graphId>       # 查看图表SQL详情
    python space_sql_mapper.py tree                  # 显示完整目录树
    python space_sql_mapper.py sql <graphId>         # 只输出SQL
"""

import json
import sys
import os

# 数据目录 (相对于 skill 根目录的 space-data/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'space-data')


def _exit_error(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def load_data():
    """加载所有映射数据"""
    with open(f'{DATA_DIR}/page_map.json', 'r') as f:
        page_map = json.load(f)
    with open(f'{DATA_DIR}/graph_map.json', 'r') as f:
        graph_map = json.load(f)
    with open(f'{DATA_DIR}/page_to_graphs.json', 'r') as f:
        page_to_graphs = json.load(f)
    return page_map, graph_map, page_to_graphs

def search_pages(page_map, keyword):
    """按关键词搜索页面"""
    keyword = keyword.lower()
    results = []
    for page_id, page_info in page_map.items():
        if keyword in page_info['path'].lower() or keyword in str(page_info['pageName']).lower():
            results.append(page_info)
    return sorted(results, key=lambda x: x['path'])

def get_page_graphs(page_id, page_to_graphs, graph_map):
    """获取页面的所有图表详情"""
    graph_ids = page_to_graphs.get(str(page_id), [])
    graphs = []
    for gid in graph_ids:
        if str(gid) in graph_map:
            graphs.append(graph_map[str(gid)])
    return graphs

def show_tree(page_map):
    """显示目录树结构"""
    print("=" * 80)
    print("📁 目录树结构 (Space ID: 1140)")
    print("=" * 80)
    
    # 按路径排序
    sorted_pages = sorted(page_map.values(), key=lambda x: x['path'])
    
    for page in sorted_pages:
        path = page['path']
        depth = path.count('/')
        indent = "  " * depth
        name = page['pageName']
        page_id = page['pageId']
        graph_count = page.get('childCount', 0)
        
        # 显示图标
        icon = "📄" if page['pageType'] == 'doc' else "📊"
        
        print(f"{indent}{icon} {name} (pageId={page_id})")

def show_page_detail(page_id, page_map, page_to_graphs, graph_map):
    """显示页面详情"""
    page_id_str = str(page_id)
    if page_id_str not in page_map:
        _exit_error(f"页面 {page_id} 不存在")
    
    page = page_map[page_id_str]
    print("=" * 80)
    print(f"📄 页面详情: {page['pageName']}")
    print("=" * 80)
    print(f"  pageId:    {page['pageId']}")
    print(f"  pageType:  {page['pageType']}")
    print(f"  spaceId:   {page['spaceId']}")
    print(f"  parentId:  {page['parentId']}")
    print(f"  完整路径:   {page['path']}")
    print()
    
    # 显示图表列表
    graphs = get_page_graphs(page_id, page_to_graphs, graph_map)
    if graphs:
        print(f"📊 包含 {len(graphs)} 个图表/查询:")
        print("-" * 80)
        for i, g in enumerate(graphs, 1):
            print(f"  [{i}] graphId={g['graphId']} | queryId={g['queryId']}")
            print(f"      名称: {g['graphName']}")
            if g['description']:
                print(f"      描述: {g['description'][:60]}...")
            print()
    else:
        print("📊 该页面没有图表/查询")

def show_graph_detail(graph_id, graph_map):
    """显示图表/SQL详情"""
    graph_id_str = str(graph_id)
    if graph_id_str not in graph_map:
        _exit_error(f"图表 {graph_id} 不存在")
    
    g = graph_map[graph_id_str]
    print("=" * 80)
    print(f"📊 图表详情: {g['graphName']}")
    print("=" * 80)
    print(f"  graphId: {g['graphId']}")
    print(f"  pageId:  {g['pageId']}")
    print(f"  queryId: {g['queryId']}")
    if g['description']:
        print(f"  描述:    {g['description']}")
    print()
    print("📝 SQL 查询:")
    print("-" * 80)
    print(g['sql'])
    print("-" * 80)

def show_sql_only(graph_id, graph_map):
    """只输出SQL"""
    graph_id_str = str(graph_id)
    if graph_id_str in graph_map:
        print(graph_map[graph_id_str]['sql'])
    else:
        _exit_error(f"图表 {graph_id} 不存在")

def main():
    if len(sys.argv) < 2:
        _exit_error("缺少命令参数，请使用 search/page/graph/sql/tree")
    
    cmd = sys.argv[1]
    
    # 加载数据
    try:
        page_map, graph_map, page_to_graphs = load_data()
    except FileNotFoundError as e:
        _exit_error(f"数据文件不存在: {e}")
    
    if cmd == 'search' and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        results = search_pages(page_map, keyword)
        print(f"🔍 搜索 '{keyword}' 找到 {len(results)} 个结果:")
        print("-" * 80)
        for p in results[:20]:  # 最多显示20个
            graphs = page_to_graphs.get(str(p['pageId']), [])
            graph_info = f" [{len(graphs)}个图表]" if graphs else ""
            print(f"  pageId={p['pageId']} | {p['path']}{graph_info}")
        if len(results) > 20:
            print(f"  ... 还有 {len(results)-20} 个结果")
    
    elif cmd == 'page' and len(sys.argv) >= 3:
        show_page_detail(sys.argv[2], page_map, page_to_graphs, graph_map)
    
    elif cmd == 'graph' and len(sys.argv) >= 3:
        show_graph_detail(sys.argv[2], graph_map)
    
    elif cmd == 'sql' and len(sys.argv) >= 3:
        show_sql_only(sys.argv[2], graph_map)
    
    elif cmd == 'tree':
        show_tree(page_map)
    
    else:
        _exit_error(f"不支持的命令: {cmd}，请使用 search/page/graph/sql/tree")

if __name__ == '__main__':
    main()
