#!/usr/bin/env python3
"""
自动分类整理引擎

基于 AI 和规则的文件自动分类
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SortStrategy(Enum):
    """分类策略"""
    BY_TYPE = "type"           # 按文件类型
    BY_DATE = "date"           # 按日期
    BY_KEYWORD = "keyword"     # 按关键词
    BY_AI = "ai"              # AI 智能分类


@dataclass
class SortRule:
    """分类规则"""
    name: str
    pattern: str              # 匹配模式（支持通配符）
    target_folder: str        # 目标文件夹
    priority: int = 0         # 优先级（数字越大优先级越高）


@dataclass
class SortResult:
    """分类结果"""
    file_hash: str
    file_name: str
    original_path: str
    target_path: str
    strategy: SortStrategy
    confidence: float         # 置信度 0-1
    success: bool
    error: Optional[str] = None


class AutoSorter:
    """
    自动分类整理引擎
    """
    
    # 默认文件类型映射
    TYPE_MAPPING = {
        "合同": ["*合同*", "*协议*", "*contract*", "*agreement*"],
        "财务": ["*财务*", "*会计*", "*发票*", "*报销*", "*budget*", "*invoice*"],
        "人事": ["*人事*", "*招聘*", "*薪资*", "*hr*", "*salary*"],
        "技术": ["*技术*", "*开发*", "*代码*", "*api*", "*tech*", "*dev*"],
        "市场": ["*市场*", "*营销*", "*推广*", "*marketing*", "*sales*"],
        "行政": ["*行政*", "*通知*", "*公告*", "*admin*", "*notice*"],
        "法律": ["*法律*", "*法务*", "*合规*", "*legal*", "*compliance*"],
        "产品": ["*产品*", "*需求*", "*prd*", "*product*"],
        "设计": ["*设计*", "*ui*", "*ux*", "*design*", "*psd*", "*ai*"],
        "其他": ["*"]
    }
    
    # 文件扩展名映射
    EXT_MAPPING = {
        "文档": [".doc", ".docx", ".pdf", ".txt", ".md"],
        "表格": [".xls", ".xlsx", ".csv"],
        "演示": [".ppt", ".pptx", ".key"],
        "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "视频": [".mp4", ".avi", ".mov", ".wmv"],
        "音频": [".mp3", ".wav", ".aac"],
        "代码": [".py", ".js", ".java", ".cpp", ".go", ".rs"],
        "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"]
    }
    
    def __init__(self, adapter):
        """
        初始化分类器
        
        Args:
            adapter: 网盘适配器实例
        """
        self.adapter = adapter
        self.rules: List[SortRule] = []
        self.custom_mapping: Dict[str, List[str]] = {}
    
    def add_rule(self, name: str, pattern: str, 
                 target_folder: str, priority: int = 0):
        """
        添加分类规则
        
        Args:
            name: 规则名称
            pattern: 匹配模式（支持 * 通配符）
            target_folder: 目标文件夹路径
            priority: 优先级
        """
        rule = SortRule(
            name=name,
            pattern=pattern,
            target_folder=target_folder,
            priority=priority
        )
        self.rules.append(rule)
        
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def clear_rules(self):
        """清除所有规则"""
        self.rules.clear()
    
    def add_type_mapping(self, category: str, patterns: List[str]):
        """
        添加自定义类型映射
        
        Args:
            category: 分类名称
            patterns: 匹配模式列表
        """
        self.custom_mapping[category] = patterns
    
    def classify_by_name(self, filename: str) -> Tuple[str, float]:
        """
        根据文件名分类
        
        Args:
            filename: 文件名
        
        Returns:
            Tuple[str, float]: (分类名称，置信度)
        """
        import fnmatch
        
        # 检查自定义规则
        for rule in self.rules:
            if fnmatch.fnmatch(filename.lower(), rule.pattern.lower()):
                return (rule.name, 0.9)
        
        # 检查类型映射
        mapping = {**self.TYPE_MAPPING, **self.custom_mapping}
        
        for category, patterns in mapping.items():
            for pattern in patterns:
                if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    # 计算置信度
                    if pattern == "*":
                        confidence = 0.3
                    elif pattern.startswith("*") and pattern.endswith("*"):
                        confidence = 0.6
                    else:
                        confidence = 0.8
                    
                    return (category, confidence)
        
        return ("其他", 0.5)
    
    def classify_by_content(self, fullpath: str) -> Tuple[str, float]:
        """
        根据文件内容分类
        
        Args:
            fullpath: 文件路径
        
        Returns:
            Tuple[str, float]: (分类名称，置信度)
        """
        # 获取文件内容
        try:
            content = self.adapter.get_file_content(fullpath=fullpath)
        except Exception:
            return ("其他", 0.3)
        
        # 简单关键词匹配
        keywords = {
            "合同": ["合同", "协议", "签署", "甲方", "乙方"],
            "财务": ["发票", "报销", "预算", "决算", "收入", "支出"],
            "人事": ["招聘", "面试", "薪资", "绩效", "考勤"],
            "技术": ["代码", "接口", "API", "开发", "技术"],
            "市场": ["市场", "营销", "推广", "客户", "销售"],
        }
        
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in content)
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return ("其他", 0.3)
        
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 10, 0.9)
        
        return (best_category, confidence)
    
    def classify_by_extension(self, filename: str) -> Tuple[str, float]:
        """
        根据扩展名分类
        
        Args:
            filename: 文件名
        
        Returns:
            Tuple[str, float]: (分类名称，置信度)
        """
        import os
        ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in self.EXT_MAPPING.items():
            if ext in extensions:
                return (category, 0.95)
        
        return ("其他", 0.5)
    
    def classify(self, fullpath: str, strategy: SortStrategy = SortStrategy.BY_KEYWORD) -> Tuple[str, float]:
        """
        分类文件
        
        Args:
            fullpath: 文件路径
            strategy: 分类策略
        
        Returns:
            Tuple[str, float]: (分类名称，置信度)
        """
        filename = fullpath.split("/")[-1]
        
        if strategy == SortStrategy.BY_TYPE:
            return self.classify_by_extension(filename)
        elif strategy == SortStrategy.BY_KEYWORD:
            return self.classify_by_name(filename)
        elif strategy == SortStrategy.BY_AI:
            # 组合多种策略
            name_result = self.classify_by_name(filename)
            content_result = self.classify_by_content(fullpath)
            
            # 选择置信度高的
            if name_result[1] >= content_result[1]:
                return name_result
            else:
                return content_result
        else:
            return self.classify_by_name(filename)
    
    def get_target_folder(self, fullpath: str, category: str,
                          base_folder: str = "/") -> str:
        """
        获取目标文件夹路径
        
        Args:
            fullpath: 文件路径
            category: 分类名称
            base_folder: 基础文件夹
        
        Returns:
            str: 目标文件夹路径
        """
        filename = fullpath.split("/")[-1]
        return f"{base_folder}/{category}/{filename}"
    
    def sort_file(self, fullpath: str, strategy: SortStrategy = SortStrategy.BY_KEYWORD,
                  base_folder: str = "/", create_folder: bool = True,
                  move: bool = True) -> SortResult:
        """
        整理单个文件
        
        Args:
            fullpath: 文件路径
            strategy: 分类策略
            base_folder: 基础文件夹
            create_folder: 是否创建目标文件夹
            move: 是否移动（否则返回目标路径）
        
        Returns:
            SortResult: 整理结果
        """
        filename = fullpath.split("/")[-1]
        
        # 分类
        category, confidence = self.classify(fullpath, strategy)
        
        # 获取目标路径
        target_folder = f"{base_folder}/{category}"
        target_path = f"{target_folder}/{filename}"
        
        # 创建目标文件夹
        if create_folder:
            try:
                self.adapter.create_folder(target_folder)
            except Exception:
                pass  # 文件夹可能已存在
        
        # 移动文件
        if move:
            try:
                self.adapter.move_file(fullpath, target_path)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
        else:
            success = True
            error = None
        
        return SortResult(
            file_hash="",
            file_name=filename,
            original_path=fullpath,
            target_path=target_path,
            strategy=strategy,
            confidence=confidence,
            success=success,
            error=error
        )
    
    def sort_folder(self, folder_path: str, strategy: SortStrategy = SortStrategy.BY_KEYWORD,
                    base_folder: str = "/", recursive: bool = False,
                    dry_run: bool = False) -> List[SortResult]:
        """
        整理整个文件夹
        
        Args:
            folder_path: 文件夹路径
            strategy: 分类策略
            base_folder: 基础文件夹
            recursive: 是否递归处理子文件夹
            dry_run: 是否仅预览（不实际移动）
        
        Returns:
            List[SortResult]: 整理结果列表
        """
        results = []
        
        # 获取文件列表
        files = self.adapter.list_files(fullpath=folder_path)
        
        for file_info in files:
            if file_info.dir:
                # 子文件夹
                if recursive:
                    sub_results = self.sort_folder(
                        file_info.fullpath,
                        strategy,
                        base_folder,
                        recursive=True,
                        dry_run=dry_run
                    )
                    results.extend(sub_results)
            else:
                # 文件
                if dry_run:
                    # 预览模式
                    category, confidence = self.classify(file_info.fullpath, strategy)
                    target_path = f"{base_folder}/{category}/{file_info.filename}"
                    
                    results.append(SortResult(
                        file_hash=file_info.hash,
                        file_name=file_info.filename,
                        original_path=file_info.fullpath,
                        target_path=target_path,
                        strategy=strategy,
                        confidence=confidence,
                        success=True
                    ))
                else:
                    # 实际整理
                    result = self.sort_file(
                        file_info.fullpath,
                        strategy,
                        base_folder,
                        create_folder=True,
                        move=True
                    )
                    results.append(result)
        
        return results
    
    def get_suggestions(self, folder_path: str) -> Dict[str, Any]:
        """
        获取整理建议
        
        Args:
            folder_path: 文件夹路径
        
        Returns:
            Dict: 整理建议
        """
        files = self.adapter.list_files(fullpath=folder_path)
        
        # 统计分类
        categories = {}
        for file_info in files:
            if not file_info.dir:
                category, _ = self.classify(file_info.fullpath)
                if category not in categories:
                    categories[category] = []
                categories[category].append(file_info.filename)
        
        # 生成建议
        suggestions = {
            "total_files": len(files),
            "categories": categories,
            "recommendations": []
        }
        
        for category, files in categories.items():
            if len(files) >= 3:  # 超过 3 个文件建议创建文件夹
                suggestions["recommendations"].append({
                    "action": "create_folder",
                    "category": category,
                    "file_count": len(files),
                    "files": files[:5],  # 只显示前 5 个
                    "suggested_path": f"{folder_path}/{category}"
                })
        
        return suggestions
