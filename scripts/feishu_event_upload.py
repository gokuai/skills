#!/usr/bin/env python3
"""
飞书事件订阅版本 - 文件自动上传

通过飞书事件订阅接收文件消息，实时上传到够快云库

配置步骤：
1. 在飞书开发者后台配置事件订阅
2. 订阅 im:message.group_at_msg 事件
3. 配置请求网址（需要公网可访问）
4. 当用户在群里@机器人并发送文件时自动上传
"""

import os
import sys
import json
import time
import hashlib
import hmac
import base64
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

import yaml
from adapters.goukuai import GoukuaiAdapter


class FeishuEventUploader:
    """飞书事件订阅文件上传器"""
    
    def __init__(self):
        """初始化上传器"""
        # 加载配置
        config_path = project_root / "config" / "feishu_upload.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.feishu_config = config.get("feishu", {})
        self.upload_config = config.get("upload", {})
        self.target_folder = self.upload_config.get("target_folder", "销售支持")
        
        # 加载够快云库配置
        goukuai_config_path = project_root / self.upload_config.get("goukuai", {}).get("config_file", "config/goukuai.yaml")
        with open(goukuai_config_path, 'r', encoding='utf-8') as f:
            goukuai_config = yaml.safe_load(f)
        
        self.goukuai = GoukuaiAdapter(credentials=goukuai_config.get("credentials", {}))
        
        # 已处理文件记录
        self.processed_files = self._load_processed_files()
    
    def _load_processed_files(self) -> set:
        """加载已处理文件记录"""
        record_file = project_root / "logs" / "processed_files.json"
        if record_file.exists():
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get("files", []))
        return set()
    
    def _save_processed_files(self):
        """保存已处理文件记录"""
        record_file = project_root / "logs" / "processed_files.json"
        record_file.parent.mkdir(parents=True, exist_ok=True)
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump({"files": list(self.processed_files), "updated": time.time()}, f, indent=2)
    
    def _get_feishu_token(self) -> str:
        """获取飞书应用访问令牌"""
        app_id = self.feishu_config.get("app_id")
        app_secret = self.feishu_config.get("app_secret")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = json.dumps({
            "app_id": app_id,
            "app_secret": app_secret
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") != 0:
                raise Exception(f"获取令牌失败：{result}")
            return result["tenant_access_token"]
    
    def _download_file(self, token: str, file_key: str) -> bytes:
        """下载飞书文件"""
        url = f"https://open.feishu.cn/open-apis/im/v1/files/{file_key}"
        
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    
    def upload_file_from_event(self, event_data: Dict) -> Dict:
        """
        从事件数据上传文件
        
        Args:
            event_data: 飞书事件数据（包含 message 和 file 信息）
        
        Returns:
            Dict: 上传结果
        """
        result = {
            "success": False,
            "file_name": None,
            "target_path": None,
            "error": None,
            "message": ""
        }
        
        try:
            # 解析事件数据
            message = event_data.get("message", {})
            file_info = event_data.get("file", {})
            
            file_key = file_info.get("file_key")
            file_name = file_info.get("file_name", "unknown")
            message_id = message.get("message_id")
            
            if not file_key:
                result["error"] = "未找到文件 key"
                return result
            
            # 检查是否已处理
            if file_key in self.processed_files:
                result["message"] = "文件已处理，跳过"
                return result
            
            print(f"📥 开始处理文件：{file_name}")
            
            # 1. 获取飞书令牌
            token = self._get_feishu_token()
            
            # 2. 下载文件
            print(f"⬇️ 下载中：{file_name}")
            file_content = self._download_file(token, file_key)
            
            # 3. 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_parts = file_name.rsplit('.', 1)
            if len(name_parts) > 1:
                unique_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                unique_name = f"{file_name}_{timestamp}"
            
            # 4. 上传到够快云库
            target_path = f"{self.target_folder}/{unique_name}"
            print(f"⬆️ 上传中：{target_path}")
            
            upload_result = self.goukuai.upload_file(target_path, file_content)
            
            # 5. 记录已处理文件
            self.processed_files.add(file_key)
            self._save_processed_files()
            
            print(f"✅ 上传成功：{file_name} → {target_path}")
            
            result["success"] = True
            result["file_name"] = file_name
            result["target_path"] = target_path
            result["message"] = f"上传成功：{file_name}"
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 上传失败：{error_msg}")
            result["error"] = error_msg
            result["message"] = f"上传失败：{error_msg}"
        
        return result
    
    def send_reply(self, chat_id: str, message_id: str, content: str):
        """发送回复消息到飞书群"""
        try:
            token = self._get_feishu_token()
            
            url = "https://open.feishu.cn/open-apis/im/v1/messages"
            data = json.dumps({
                "receive_id": chat_id.replace("chat:", ""),
                "msg_type": "text",
                "content": json.dumps({"text": content}),
                "reply_id": message_id
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("code") == 0
                
        except Exception as e:
            print(f"发送回复失败：{e}")
            return False


def handle_event(event_data: Dict) -> Dict:
    """
    处理飞书事件
    
    Args:
        event_data: 完整的事件数据
    
    Returns:
        Dict: 处理结果
    """
    print("=" * 60)
    print("收到飞书事件")
    print("=" * 60)
    
    # 提取关键信息
    header = event_data.get("header", {})
    event = event_data.get("event", {})
    
    print(f"事件类型：{header.get('event_type')}")
    print(f"消息 ID: {event.get('message', {}).get('message_id')}")
    
    # 创建上传器
    uploader = FeishuEventUploader()
    
    # 提取文件信息
    message = event.get("message", {})
    content = message.get("content", "{}")
    
    try:
        content_data = json.loads(content)
    except:
        return {"success": False, "error": "无法解析消息内容"}
    
    file_info = content_data.get("file", {})
    
    if not file_info:
        return {"success": False, "error": "消息中没有文件"}
    
    # 准备上传数据
    upload_data = {
        "message": message,
        "file": file_info
    }
    
    # 执行上传
    result = uploader.upload_file_from_event(upload_data)
    
    # 发送回复
    if result.get("success"):
        chat_id = event.get("message", {}).get("chat_id", "")
        message_id = message.get("message_id")
        reply = f"✅ 已上传到够快云库：{result['target_path']}"
        uploader.send_reply(chat_id, message_id, reply)
    
    return result


def main():
    """主函数 - 用于测试"""
    print("飞书事件订阅文件上传 - 测试模式")
    print("此脚本需要通过飞书事件订阅触发")
    print("")
    print("配置步骤：")
    print("1. 在飞书开发者后台配置事件订阅")
    print("2. 订阅 im:message.group_at_msg 事件")
    print("3. 配置请求网址（需要公网可访问）")
    print("4. 当用户在群里@机器人并发送文件时自动上传")
    
    # 测试够快云库连接
    try:
        uploader = FeishuEventUploader()
        print("\n✅ 配置加载成功")
        print(f"   目标文件夹：{uploader.target_folder}")
        print(f"   够快云库：已连接")
    except Exception as e:
        print(f"\n❌ 配置错误：{e}")


if __name__ == "__main__":
    main()
