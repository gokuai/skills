# 够快云库连接器 (Goukuai Cloud Connector)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.1-green.svg)](https://github.com/YOUR_USERNAME/goukuai-connector)

> **企业级网盘 AI 连接器** - 让 AI 能够安全、高效地操作够快云库中的文件

---

## 🌟 特性亮点

- **📁 完整文件操作** - 搜索/上传/下载/移动/复制/删除/重命名
- **🔐 企业级权限** - RBAC 权限模型，审计日志，敏感文件保护
- **🧹 智能整理** - 基于 AI 和规则的文件自动分类和批量整理
- **🔗 协作分享** - 创建外链/协同编辑/权限管理
- **📊 统计审计** - 库统计信息，操作日志追踪
- **⚡ 轻量级** - 无额外依赖，开箱即用

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 本库无强制依赖，可选安装 PDF 处理库
# pip install pypdf
```

### 2. 配置认证信息

```bash
# 企业级认证（管理组织架构）
export GOUKUAI_CLIENT_ID="your_client_id"
export GOUKUAI_CLIENT_SECRET="your_client_secret"

# 库级认证（操作特定文件库）
export GOUKUAI_ORG_CLIENT_ID="your_org_client_id"
export GOUKUAI_ORG_CLIENT_SECRET="your_org_client_secret"
```

**获取认证信息：**
1. 登录够快云库管理后台
2. 进入「企业应用开发」
3. 创建应用获取 `client_id` 和 `client_secret`
4. 调用 API 获取库级认证

### 3. 测试连接

```bash
cd goukuai-connector
python3 scripts/test_connection.py
```

**预期输出：**
```
✅ 认证成功
✅ 库信息获取成功
✅ 文件列表获取成功
✅ 所有测试通过！
```

---

## 📖 使用示例

### 基础文件操作

```python
from adapters.goukuai import GoukuaiAdapter

# 初始化适配器
adapter = GoukuaiAdapter({
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "org_client_id": "your_org_client_id",
    "org_client_secret": "your_org_client_secret",
    "api_host": "yk3.gokuai.com"
})

# 搜索文件
files = adapter.search_files("合同", size=10)
print(f"找到 {len(files)} 个文件")
for f in files:
    print(f"  - {f.fullpath} ({f.filesize} 字节)")

# 下载文件
content = adapter.download_file(fullpath="/docs/report.pdf")

# 上传文件
with open("local_file.pdf", "rb") as f:
    adapter.upload_file("/docs/file.pdf", f.read())

# 移动文件
adapter.move_file("/old/file.pdf", "/new/file.pdf")

# 删除文件
adapter.delete_file("/temp/file.pdf")
```

### 文件夹管理

```python
# 创建文件夹
folder = adapter.create_folder("/2026/Q1")

# 列出文件
files = adapter.list_files("/2026/Q1")
for f in files:
    print(f"{'📁' if f.dir else '📄'} {f.filename}")

# 添加标签
adapter.add_tag("/docs/contract.pdf", "合同;2026;重要")
```

### 权限管理

```python
# 获取文件权限
permissions = adapter.get_permission("/docs/salary.xlsx")
print(f"权限条目：{len(permissions)}")

# 设置权限
adapter.set_permission("/docs/salary.xlsx", {
    "member_ids": [123, 456],
    "permission": {
        "ls": 1,  # 显示
        "cd": 1,  # 进入
        "pv": 1,  # 预览
        "dl": 1   # 下载
    }
})

# 设置权限继承
adapter.set_permission_inherit("/docs", inherit=True)
```

### 分享协作

```python
# 创建分享链接
link = adapter.create_share_link(
    fullpath="/docs/report.pdf",
    deadline=1710316800,  # 到期时间戳
    password="123456",     # 访问密码
    auth="download"        # 权限：preview/download/upload
)
print(f"分享链接：{link.link}")

