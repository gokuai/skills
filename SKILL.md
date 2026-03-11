---
name: goukuai-connector
description: 够快云库企业网盘连接器。提供文件管理（搜索/上传/下载/移动/复制/删除）、文件夹整理、权限管理、协作分享、AI 增强（文档摘要/问答/智能分类）等能力。适用于企业知识库管理、文档自动化、团队协作场景。
---

# 够快云库连接器 Skill

企业级网盘 AI 连接器，让 AI 能够安全、高效地操作够快云库中的文件。

## 🎯 使用场景

- **企业知识库管理** - 自动整理、分类、归档文档
- **团队协作** - 文件分享、权限管理、协同编辑
- **文档自动化** - 批量处理、模板填充、报告生成
- **智能检索** - 语义搜索、文档问答、内容摘要
- **安全合规** - 权限控制、审计日志、敏感文件保护

## 🚀 快速开始

### 1. 配置认证信息

```bash
# 企业级认证（推荐）
export GOUKUAI_CLIENT_ID="your_client_id"
export GOUKUAI_CLIENT_SECRET="your_client_secret"

# 库级认证（操作特定文件库）
export GOUKUAI_ORG_CLIENT_ID="your_org_client_id"
export GOUKUAI_ORG_CLIENT_SECRET="your_org_client_secret"

# API 域名
export GOUKUAI_API_HOST="yk3.gokuai.com"
```

### 2. 初始化连接

```python
from adapters.goukuai import GoukuaiAdapter

# 初始化适配器
adapter = GoukuaiAdapter(
    client_id=os.environ["GOUKUAI_CLIENT_ID"],
    client_secret=os.environ["GOUKUAI_CLIENT_SECRET"],
    org_client_id=os.environ.get("GOUKUAI_ORG_CLIENT_ID"),
    org_client_secret=os.environ.get("GOUKUAI_ORG_CLIENT_SECRET")
)

# 测试连接
info = adapter.get_library_info()
print(f"连接成功：{info['org_name']}")
```

### 3. 基本操作示例

```python
# 搜索文件
files = adapter.search_files("合同")

# 下载文件
content = adapter.download_file(hash="file_hash_123")

# 上传文件
result = adapter.upload_file("/docs/report.pdf", file_content)

# 创建文件夹
adapter.create_folder("/2026/Q1")

# 移动文件
adapter.move_file("/old/report.pdf", "/2026/Q1/report.pdf")

# 获取文件权限
permissions = adapter.get_permission("/docs/contract.docx")

# 文档摘要
summary = adapter.summarize_file("/docs/report.pdf")

# 文档问答
answer = adapter.ask_file("/docs/policy.pdf", "报销流程是什么？")
```

## 📁 目录结构

```
goukuai-connector/
├── SKILL.md                        # 本文件
├── README.md                       # 人类可读文档
├── LICENSE                         # MIT 协议
├── requirements.txt                # Python 依赖
├── .gitignore                      # Git 忽略配置
│
├── adapters/                       # 网盘适配器层
│   ├── base.py                     # 适配器基类
│   └── goukuai.py                  # 够快云适配器
│
├── security/                       # 安全模块
│   └── permission_checker.py       # 权限检查器
│
├── organizers/                     # 整理引擎
│   └── auto_sort.py                # 自动分类整理
│
├── scripts/                        # 工具脚本
│   └── test_connection.py          # 连接测试
│
├── references/                     # 参考文档
│   └── api_docs.md                 # API 文档汇总
│
└── config/                         # 配置目录
    └── goukuai.example.yaml        # 配置模板
```

## 🔧 核心能力

### 文件操作

| 功能 | 说明 | 示例 |
|------|------|------|
| 🔍 搜索文件 | 按名称/标签/内容搜索 | `search_files("合同")` |
| ⬇️ 下载文件 | 获取文件内容 | `download_file(hash)` |
| ⬆️ 上传文件 | 上传到指定位置 | `upload_file(path, content)` |
| 📄 读取内容 | 提取文本（PDF/Word/Excel） | `get_file_content(hash)` |
| 📋 复制文件 | 复制文件/文件夹 | `copy_file(from, to)` |
| 🔄 移动文件 | 移动文件/文件夹 | `move_file(from, to)` |
| 🗑️ 删除文件 | 删除到回收站 | `delete_file(path)` |
| 🔒 文件锁 | 上锁/解锁 | `lock_file(path, "lock")` |

### 文件夹管理

| 功能 | 说明 | 示例 |
|------|------|------|
| 📂 创建文件夹 | 新建目录 | `create_folder("/docs/2026")` |
| 📁 浏览文件夹 | 列出文件列表 | `list_files("/docs")` |
| 🏷️ 添加标签 | 设置文件标签 | `add_tag(path, "合同;2026")` |
| 📊 统计信息 | 获取空间使用 | `get_library_stat()` |

