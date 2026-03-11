#!/usr/bin/env python3
"""
OpenClaw 集成版本 - 飞书群文件自动上传

此脚本设计为：
1. 可通过 OpenClaw 心跳定时运行
2. 可作为独立脚本手动触发
3. 支持通过飞书 webhook 实时触发

使用方法：
    # 手动运行
    python scripts/openclaw_feishu_upload.py
    
    # 作为 OpenClaw 心跳任务
    在 HEARTBEAT.md 中添加定时任务
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

import yaml
from adapters.goukuai import GoukuaiAdapter


class OpenClawFeishuUploader:
    """OpenClaw 集成的飞书文件上传器"""
    
    def __init__(self, chat_id: str = None, target_folder: str = "销售支持"):
        """
        初始化上传器
        
        Args:
            chat_id: 飞书群聊 ID（可选，默认从配置读取）
            target_folder: 够快云库目标文件夹
        """
        self.chat_id = chat_id or "chat:oc_8866d74caa0813e3763ab71f8f0dd272"
        self.target_folder = target_folder
        self.log_messages = []
        
        # 加载够快云库配置
        config_path = project_root / "config" / "goukuai.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            goukuai_config = yaml.safe_load(f)
        
        self.goukuai = GoukuaiAdapter(credentials=goukuai_config.get("credentials", {}))
        
        # 已处理文件记录
        self.processed_files = self._load_processed_files()
        
        # 飞书凭证（从环境变量读取，更安全）
        self.feishu_app_id = os.environ.get("FEISHU_APP_ID")
        self.feishu_app_secret = os.environ.get("FEISHU_APP_SECRET")
    
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
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def _get_feishu_token(self) -> str:
        """获取飞书应用访问令牌"""
        if not self.feishu_app_id or not self.feishu_app_secret:
            # 尝试从配置文件读取
            config_path = project_root / "config" / "feishu_upload.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    feishu_config = config.get("feishu", {})
                    self.feishu_app_id = feishu_config.get("app_id")
                    self.feishu_app_secret = feishu_config.get("app_secret")
        
        if not self.feishu_app_id or not self.feishu_app_secret:
            raise ValueError("飞书 app_id 或 app_secret 未配置（请设置环境变量 FEISHU_APP_ID/FEISHU_APP_SECRET）")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = json.dumps({
            "app_id": self.feishu_app_id,
            "app_secret": self.feishu_app_secret
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") != 0:
                raise Exception(f"获取令牌失败：{result}")
            return result["tenant_access_token"]
    
    def _get_chat_messages(self, token: str, container_id: str, page_token: str = None) -> Dict:
        """获取群聊消息"""
        # 去掉 chat: 前缀，使用纯 ID
        chat_id = container_id.replace("chat:", "")
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?container_id={chat_id}&container_id_type=chat_id&container_type=group&order=desc"
        if page_token:
            url += f"&page_token={page_token}"
        
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    
    def _download_file(self, token: str, file_key: str) -> bytes:
        """下载飞书文件"""
        url = f"https://open.feishu.cn/open-apis/im/v1/files/{file_key}"
        
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    
    def _parse_message_files(self, message: Dict) -> List[Dict]:
        """解析消息中的文件附件"""
        files = []
        
        # 检查消息类型
        msg_type = message.get("message_type")
        content = message.get("content", "{}")
        
        try:
            content_data = json.loads(content)
        except:
            return files
        
        # 文件消息类型
        if msg_type == "file":
            file_info = content_data.get("file", {})
            if file_info and file_info.get("file_key"):
                files.append({
                    "file_key": file_info.get("file_key"),
                    "file_name": file_info.get("file_name"),
                    "file_size": file_info.get("size", 0),
                    "message_id": message.get("message_id"),
                    "sender_id": message.get("sender_id"),
                    "create_time": message.get("create_time")
                })
        
        return files
    
    def _should_upload(self, file_info: Dict) -> tuple:
        """检查文件是否应该上传"""
        file_key = file_info.get("file_key", "")
        
        # 检查是否已处理
        if file_key in self.processed_files:
            return False, "已处理"
        
        # 检查文件大小（100MB 限制）
        file_size = int(file_info.get("file_size", 0))
        if file_size > 100 * 1024 * 1024:
            return False, "文件过大"
        
        return True, "OK"
    
    def upload_file(self, file_info: Dict) -> Dict:
        """上传单个文件到够快云库"""
        file_key = file_info.get("file_key")
        file_name = file_info.get("file_name", "unknown")
        message_id = file_info.get("message_id")
        
        self._log(f"📥 开始处理：{file_name}")
        
        result = {
            "success": False,
            "file_name": file_name,
            "message_id": message_id,
            "error": None
        }
        
        try:
            # 1. 获取飞书令牌
            token = self._get_feishu_token()
            
            # 2. 下载文件
            self._log(f"⬇️ 下载中：{file_name}")
            file_content = self._download_file(token, file_key)
            
            # 3. 生成唯一文件名（避免覆盖）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_parts = file_name.rsplit('.', 1)
            if len(name_parts) > 1:
                unique_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                unique_name = f"{file_name}_{timestamp}"
            
            # 4. 上传到够快云库
            target_path = f"{self.target_folder}/{unique_name}"
            self._log(f"⬆️ 上传中：{target_path}")
            
            upload_result = self.goukuai.upload_file(target_path, file_content)
            
            # 5. 记录已处理文件
            self.processed_files.add(file_key)
            self._save_processed_files()
            
            self._log(f"✅ 上传成功：{file_name} → {target_path}")
            
            result["success"] = True
            result["target_path"] = target_path
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"❌ 上传失败：{file_name} - {error_msg}")
            result["error"] = error_msg
        
        return result
    
    def process_new_files(self, limit: int = 50) -> Dict:
        """处理群聊中的新文件"""
        self._log("=" * 50)
        self._log("开始扫描群聊文件")
        
        result = {
            "total_messages": 0,
            "files_found": 0,
            "files_uploaded": 0,
            "files_skipped": 0,
            "upload_results": [],
            "errors": []
        }
        
        try:
            # 获取飞书令牌
            token = self._get_feishu_token()
            
            # 获取消息列表（最新的 limit 条）
            messages_data = self._get_chat_messages(token, self.chat_id)
            messages = messages_data.get("data", {}).get("items", [])
            
            result["total_messages"] = len(messages)
            self._log(f"📨 获取到 {len(messages)} 条消息")
            
            # 处理每条消息
            for msg in messages:
                files = self._parse_message_files(msg)
                
                for file_info in files:
                    result["files_found"] += 1
                    
                    should_upload, reason = self._should_upload(file_info)
                    
                    if should_upload:
                        upload_result = self.upload_file(file_info)
                        result["upload_results"].append(upload_result)
                        
                        if upload_result["success"]:
                            result["files_uploaded"] += 1
                        else:
                            result["errors"].append(upload_result.get("error"))
                    else:
                        self._log(f"⏭️ 跳过：{file_info.get('file_name')} ({reason})")
                        result["files_skipped"] += 1
            
            summary = f"扫描完成：{result['files_found']} 个文件，上传 {result['files_uploaded']} 个，跳过 {result['files_skipped']} 个"
            self._log(summary)
            result["summary"] = summary
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"❌ 处理异常：{error_msg}")
            result["errors"].append(error_msg)
        
        return result
    
    def get_summary_report(self, result: Dict) -> str:
        """生成汇总报告（用于飞书消息）"""
        lines = ["📁 文件上传报告", ""]
        
        if result.get("summary"):
            lines.append(result["summary"])
            lines.append("")
        
        if result.get("files_uploaded", 0) > 0:
            lines.append("✅ 成功上传:")
            for r in result.get("upload_results", []):
                if r.get("success"):
                    lines.append(f"  • {r.get('file_name')} → {r.get('target_path')}")
            lines.append("")
        
        if result.get("errors"):
            lines.append("❌ 失败:")
            for err in result["errors"]:
                lines.append(f"  • {err}")
        
        return "\n".join(lines)


def main():
    """主函数 - 可被 OpenClaw 调用"""
    print("=" * 60)
    print("OpenClaw - 飞书群文件自动上传")
    print("=" * 60)
    
    try:
        uploader = OpenClawFeishuUploader()
        result = uploader.process_new_files()
        
        print("\n" + "=" * 60)
        print("处理结果:")
        print(f"  总消息数：{result['total_messages']}")
        print(f"  找到文件：{result['files_found']}")
        print(f"  上传成功：{result['files_uploaded']}")
        print(f"  跳过：{result['files_skipped']}")
        
        if result.get('upload_results'):
            print("\n上传详情:")
            for r in result['upload_results']:
                status = "✅" if r.get('success') else "❌"
                print(f"  {status} {r.get('file_name')}")
                if r.get('target_path'):
                    print(f"     → {r.get('target_path')}")
                if r.get('error'):
                    print(f"     错误：{r.get('error')}")
        
        print("=" * 60)
        
        # 返回结果供 OpenClaw 使用
        return result
        
    except Exception as e:
        print(f"\n❌ 运行错误：{e}")
        return {"error": str(e)}


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("files_uploaded", 0) >= 0 else 1)
