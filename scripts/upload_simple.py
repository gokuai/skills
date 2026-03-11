#!/usr/bin/env python3
"""
简化版本 - 手动触发上传

使用方法：
    python upload_simple.py <file_key> <file_name>

示例：
    python upload_simple.py boxxyy123abc "销售报告.xlsx"
"""

import sys
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

import yaml
from adapters.goukuai import GoukuaiAdapter


def upload_file(file_key: str, file_name: str):
    """上传单个文件到够快云库"""
    
    # 加载配置
    with open(project_root / "config" / "feishu_upload.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    feishu_config = config.get("feishu", {})
    upload_config = config.get("upload", {})
    target_folder = upload_config.get("target_folder", "销售支持")
    
    # 加载够快云库配置
    with open(project_root / "config" / "goukuai.yaml", 'r') as f:
        goukuai_config = yaml.safe_load(f)
    
    goukuai = GoukuaiAdapter(credentials=goukuai_config.get("credentials", {}))
    
    print(f"📥 开始处理：{file_name}")
    
    # 1. 获取飞书令牌
    app_id = feishu_config.get("app_id")
    app_secret = feishu_config.get("app_secret")
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        token = result["tenant_access_token"]
    
    print(f"✅ 令牌获取成功")
    
    # 2. 下载文件
    print(f"⬇️ 下载中...")
    file_url = f"https://open.feishu.cn/open-apis/im/v1/files/{file_key}"
    req = urllib.request.Request(file_url, headers={"Authorization": f"Bearer {token}"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        file_content = resp.read()
    
    print(f"✅ 下载完成 ({len(file_content)} 字节)")
    
    # 3. 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_parts = file_name.rsplit('.', 1)
    if len(name_parts) > 1:
        unique_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
    else:
        unique_name = f"{file_name}_{timestamp}"
    
    # 4. 上传到够快云库
    target_path = f"{target_folder}/{unique_name}"
    print(f"⬆️ 上传到：{target_path}")
    
    result = goukuai.upload_file(target_path, file_content)
    
    print(f"✅ 上传成功!")
    print(f"   路径：{target_path}")
    
    return {"success": True, "target_path": target_path, "file_name": file_name}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法：python upload_simple.py <file_key> <file_name>")
        print("示例：python upload_simple.py boxxyy123abc 销售报告.xlsx")
        sys.exit(1)
    
    file_key = sys.argv[1]
    file_name = sys.argv[2]
    
    try:
        result = upload_file(file_key, file_name)
        print("\n" + "=" * 50)
        print("✅ 完成!")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        sys.exit(1)
