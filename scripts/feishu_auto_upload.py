#!/usr/bin/env python3
"""
飞书群文件自动上传到够快云库

功能：
- 监听指定飞书群聊消息
- 自动检测文件附件
- 下载并上传到够快云库指定文件夹
- 记录上传日志

使用方法：
    python scripts/feishu_auto_upload.py

配置：
    编辑 config/feishu_upload.yaml 文件
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


class FeishuUploader:
    """飞书文件上传器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化上传器
        
        Args:
            config_path: 配置文件路径（默认：config/feishu_upload.yaml）
        """
        if config_path is None:
            config_path = project_root / "config" / "feishu_upload.yaml"
        
        self.config = self._load_config(config_path)
        self.goukuai = self._init_goukuai()
        self.target_folder = self.config.get("target_folder", "销售支持")
        self.chat_id = self.config.get("chat_id", "")
        self.log_file = project_root / "logs" / "feishu_upload.log"
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 已处理文件记录（避免重复上传）
        self.processed_files = self._load_processed_files()
    
    def _load_config(self, config_path: Path) -> Dict:
        """加载配置文件"""
        if not config_path.exists():
            # 创建示例配置
            self._create_example_config(config_path)
            raise FileNotFoundError(
                f"配置文件不存在，已创建示例配置：{config_path}\n"
                f"请编辑配置文件后重新运行"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_example_config(self, config_path: Path):
        """创建示例配置文件"""
        example_config = """# 飞书文件自动上传配置

# 飞书配置
feishu:
  # 飞书应用凭证（从飞书开发者后台获取）
  app_id: "cli_xxxxxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxxxxxxxxx"
  
  # 要监听的群聊 ID（从飞书群 URL 或事件 payload 获取）
  # 格式：chat_xxxxxxxxxxxxx
  chat_id: "chat_xxxxxxxxxxxxx"

# 够快云库配置（复用 goukuai.yaml）
goukuai:
  config_file: "config/goukuai.yaml"

# 上传配置
upload:
  # 目标文件夹路径
  target_folder: "销售支持"
  
  # 文件类型过滤（空表示全部上传）
  # 支持扩展名或 MIME 类型
  file_types: []  # ["pdf", "docx", "xlsx", "doc", "xls"]
  
  # 文件大小限制（MB，0 表示无限制）
  max_size_mb: 100
  
  # 是否保留原文件名
  keep_original_name: true
  
  # 文件名前缀（可选，用于分类）
  # name_prefix: "{date}_"  # 例如：2026-03-11_文件名

# 通知配置
notification:
  # 是否在群里发送上传通知
  enabled: true
  
  # 通知模板
  template: "✅ 已上传：{filename} → 够快云库/销售支持/"

# 日志配置
logging:
  # 日志文件路径
  file: "logs/feishu_upload.log"
  
  # 日志级别：DEBUG, INFO, WARNING, ERROR
  level: "INFO"
