#!/usr/bin/env python3
"""
够快云库连接测试脚本

测试认证信息和基本功能
"""

import os
import sys
import json
from typing import Dict, Any


def load_config(config_file: str = None) -> Dict[str, Any]:
    """加载配置文件"""
    if config_file and os.path.exists(config_file):
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # 从环境变量加载
    return {
        "credentials": {
            "client_id": os.environ.get("GOUKUAI_CLIENT_ID"),
            "client_secret": os.environ.get("GOUKUAI_CLIENT_SECRET"),
            "org_client_id": os.environ.get("GOUKUAI_ORG_CLIENT_ID"),
            "org_client_secret": os.environ.get("GOUKUAI_ORG_CLIENT_SECRET"),
            "api_host": os.environ.get("GOUKUAI_API_HOST", "yk3.gokuai.com")
        }
    }


def test_authentication(adapter) -> bool:
    """测试认证"""
    print("\n📝 测试认证...")
    
    try:
        result = adapter.authenticate()
        if result:
            print("✅ 认证成功")
            return True
        else:
            print("❌ 认证失败")
            return False
    except Exception as e:
        print(f"❌ 认证错误：{e}")
        return False


def test_library_info(adapter) -> bool:
    """测试获取库信息"""
    print("\n📊 测试获取库信息...")
    
    try:
        info = adapter.get_library_info()
        print("✅ 库信息获取成功")
        print(f"   库名称：{info.get('org_name', 'N/A')}")
        print(f"   库 ID: {info.get('org_id', 'N/A')}")
        print(f"   空间配额：{info.get('size_org_total', 'N/A')} 字节")
        print(f"   已使用：{info.get('size_org_use', 'N/A')} 字节")
        return True
    except Exception as e:
        print(f"❌ 获取库信息失败：{e}")
        return False


def test_list_files(adapter) -> bool:
    """测试列出文件"""
    print("\n📁 测试列出文件...")
    
    try:
        files = adapter.list_files(fullpath="", size=5)
        print(f"✅ 文件列表获取成功（共{len(files)}个文件）")
        
        for i, file in enumerate(files[:3], 1):
            print(f"   {i}. {file.filename} ({'文件夹' if file.dir else '文件'}, {file.filesize} 字节)")
        
        return True
    except Exception as e:
        print(f"❌ 列出文件失败：{e}")
        return False


def test_search_files(adapter) -> bool:
    """测试搜索文件"""
    print("\n🔍 测试搜索文件...")
    
    try:
        files = adapter.search_files(keywords="", size=5)
        print(f"✅ 搜索成功（找到{len(files)}个文件）")
        
        for i, file in enumerate(files[:3], 1):
            print(f"   {i}. {file.fullpath}")
        
        return True
    except Exception as e:
        print(f"❌ 搜索失败：{e}")
        return False


def test_permission(adapter) -> bool:
    """测试权限获取"""
    print("\n🔐 测试权限获取...")
    
    try:
        # 获取根目录权限
        permissions = adapter.get_permission("")
        print(f"✅ 权限获取成功")
        print(f"   权限数量：{len(permissions)}")
        return True
    except Exception as e:
        print(f"❌ 权限获取失败：{e}")
        return False


def test_stat(adapter) -> bool:
    """测试统计信息"""
    print("\n📈 测试统计信息...")
    
    try:
        stat = adapter.get_library_stat()
        print("✅ 统计信息获取成功")
        print(f"   库 ID: {stat.get('org_id', 'N/A')}")
        print(f"   库名称：{stat.get('org_name', 'N/A')}")
        print(f"   文件数量：{stat.get('count_file', 'N/A')}")
        print(f"   空间配额：{stat.get('capacity', 'N/A')} 字节")
        print(f"   已使用：{stat.get('size', 'N/A')} 字节")
        return True
    except Exception as e:
        print(f"❌ 统计信息获取失败：{e}")
        return False


def run_all_tests(config: Dict[str, Any]) -> Dict[str, bool]:
    """运行所有测试"""
    from adapters.goukuai import GoukuaiAdapter
    
    results = {}
    
    # 初始化适配器
    print("=" * 60)
    print("够快云库连接器 - 连接测试")
    print("=" * 60)
    
    print("\n🔧 初始化适配器...")
    try:
        adapter = GoukuaiAdapter(config["credentials"])
        print("✅ 适配器初始化成功")
    except Exception as e:
        print(f"❌ 适配器初始化失败：{e}")
        return {"init": False}
    
    results["init"] = True
    
    # 运行测试
    results["authentication"] = test_authentication(adapter)
    
    if results["authentication"]:
        results["library_info"] = test_library_info(adapter)
        results["list_files"] = test_list_files(adapter)
        results["search_files"] = test_search_files(adapter)
        results["permission"] = test_permission(adapter)
        results["stat"] = test_stat(adapter)
    else:
        print("\n⚠️  认证失败，跳过后续测试")
        results["library_info"] = False
        results["list_files"] = False
        results["search_files"] = False
        results["permission"] = False
        results["stat"] = False
    
    return results


def print_summary(results: Dict[str, bool]):
    """打印测试摘要"""
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n总计：{total} 项测试")
    print(f"通过：{passed} 项 ✅")
    print(f"失败：{failed} 项 ❌")
    print(f"成功率：{passed/total*100:.1f}%")
    
    if failed > 0:
        print("\n失败项:")
        for test, result in results.items():
            if not result:
                print(f"  - {test}")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="够快云库连接测试")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--json", "-j", action="store_true", help="以 JSON 格式输出结果")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 检查必要配置
    creds = config.get("credentials", {})
    if not creds.get("client_id") or not creds.get("client_secret"):
        print("❌ 错误：缺少必要的认证信息")
        print("\n请设置以下环境变量或提供配置文件:")
        print("  GOUKUAI_CLIENT_ID")
        print("  GOUKUAI_CLIENT_SECRET")
        print("  GOUKUAI_ORG_CLIENT_ID (可选)")
        print("  GOUKUAI_ORG_CLIENT_SECRET (可选)")
        sys.exit(1)
    
    # 运行测试
    results = run_all_tests(config)
    
    # 输出结果
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results)
    
    # 返回退出码
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
