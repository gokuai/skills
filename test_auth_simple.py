#!/usr/bin/env python3
"""简单测试认证"""

import sys
import os
import time
import hmac
import hashlib
import base64
import json
import urllib.request
import urllib.error
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 认证信息
client_id = "Q339mEsvM2rIC2aF2sYZWAxbFYk"
client_secret = "i3K9A4sHHn3xC3cacGA93peTrr0"
org_client_id = "OAa68aJ3ZwGajbIsxWePiR2EmQ"
org_client_secret = "TxE29C5Y99pEtxD6Eytd3kh3HQ"
api_host = "yk3.gokuai.com"

def calculate_sign(params, secret):
    """计算签名"""
    # 1. 按字母顺序排序参数
    sorted_keys = sorted([k for k in params.keys() if k not in ['sign']])
    
    # 2. 拼接参数值
    values = []
    for key in sorted_keys:
        value = params[key]
        if isinstance(value, (list, dict)):
            value = json.dumps(value, separators=(',', ':'))
        values.append(str(value))
    
    sign_string = '\n'.join(values)
    print(f"待签名字符串:\n{repr(sign_string)}\n")
    
    # 3. HMAC-SHA1
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha1
    ).digest()
    
    # 4. Base64
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

def test_library_info():
    """测试获取库信息"""
    print("=" * 60)
    print("测试：获取库信息")
    print("=" * 60)
    
    endpoint = "/m-open/1/org/info"
    params = {
        "org_client_id": org_client_id,
        "dateline": int(time.time())
    }
    
    # 计算签名
    sign = calculate_sign(params, org_client_secret)
    params['sign'] = sign
    
    print(f"请求参数:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    
    # 发送请求
    url = f"https://{api_host}{endpoint}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    
    encoded_params = []
    for key, value in params.items():
        encoded_value = quote(str(value), safe='')
        encoded_params.append(f"{key}={encoded_value}")
    
    data = '&'.join(encoded_params).encode('utf-8')
    
    print(f"\n请求 URL: {url}")
    print(f"请求数据：{data.decode('utf-8')[:200]}...")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n✅ 成功!")
            print(f"响应：{json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        print(f"\n❌ HTTP 错误：{e.code} - {e.reason}")
        print(f"响应：{error_body}")
        return None
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        return None

def test_file_list():
    """测试文件列表"""
    print("\n" + "=" * 60)
    print("测试：获取文件列表")
    print("=" * 60)
    
    endpoint = "/m-open/1/file/ls"
    params = {
        "org_client_id": org_client_id,
        "fullpath": "",
        "start": 0,
        "size": 5,
        "dateline": int(time.time())
    }
    
    sign = calculate_sign(params, org_client_secret)
    params['sign'] = sign
    
    url = f"https://{api_host}{endpoint}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    
    encoded_params = []
    for key, value in params.items():
        encoded_value = quote(str(value), safe='')
        encoded_params.append(f"{key}={encoded_value}")
    
    data = '&'.join(encoded_params).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n✅ 成功!")
            count = result.get('count', 0)
            print(f"文件总数：{count}")
            for i, file in enumerate(result.get('list', [])[:5], 1):
                file_type = "📁" if file.get('dir') else "📄"
                print(f"  {i}. {file_type} {file.get('filename')} ({file.get('filesize', 0)} 字节)")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        print(f"\n❌ HTTP 错误：{e.code} - {e.reason}")
        print(f"响应：{error_body}")
        return None
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        return None

# 运行测试
if __name__ == "__main__":
    result1 = test_library_info()
    result2 = test_file_list()
    
    print("\n" + "=" * 60)
    if result1 or result2:
        print("✅ 测试通过！API 连接正常！")
    else:
        print("❌ 测试失败，请检查认证信息")
    print("=" * 60)