"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(example_config)
    
    def _init_goukuai(self) -> GoukuaiAdapter:
        """初始化够快云库适配器"""
        goukuai_config = self.config.get("goukuai", {})
        config_file = goukuai_config.get("config_file", "config/goukuai.yaml")
        
        config_path = project_root / config_file
        with open(config_path, 'r', encoding='utf-8') as f:
            goukuai_config = yaml.safe_load(f)
        
        return GoukuaiAdapter(credentials=goukuai_config.get("credentials", {}))
    
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
            json.dump({"files": list(self.processed_files)}, f, indent=2)
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def _get_feishu_token(self) -> str:
        """获取飞书应用访问令牌"""
        feishu_config = self.config.get("feishu", {})
        app_id = feishu_config.get("app_id")
        app_secret = feishu_config.get("app_secret")
        
        if not app_id or not app_secret:
            raise ValueError("飞书 app_id 或 app_secret 未配置")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = json.dumps({
            "app_id": app_id,
            "app_secret": app_secret
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("code") != 0:
                    raise Exception(f"获取令牌失败：{result}")
                return result["tenant_access_token"]
        except urllib.error.HTTPError as e:
            raise Exception(f"飞书 API 请求失败：{e.code} {e.reason}")
    
    def _get_chat_messages(self, token: str, page_token: str = None) -> Dict:
        """获取群聊消息"""
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?container_id={self.chat_id}&message_type=all"
        if page_token:
            url += f"&page_token={page_token}"
        
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise Exception(f"获取消息失败：{e.code} {e.reason}")
    
    def _download_file(self, token: str, file_key: str, save_path: str) -> str:
        """下载飞书文件"""
        url = f"https://open.feishu.cn/open-apis/im/v1/files/{file_key}"
        
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(save_path, 'wb') as f:
                    f.write(response.read())
                return save_path
        except urllib.error.HTTPError as e:
            raise Exception(f"下载文件失败：{e.code} {e.reason}")
    
    def _parse_message_files(self, message: Dict) -> List[Dict]:
        """解析消息中的文件附件"""
        files = []
        
        # 检查消息内容中的文件
        content = message.get("content", "{}")
        try:
            content_data = json.loads(content)
        except:
            return files
        
        # 飞书文件消息类型
        if message.get("message_type") == "file":
            file_info = content_data.get("file", {})
            if file_info:
                files.append({
                    "file_key": file_info.get("file_key"),
                    "file_name": file_info.get("file_name"),
                    "file_size": file_info.get("size"),
                    "message_id": message.get("message_id")
                })
        
        # 检查富文本消息中的附件
        elif message.get("message_type") == "post":
            # post 类型消息可能包含附件引用
            pass
        
        return files
    
    def _should_upload(self, file_info: Dict) -> bool:
        """检查文件是否应该上传"""
        upload_config = self.config.get("upload", {})
        
        # 检查是否已处理
        file_key = file_info.get("file_key", "")
        if file_key in self.processed_files:
            self._log(f"文件已处理，跳过：{file_info.get('file_name')}")
            return False
        
        # 检查文件大小
        max_size = upload_config.get("max_size_mb", 0)
        if max_size > 0:
            file_size = int(file_info.get("file_size", 0))
            if file_size > max_size * 1024 * 1024:
                self._log(f"文件超过大小限制，跳过：{file_info.get('file_name')}")
                return False
        
        # 检查文件类型
        file_types = upload_config.get("file_types", [])
        if file_types:
            file_name = file_info.get("file_name", "").lower()
            ext = file_name.split(".")[-1] if "." in file_name else ""
            if ext not in file_types:
                self._log(f"文件类型不符合，跳过：{file_info.get('file_name')}")
                return False
        
        return True
    
    def _generate_filename(self, original_name: str) -> str:
        """生成上传文件名"""
        upload_config = self.config.get("upload", {})
        
        if upload_config.get("keep_original_name", True):
            return original_name
        
        # 添加前缀
        prefix = upload_config.get("name_prefix", "")
        if prefix:
            date_str = datetime.now().strftime("%Y-%m-%d")
            prefix = prefix.format(date=date_str)
            return f"{prefix}{original_name}"
        
        return original_name
    
    def upload_file(self, file_info: Dict) -> bool:
        """上传单个文件到够快云库"""
        file_key = file_info.get("file_key")
        file_name = file_info.get("file_name")
        message_id = file_info.get("message_id")
        
        self._log(f"开始处理文件：{file_name}")
        
        try:
            # 1. 获取飞书令牌
            token = self._get_feishu_token()
            
            # 2. 下载文件到临时目录
            temp_dir = project_root / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成唯一文件名避免冲突
            unique_name = f"{int(time.time())}_{file_name}"
            temp_path = temp_dir / unique_name
            
            self._log(f"下载文件：{file_name}")
            self._download_file(token, file_key, str(temp_path))
            
            # 3. 读取文件内容
            with open(temp_path, 'rb') as f:
                file_content = f.read()
            
            # 4. 上传到够快云库
            upload_name = self._generate_filename(file_name)
            target_path = f"{self.target_folder}/{upload_name}"
            
            self._log(f"上传到够快云库：{target_path}")
            result = self.goukuai.upload_file(target_path, file_content)
            
            # 5. 记录已处理文件
            self.processed_files.add(file_key)
            self._save_processed_files()
            
            # 6. 清理临时文件
            temp_path.unlink()
            
            self._log(f"✅ 上传成功：{file_name} → {target_path}")
            return True
            
        except Exception as e:
            self._log(f"❌ 上传失败：{file_name} - {str(e)}", "ERROR")
            return False
    
    def process_messages(self) -> Dict:
        """处理群消息中的文件"""
        self._log("=" * 50)
        self._log("开始处理群消息文件")
        
        result = {
            "total_messages": 0,
            "files_found": 0,
            "files_uploaded": 0,
            "files_skipped": 0,
            "errors": []
        }
        
        try:
            # 获取飞书令牌
            token = self._get_feishu_token()
            
            # 获取消息列表
            messages_data = self._get_chat_messages(token)
            messages = messages_data.get("data", {}).get("items", [])
            
            result["total_messages"] = len(messages)
            self._log(f"获取到 {len(messages)} 条消息")
            
            # 处理每条消息
            for msg in messages:
                files = self._parse_message_files(msg)
                
                for file_info in files:
                    result["files_found"] += 1
                    
                    if self._should_upload(file_info):
                        if self.upload_file(file_info):
                            result["files_uploaded"] += 1
                        else:
                            result["errors"].append(file_info.get("file_name"))
                    else:
                        result["files_skipped"] += 1
            
            self._log(f"处理完成：找到 {result['files_found']} 个文件，"
                     f"上传 {result['files_uploaded']} 个，跳过 {result['files_skipped']} 个")
            
        except Exception as e:
            self._log(f"处理异常：{str(e)}", "ERROR")
            result["errors"].append(str(e))
        
        return result


def main():
    """主函数"""
    print("=" * 60)
    print("飞书群文件自动上传工具")
    print("=" * 60)
    
    try:
        uploader = FeishuUploader()
        result = uploader.process_messages()
        
        print("\n" + "=" * 60)
        print("处理结果:")
        print(f"  总消息数：{result['total_messages']}")
        print(f"  找到文件：{result['files_found']}")
        print(f"  上传成功：{result['files_uploaded']}")
        print(f"  跳过：{result['files_skipped']}")
        if result['errors']:
            print(f"  错误：{len(result['errors'])}")
            for err in result['errors']:
                print(f"    - {err}")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n配置错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n运行错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
