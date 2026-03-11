#!/usr/bin/env python3
"""
Cloud Adapter Base Class

所有网盘适配器必须实现的标准接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, BinaryIO
from datetime import datetime


@dataclass
class FileInfo:
    """文件信息"""
    hash: str
    dir: bool
    fullpath: str
    filename: str
    filehash: Optional[str] = None
    filesize: int = 0
    create_member_name: Optional[str] = None
    create_dateline: Optional[int] = None
    last_member_name: Optional[str] = None
    last_dateline: Optional[int] = None
    tag: Optional[str] = None
    permission: Optional[Dict] = None


@dataclass
class FolderInfo:
    """文件夹信息"""
    hash: str
    fullpath: str
    filename: str
    file_count: int = 0
    folder_count: int = 0
    files_size: int = 0


@dataclass
class ShareLink:
    """分享链接信息"""
    link: str
    code: str
    deadline: Optional[int] = None
    password: Optional[str] = None
    auth: str = "preview"


@dataclass
class Permission:
    """权限信息"""
    member_id: Optional[int] = None
    group_id: Optional[int] = None
    account: Optional[str] = None
    permissions: List[str] = None  # ['file_preview', 'file_read', 'file_write', ...]
    role_id: Optional[int] = None


class CloudAdapter(ABC):
    """
    网盘适配器基类
    
    所有网盘适配器必须实现的标准接口
    """
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            credentials: 认证信息
        """
        self.credentials = credentials
        self.current_user_id: Optional[str] = None
        self.current_user_account: Optional[str] = None
    
    # ========== 认证方法 ==========
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        验证认证信息
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def get_library_info(self) -> Dict[str, Any]:
        """
        获取文件库信息
        
        Returns:
            dict: 库信息
        """
        pass
    
    # ========== 用户上下文 ==========
    
    def set_user_context(self, user_id: Optional[str] = None, account: Optional[str] = None):
        """
        设置当前操作用户上下文（用于权限检查）
        
        Args:
            user_id: 用户 ID
            account: 用户账号
        """
        self.current_user_id = user_id
        self.current_user_account = account
    
    # ========== 文件操作 ==========
    
    @abstractmethod
    def list_files(self, fullpath: str = "", tag: Optional[str] = None, 
                   start: int = 0, size: int = 100) -> List[FileInfo]:
        """
        列出文件夹内容
        
        Args:
            fullpath: 文件夹路径
            tag: 按标签筛选
            start: 开始位置
            size: 返回数量
        
        Returns:
            List[FileInfo]: 文件列表
        """
        pass
    
    @abstractmethod
    def search_files(self, keywords: str, path: str = "", 
                     scope: List[str] = None, start: int = 0, size: int = 100) -> List[FileInfo]:
        """
        搜索文件
        
        Args:
            keywords: 搜索关键字
            path: 搜索范围（文件夹路径）
            scope: 搜索范围 ['filename', 'tag', 'content']
            start: 开始位置
            size: 返回数量
        
        Returns:
            List[FileInfo]: 文件列表
        """
        pass
    
    @abstractmethod
    def download_file(self, file_hash: str = None, fullpath: str = None, 
                      open_browser: bool = False) -> bytes:
        """
        下载文件
        
        Args:
            file_hash: 文件唯一标识
            fullpath: 文件路径
            open_browser: 是否返回浏览器可打开的链接
        
        Returns:
            bytes: 文件内容
        """
        pass
    
    @abstractmethod
    def upload_file(self, fullpath: str, content: bytes, 
                    overwrite: bool = False) -> FileInfo:
        """
        上传文件
        
        Args:
            fullpath: 文件完整路径
            content: 文件内容
            overwrite: 是否覆盖同名文件
        
        Returns:
            FileInfo: 上传后的文件信息
        """
        pass
    
    @abstractmethod
    def get_file_content(self, file_hash: str = None, fullpath: str = None) -> str:
        """
        获取文件文本内容（提取 PDF/Word/Excel 文本）
        
        Args:
            file_hash: 文件唯一标识
            fullpath: 文件路径
        
        Returns:
            str: 文本内容
        """
        pass
    
    @abstractmethod
    def get_file_info(self, file_hash: str = None, fullpath: str = None, 
                      attribute: bool = False) -> FileInfo:
        """
        获取文件（夹）信息
        
        Args:
            file_hash: 文件唯一标识
            fullpath: 文件路径
            attribute: 是否获取额外属性
        
        Returns:
            FileInfo: 文件信息
        """
        pass
    
    @abstractmethod
    def copy_file(self, from_fullpath: str, to_fullpath: str, 
                  overwrite: bool = False) -> FileInfo:
        """
        复制文件（夹）
        
        Args:
            from_fullpath: 源路径
            to_fullpath: 目标路径
            overwrite: 是否覆盖
        
        Returns:
            FileInfo: 复制后的文件信息
        """
        pass
    
    @abstractmethod
    def move_file(self, from_fullpath: str, to_fullpath: str) -> bool:
        """
        移动文件（夹）
        
        Args:
            from_fullpath: 源路径
            to_fullpath: 目标路径
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def delete_file(self, fullpath: str = None, tag: str = None, 
                    destroy: bool = False) -> bool:
        """
        删除文件（夹）
        
        Args:
            fullpath: 文件路径
            tag: 按标签删除
            destroy: 是否彻底删除（不进回收站）
        
        Returns:
            bool: 是否成功
        """
        pass
    
    # ========== 文件夹操作 ==========
    
    @abstractmethod
    def create_folder(self, fullpath: str) -> FolderInfo:
        """
        创建文件夹
        
        Args:
            fullpath: 文件夹完整路径
        
        Returns:
            FolderInfo: 文件夹信息
        """
        pass
    
    # ========== 权限管理 ==========
    
    @abstractmethod
    def get_permission(self, fullpath: str, member_id: str = None) -> List[Permission]:
        """
        获取文件权限
        
        Args:
            fullpath: 文件路径
            member_id: 指定用户（可选）
        
        Returns:
            List[Permission]: 权限列表
        """
        pass
    
    @abstractmethod
    def set_permission(self, fullpath: str, permissions: Dict) -> bool:
        """
        设置文件权限
        
        Args:
            fullpath: 文件路径
            permissions: 权限配置
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def set_permission_inherit(self, fullpath: str, inherit: bool, 
                                keep: bool = False) -> bool:
        """
        设置权限继承
        
        Args:
            fullpath: 文件路径
            inherit: 是否继承
            keep: 是否保留并合并上级权限
        
        Returns:
            bool: 是否成功
        """
        pass
    
    # ========== 分享协作 ==========
    
    @abstractmethod
    def create_share_link(self, fullpath: str, deadline: int = None, 
                          password: str = None, auth: str = "preview",
                          dir: bool = False) -> ShareLink:
        """
        创建分享链接
        
        Args:
            fullpath: 文件路径
            deadline: 到期时间戳
            password: 访问密码
            auth: 权限类型（preview/download/upload）
            dir: 是否文件夹
        
        Returns:
            ShareLink: 分享链接信息
        """
        pass
    
    @abstractmethod
    def close_share_link(self, code: str = None, fullpath: str = None) -> bool:
        """
        关闭分享链接
        
        Args:
            code: 外链码
            fullpath: 文件路径
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def get_cedit_url(self, file_hash: str = None, fullpath: str = None,
                      readonly: bool = False, timeout: int = 3600,
                      op_id: str = None) -> str:
        """
        获取协同编辑链接
        
        Args:
            file_hash: 文件唯一标识
            fullpath: 文件路径
            readonly: 是否只读
            timeout: 过期时间（秒）
            op_id: 操作人 ID
        
        Returns:
            str: 编辑链接
        """
        pass
    
    # ========== 版本管理 ==========
    
    @abstractmethod
    def get_history(self, fullpath: str, start: int = 0, size: int = 20) -> List[Dict]:
        """
        获取文件历史版本
        
        Args:
            fullpath: 文件路径
            start: 开始位置
            size: 返回数量
        
        Returns:
            List[Dict]: 历史版本列表
        """
        pass
    
    @abstractmethod
    def recover_version(self, hid: str) -> bool:
        """
        恢复历史版本
        
        Args:
            hid: 版本 ID
        
        Returns:
            bool: 是否成功
        """
        pass
    
    # ========== 标签管理 ==========
    
    @abstractmethod
    def add_tag(self, fullpath: str, tag: str) -> bool:
        """
        添加标签
        
        Args:
            fullpath: 文件路径
            tag: 标签（多个用分号分隔）
        
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def del_tag(self, fullpath: str, tag: str) -> bool:
        """
        删除标签
        
        Args:
            fullpath: 文件路径
            tag: 标签
        
        Returns:
            bool: 是否成功
        """
        pass
    
    # ========== 统计信息 ==========
    
    @abstractmethod
    def get_library_stat(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        pass
    
    # ========== AI 增强方法（可选实现） ==========
    
    def summarize_file(self, fullpath: str) -> str:
        """
        摘要文件内容
        
        Args:
            fullpath: 文件路径
        
        Returns:
            str: 摘要
        """
        raise NotImplementedError("当前适配器不支持文档摘要")
    
    def ask_file(self, fullpath: str, question: str) -> str:
        """
        基于文件内容问答
        
        Args:
            fullpath: 文件路径
            question: 问题
        
        Returns:
            str: 答案
        """
        raise NotImplementedError("当前适配器不支持文档问答")
    
    # ========== 工具方法 ==========
    
    def _check_permission(self, fullpath: str, required_permission: str) -> bool:
        """
        检查当前用户是否有指定权限
        
        Args:
            fullpath: 文件路径
            required_permission: 需要的权限
        
        Returns:
            bool: 是否有权限
        """
        if not self.current_user_id and not self.current_user_account:
            return True  # 未设置用户上下文，跳过检查
        
        permissions = self.get_permission(fullpath)
        # 具体实现由子类完成
        return True
    
    def _format_timestamp(self, dt: datetime = None) -> int:
        """
        获取 Unix 时间戳（秒）
        
        Args:
            dt: 日期时间
        
        Returns:
            int: 时间戳
        """
        if dt is None:
            dt = datetime.now()
        return int(dt.timestamp())
