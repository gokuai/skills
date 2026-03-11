#!/usr/bin/env python3
"""
权限检查器

实现企业级权限验证和访问控制
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PermissionLevel(Enum):
    """权限级别"""
    OWNER = "owner"          # 拥有者
    ADMIN = "admin"          # 管理员
    EDITOR = "editor"        # 编辑者
    VIEWER = "viewer"        # 查看者
    GUEST = "guest"          # 访客


@dataclass
class PermissionContext:
    """权限上下文"""
    user_id: Optional[str] = None
    account: Optional[str] = None
    member_id: Optional[int] = None
    group_ids: List[int] = None
    roles: List[str] = None
    
    def __post_init__(self):
        if self.group_ids is None:
            self.group_ids = []
        if self.roles is None:
            self.roles = []


class PermissionChecker:
    """
    权限检查器
    
    验证用户对文件的访问权限
    """
    
    # 权限映射表
    PERMISSION_MAP = {
        # 基础权限
        "file_preview": PermissionLevel.VIEWER,
        "file_read": PermissionLevel.VIEWER,
        "file_download": PermissionLevel.VIEWER,
        
        # 编辑权限
        "file_write": PermissionLevel.EDITOR,
        "file_edit": PermissionLevel.EDITOR,
        "file_upload": PermissionLevel.EDITOR,
        
        # 管理权限
        "file_delete": PermissionLevel.ADMIN,
        "file_share": PermissionLevel.EDITOR,
        "file_link": PermissionLevel.EDITOR,
        "file_permission": PermissionLevel.ADMIN,
        
        # 特殊权限
        "file_lock": PermissionLevel.EDITOR,
        "file_version": PermissionLevel.EDITOR,
        "file_comment": PermissionLevel.VIEWER,
    }
    
    def __init__(self, adapter):
        """
        初始化权限检查器
        
        Args:
            adapter: 网盘适配器实例
        """
        self.adapter = adapter
        self.permission_cache = {}
    
    def check_access(self, fullpath: str, context: PermissionContext) -> bool:
        """
        检查是否有权访问文件
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            bool: 是否有访问权限
        """
        try:
            permissions = self._get_permissions(fullpath, context)
            return len(permissions) > 0
        except Exception:
            return False
    
    def check_edit(self, fullpath: str, context: PermissionContext) -> bool:
        """
        检查是否有权编辑文件
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            bool: 是否有编辑权限
        """
        try:
            permissions = self._get_permissions(fullpath, context)
            
            # 检查是否有编辑相关权限
            edit_permissions = ["file_write", "file_edit", "file_upload"]
            return any(p in permissions for p in edit_permissions)
        except Exception:
            return False
    
    def check_delete(self, fullpath: str, context: PermissionContext) -> bool:
        """
        检查是否有权删除文件
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            bool: 是否有删除权限
        """
        try:
            permissions = self._get_permissions(fullpath, context)
            return "file_delete" in permissions
        except Exception:
            return False
    
    def check_share(self, fullpath: str, context: PermissionContext) -> bool:
        """
        检查是否有权分享文件
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            bool: 是否有分享权限
        """
        try:
            permissions = self._get_permissions(fullpath, context)
            return "file_link" in permissions or "file_share" in permissions
        except Exception:
            return False
    
    def get_permission_level(self, fullpath: str, context: PermissionContext) -> PermissionLevel:
        """
        获取用户对文件的权限级别
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            PermissionLevel: 权限级别
        """
        try:
            permissions = self._get_permissions(fullpath, context)
            
            if not permissions:
                return PermissionLevel.GUEST
            
            # 检查最高权限
            if "file_delete" in permissions or "file_permission" in permissions:
                return PermissionLevel.ADMIN
            elif "file_write" in permissions or "file_edit" in permissions:
                return PermissionLevel.EDITOR
            elif "file_read" in permissions or "file_preview" in permissions:
                return PermissionLevel.VIEWER
            else:
                return PermissionLevel.GUEST
        except Exception:
            return PermissionLevel.GUEST
    
    def can_grant_permission(self, user_context: PermissionContext, 
                             target_permission: PermissionLevel) -> bool:
        """
        检查用户是否有权授予指定权限
        
        Args:
            user_context: 用户权限上下文
            target_permission: 目标权限级别
        
        Returns:
            bool: 是否有权授予
        """
        # 只能授予比自己低的权限
        user_level = self.get_permission_level("", user_context)
        
        level_order = [
            PermissionLevel.GUEST,
            PermissionLevel.VIEWER,
            PermissionLevel.EDITOR,
            PermissionLevel.ADMIN,
            PermissionLevel.OWNER
        ]
        
        user_index = level_order.index(user_level)
        target_index = level_order.index(target_permission)
        
        return user_index > target_index
    
    def _get_permissions(self, fullpath: str, context: PermissionContext) -> List[str]:
        """
        获取用户对文件的权限列表
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
        
        Returns:
            List[str]: 权限列表
        """
        cache_key = f"{fullpath}:{context.user_id}:{context.account}"
        
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        # 获取文件权限
        permissions_data = self.adapter.get_permission(fullpath)
        
        user_permissions = set()
        
        # 检查用户直接权限
        if context.member_id:
            for perm in permissions_data:
                if perm.member_id == context.member_id:
                    user_permissions.update(perm.permissions)
        
        # 检查部门权限
        for group_id in context.group_ids:
            for perm in permissions_data:
                if perm.group_id == group_id:
                    user_permissions.update(perm.permissions)
        
        # 缓存结果
        permissions_list = list(user_permissions)
        self.permission_cache[cache_key] = permissions_list
        
        return permissions_list
    
    def clear_cache(self):
        """清除权限缓存"""
        self.permission_cache.clear()
    
    def validate_operation(self, fullpath: str, context: PermissionContext,
                           operation: str) -> bool:
        """
        验证用户是否有权执行指定操作
        
        Args:
            fullpath: 文件路径
            context: 权限上下文
            operation: 操作类型（preview/download/edit/delete/share）
        
        Returns:
            bool: 是否有权执行
        """
        operation_map = {
            "preview": ["file_preview"],
            "download": ["file_read", "file_download"],
            "edit": ["file_write", "file_edit"],
            "delete": ["file_delete"],
            "share": ["file_link", "file_share"],
            "upload": ["file_upload"],
            "permission": ["file_permission"]
        }
        
        required_permissions = operation_map.get(operation, [])
        
        if not required_permissions:
            return True
        
        try:
            permissions = self._get_permissions(fullpath, context)
            return any(p in permissions for p in required_permissions)
        except Exception:
            return False
