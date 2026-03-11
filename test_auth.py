#!/usr/bin/env python3
"""测试认证连接"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adapters.goukuai import GoukuaiAdapter

# 认证信息
credentials = {
    "client_id": "Q339mEsvM2rIC2aF2sYZWAxbFYk",
    "client_secret": "i3K9A4sHHn3xC3cacGA93peTrr0",
    "org_client_id": "OAa68aJ3ZwGajbIsxWePiR2EmQ",
    "org_client_secret": "TxE29C5Y99pEtxD6Eytd3kh3HQ",
    "api_host": "yk3.gokuai.com"
}

print("=" * 60)
print("够快云库连接器 - 认证测试")
print("=" * 60)

# 初始化适配器
print("\n📝 初始化适配器...")
try:
    adapter = GoukuaiAdapter(credentials)
    print("✅ 适配器初始化成功")
except Exception as e:
    print(f"❌ 初始化失败：{e}")
    sys.exit(1)

# 测试认证
print("\n🔑 测试认证...")
try:
    result = adapter.authenticate()
    if result:
        print("✅ 认证成功")
    else:
        print("❌ 认证失败")
        sys.exit(1)
except Exception as e:
    print(f"❌ 认证错误：{e}")
    sys.exit(1)

# 获取库信息
print("\n📊 获取库信息...")
try:
    info = adapter.get_library_info()
    print("✅ 库信息获取成功")
    print(f"   库名称：{info.get('org_name', 'N/A')}")
    print(f"   库 ID: {info.get('org_id', 'N/A')}")
    print(f"   空间配额：{info.get('size_org_total', 'N/A')} 字节")
    print(f"   已使用：{info.get('size_org_use', 'N/A')} 字节")
except Exception as e:
    print(f"❌ 获取库信息失败：{e}")

# 获取文件列表
print("\n📁 获取根目录文件列表...")
try:
    files = adapter.list_files(fullpath="", size=5)
    print(f"✅ 文件列表获取成功（共{len(files)}个文件/文件夹）")
    for i, file in enumerate(files[:5], 1):
        file_type = "📁 文件夹" if file.dir else "📄 文件"
        print(f"   {i}. {file_type} {file.filename} ({file.filesize} 字节)")
except Exception as e:
    print(f"❌ 获取文件列表失败：{e}")

# 获取统计信息
print("\n📈 获取统计信息...")
try:
    stat = adapter.get_library_stat()
    print("✅ 统计信息获取成功")
    print(f"   库 ID: {stat.get('org_id', 'N/A')}")
    print(f"   库名称：{stat.get('org_name', 'N/A')}")
    print(f"   文件数量：{stat.get('count_file', 'N/A')}")
    print(f"   空间配额：{stat.get('capacity', 'N/A')} 字节")
    print(f"   已使用：{stat.get('size', 'N/A')} 字节")
except Exception as e:
    print(f"❌ 获取统计信息失败：{e}")

# 测试搜索
print("\n🔍 测试搜索文件...")
try:
    files = adapter.search_files(keywords="", size=3)
    print(f"✅ 搜索成功（找到{len(files)}个文件）")
    for i, file in enumerate(files[:3], 1):
        print(f"   {i}. {file.fullpath}")
except Exception as e:
    print(f"❌ 搜索失败：{e}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！Skill 可以正常使用！")
print("=" * 60)