# 协同编辑链接
edit_url = adapter.get_cedit_url(
    fullpath="/docs/report.docx",
    op_id="123",
    readonly=False,
    timeout=3600
)
```

### 智能整理

```python
from organizers.auto_sort import AutoSorter

sorter = AutoSorter(adapter)

# 自动分类文件
category, confidence = sorter.classify("/test/合同 2026.pdf")
print(f"分类：{category} (置信度：{confidence:.1%})")
# 输出：分类：合同 (置信度：60.0%)

# 整理整个文件夹
results = sorter.sort_folder(
    "/inbox",
    base_folder="/organized",
    recursive=True,
    dry_run=False  # True=预览，False=实际移动
)
print(f"整理了 {len(results)} 个文件")

# 获取整理建议
suggestions = sorter.get_suggestions("/inbox")
print(f"建议创建 {len(suggestions['recommendations'])} 个文件夹")
```

---

## 📁 项目结构

```
goukuai-connector/
├── 📄 README.md                    # 本文件
├── 📄 SKILL.md                     # 详细使用文档
├── 📄 LICENSE                      # MIT 开源协议
├── 📄 requirements.txt             # Python 依赖
├── 📄 .gitignore                   # Git 忽略配置
│
├── 📁 adapters/                    # 网盘适配器层
│   ├── base.py                     # 适配器基类（标准接口）
│   └── goukuai.py                  # 够快云适配器（50+ API 接口）
│
├── 📁 security/                    # 安全模块
│   └── permission_checker.py       # 权限检查器（RBAC 模型）
│
├── 📁 organizers/                  # 整理引擎
│   └── auto_sort.py                # 自动分类整理
│
├── 📁 scripts/                     # 工具脚本
│   └── test_connection.py          # 连接测试脚本
│
├── 📁 references/                  # 参考文档
│   └── api_docs.md                 # API 文档汇总
│
└── 📁 config/                      # 配置目录
    └── goukuai.example.yaml        # 配置模板
```

---

## 🔧 API 接口支持

### 文件操作（15+ 接口）

| 接口 | 说明 | 状态 |
|------|------|------|
| `list_files()` | 列出文件夹内容 | ✅ |
| `search_files()` | 搜索文件 | ✅ |
| `download_file()` | 下载文件 | ✅ |
| `upload_file()` | 上传文件 | ✅ |
| `get_file_content()` | 提取文件文本 | ✅ |
| `get_file_info()` | 获取文件信息 | ✅ |
| `copy_file()` | 复制文件 | ✅ |
| `move_file()` | 移动文件 | ✅ |
| `delete_file()` | 删除文件 | ✅ |
| `create_folder()` | 创建文件夹 | ✅ |
| `get_history()` | 获取历史版本 | ✅ |
| `recover_version()` | 恢复版本 | ✅ |
| `add_tag()` | 添加标签 | ✅ |
| `del_tag()` | 删除标签 | ✅ |
| `get_library_stat()` | 获取统计信息 | ✅ |

### 权限管理（4 接口）

| 接口 | 说明 | 状态 |
|------|------|------|
| `get_permission()` | 获取权限 | ✅ |
| `set_permission()` | 设置权限 | ✅ |
| `set_permission_inherit()` | 权限继承 | ✅ |
| `PermissionChecker` | 权限检查器 | ✅ |

### 分享协作（3 接口）

| 接口 | 说明 | 状态 |
|------|------|------|
| `create_share_link()` | 创建外链 | ✅ |
| `close_share_link()` | 关闭外链 | ✅ |
| `get_cedit_url()` | 协同编辑 | ✅ |

### 整理引擎（10+ 方法）

| 功能 | 说明 | 状态 |
|------|------|------|
| `classify()` | 文件分类 | ✅ |
| `sort_file()` | 整理单个文件 | ✅ |
| `sort_folder()` | 整理文件夹 | ✅ |
| `get_suggestions()` | 整理建议 | ✅ |

---

## ⚙️ 配置说明

### 环境变量方式

```bash
export GOUKUAI_CLIENT_ID="your_client_id"
export GOUKUAI_CLIENT_SECRET="your_client_secret"
export GOUKUAI_ORG_CLIENT_ID="your_org_client_id"
export GOUKUAI_ORG_CLIENT_SECRET="your_org_client_secret"
export GOUKUAI_API_HOST="yk3.gokuai.com"
```

### 配置文件方式

复制配置模板：
```bash
cp config/goukuai.example.yaml config/goukuai.yaml
```

编辑 `config/goukuai.yaml`：
```yaml
credentials:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  org_client_id: "your_org_client_id"
  org_client_secret: "your_org_client_secret"
  api_host: "yk3.gokuai.com"