### 权限管理

| 功能 | 说明 | 示例 |
|------|------|------|
| 👁️ 获取权限 | 查看文件权限 | `get_permission(path)` |
| 🔐 设置权限 | 修改用户/部门权限 | `set_permission(path, permissions)` |
| 🔄 权限继承 | 设置继承状态 | `set_permission_inherit(path, True)` |
| ❌ 删除权限 | 移除权限 | `del_permission(path, member_ids)` |

### 协作分享

| 功能 | 说明 | 示例 |
|------|------|------|
| 🔗 创建外链 | 生成分享链接 | `create_link(path, deadline, password)` |
| 🚫 关闭外链 | 关闭分享 | `close_link(code)` |
| ✏️ 协同编辑 | 获取编辑链接 | `get_cedit_url(path, user_id)` |
| 💬 批注 | 获取批注链接 | `get_annotation_url(path)` |

### AI 增强

| 功能 | 说明 | 示例 |
|------|------|------|
| 📝 文档摘要 | 自动总结要点 | `summarize_file(path)` |
| ❓ 文档问答 | 基于内容回答 | `ask_file(path, "报销流程？")` |
| 📚 知识库检索 | 跨文档搜索 | `search_knowledge("合同模板")` |
| 🏷️ 智能分类 | AI 自动分类 | `auto_classify(file_content)` |
| 🧹 整理建议 | 分析文件结构 | `get_sort_suggestions()` |

### 版本管理

| 功能 | 说明 | 示例 |
|------|------|------|
| 📜 历史版本 | 获取版本列表 | `get_history(path)` |
| ↩️ 恢复版本 | 还原历史版本 | `recover_version(hid)` |
| 🔍 版本对比 | 对比差异 | `compare_versions(hid1, hid2)` |

## 🔐 安全特性

### 权限检查

所有操作都会自动进行权限验证：

```python
# 自动检查用户是否有权访问
adapter.set_user_context(user_id="123", account="zhangsan@company.com")

# 无权操作会抛出 PermissionError
try:
    adapter.download_file("/finance/salary.xlsx")
except PermissionError as e:
    print(f"权限不足：{e}")
```

### 审计日志

所有敏感操作自动记录：

```python
# 启用审计日志
adapter.enable_audit_log()

# 查询审计日志
logs = adapter.get_audit_logs(
    user_id="123",
    start_time="2026-03-01",
    end_time="2026-03-10"
)
```

### 敏感文件保护

自动识别和保护敏感文件：

```python
# 敏感文件模式
adapter.set_sensitive_patterns(["*合同*", "*财务*", "*薪资*"])

# 敏感文件操作需要额外验证
adapter.download_file("/contracts/secret_contract.pdf")
# → 需要二次验证或管理员权限
```

## 📋 配置示例

### 基础配置

```yaml
# config/goukuai.yaml
adapter: goukuai

credentials:
  client_id: "${GOUKUAI_CLIENT_ID}"
  client_secret: "${GOUKUAI_CLIENT_SECRET}"
  org_client_id: "${GOUKUAI_ORG_CLIENT_ID}"
  org_client_secret: "${GOUKUAI_ORG_CLIENT_SECRET}"
  api_host: "yk3.gokuai.com"

# 权限设置
permissions:
  default_role: viewer
  allow_external_share: true
  require_approval_for_share: true

# 审计日志
audit:
  enabled: true
  log_file: "/var/log/goukuai_audit.log"
  retention_days: 365

# 敏感文件保护
sensitive:
  enabled: true
  patterns:
    - "*合同*"
    - "*财务*"
    - "*薪资*"
    - "*机密*"
```

## ⚠️ 注意事项

1. **API 签名** - 所有请求需要按照 [sign.md](/overview/sign.md) 进行签名
2. **时间戳** - `dateline` 参数使用 Unix 时间戳（秒）
3. **编码** - 所有参数使用 UTF-8 编码
4. **频率限制** - 避免短时间内大量请求
5. **密钥安全** - 不要将 `client_secret` 硬编码在代码中

## 🛠️ 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 401041 签名验证失败 | 签名计算错误/编码问题 | 检查签名算法，确保 UTF-8 编码 |
| 403 权限不足 | 用户无权访问 | 检查用户权限设置 |
| 404 文件不存在 | 路径错误或文件已删除 | 检查文件路径 |
| 500 服务器错误 | 服务端问题 | 稍后重试或联系够快支持 |

## 📖 参考文档

- [库文件操作 API](/yk3/file.md)
- [部门和成员 API](/yk3/ent.md)
- [库操作 API](/yk3/library.md)
- [权限管理 API](/yk3/permission.md)
- [访问控制](/overview/sign.md)

---

**版本：** 1.0.1  
**最后更新：** 2026-03-10