permissions:
  default_role: viewer
  allow_external_share: true

audit:
  enabled: true
  log_file: "/var/log/goukuai_audit.log"
```

---

## 🧪 测试

### 运行测试套件

```bash
# 连接测试
python3 scripts/test_connection.py

# 功能测试
python3 final_test.py

# 认证测试
python3 test_auth.py
```

### 预期输出

```
======================================================================
                    够快云库连接器 - 最终测试
======================================================================

✅ 初始化适配器...
   状态：就绪

📊 库信息:
   库名称：档案库
   文件数量：24
   空间配额：1.00 GB

📁 根目录文件:
   📁 00 档案管理制度以及政策
   📁 01 人事档案
   📁 02 业务合同档案
   📁 03 财务档案
   📁 04 行政档案

✅ 所有测试通过！
======================================================================
```

---

## 🔒 安全特性

### 权限控制
- ✅ RBAC 角色权限模型
- ✅ 权限继承机制
- ✅ 细粒度权限控制（预览/下载/编辑/删除/分享）

### 审计日志
- ✅ 所有敏感操作自动记录
- ✅ 操作人/时间/IP 地址追踪
- ✅ 可配置日志保留期限

### 敏感文件保护
- ✅ 敏感文件自动识别
- ✅ 强制水印
- ✅ 下载限制
- ✅ 外部分享审批

---

## 📊 实际应用场景

### 场景 1：快速找合同
```python
files = adapter.search_files("XX 公司 合同")
# → 3 秒找到所有相关合同
```

### 场景 2：整理年度档案
```python
sorter.sort_folder("/2026 合同", base_folder="/已归档/2026")
# → 自动分类到 合同/财务/人事 等文件夹
```

### 场景 3：分享文件给客户
```python
link = adapter.create_share_link("/产品资料.pdf", password="abc123")
# → 生成带密码的链接，3 天后自动过期
```

### 场景 4：保护工资表
```python
adapter.set_permission("/工资表.xlsx", {"member_ids": [HR 的 ID]})
# → 只有 HR 能访问
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/goukuai-connector.git
cd goukuai-connector

# 安装依赖（可选）
pip install pypdf

# 运行测试
python3 scripts/test_connection.py
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📞 支持与反馈

- **够快云库官网：** https://www.gokuai.com
- **API 文档：** 参见 `references/api_docs.md`
- **Issue 反馈：** https://github.com/YOUR_USERNAME/goukuai-connector/issues

---

## 📝 更新日志

### v1.0.1 (2026-03-10)
- 🐛 修复 `organizers/auto_sort.py` 语法错误
- ✨ 优化 `adapters/goukuai.py` 库信息获取方法
- ✨ 移除编辑器模块，保持轻量级
- ✅ 所有功能测试通过
- ✅ 真实环境验证成功

### v1.0.0 (2026-03-10)
- 🎉 初始版本发布
- ✅ 完整的够快云 API 适配器（50+ 接口）
- ✅ 企业级权限管理（RBAC 模型）
- ✅ 自动分类整理引擎
- ✅ 完整的文档和测试脚本

---

**Made with ❤️ for Enterprise Cloud Storage**
