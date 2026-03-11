# 够快云库 API 文档汇总

## 基础信息

### API 域名

```
Host: yk3.gokuai.com
```

### 认证方式

够快云库支持两种认证级别：

1. **企业级认证** - 使用 `client_id` 和 `client_secret`
   - 用于管理企业组织架构
   - 管理文件库
   - 获取库授权

2. **库级认证** - 使用 `org_client_id` 和 `org_client_secret`
   - 用于操作具体文件库
   - 文件/文件夹操作
   - 权限管理

### 获取认证信息

#### 步骤 1: 企业授权

在够快云库管理后台创建应用，获得：
- `client_id`
- `client_secret`

#### 步骤 2: 获取库授权

调用接口获取特定文件库的授权：

```
POST /m-open/1/org/bind
```

**请求参数：**
| 参数 | 必需 | 说明 |
|------|------|------|
| client_id | 是 | 企业 client_id |
| org_id | - | 库 ID（与 mount_id 二选一） |
| mount_id | - | 库空间 ID |
| title | 是 | 应用名称 |

**返回结果：**
```json
{
  "org_client_id": "库授权 client_id",
  "org_client_secret": "库授权 client_secret"
}
```

---

## 签名算法

所有 API 请求都需要签名，计算方法：

### 步骤

1. **参数排序** - 按字母顺序排序（排除 `sign` 和文件内容）
2. **拼接值** - 用 `\n` (ASCII 10) 分隔参数值
3. **HMAC-SHA1** - 使用密钥加密
4. **Base64 编码** - 得到最终签名

### 公式

```
base64-encode( hmac-sha1( {string}, {client_secret} ) )
```

### 示例

**密钥：**
```
client_secret=lZltU72WrEFOsbmT2IxSWg
```

**参数：**
```
client_id=NGCr2q1Fwc2tBWPfOartag
dateline=1490605129
fullpath=会议资料/2017-10-31.docx
```

**排序后：**
```
client_id=NGCr2q1Fwc2tBWPfOartag
dateline=1490605129
fullpath=会议资料/2017-10-31.docx
```

**拼接字符串：**
```
NGCr2q1Fwc2tBWPfOartag
1490605129
会议资料/2017-10-31.docx
```

**签名结果：**
```
glL9RlCmaDA6udIGo2DADTgCZlI=
```

---

## 核心 API 接口

### 文件操作

#### 文件列表
```
POST /m-open/1/file/ls
```
**参数：** org_client_id, fullpath, tag(可选), start(可选), size(可选)

#### 文件搜索
```
POST /m-open/1/file/search
```
**参数：** org_client_id, keywords, path(可选), scope(可选), start(可选), size(可选)

#### 文件下载
```
POST /m-open/1/file/download_url
```
**参数：** org_client_id, fullpath/hash, open(可选), op_id(可选)

**返回：** `{"urls": ["下载链接 1", "下载链接 2"]}`

#### 文件上传
```
POST /m-open/1/file/create_file  (步骤 1)
POST /2/web_upload              (步骤 2)
```

#### 文件信息
```
POST /m-open/1/file/info
```

#### 复制文件
```
POST /m-open/1/file/copy
```

#### 移动文件
```
POST /m-open/1/file/move
```

#### 删除文件
```
POST /m-open/1/file/del
```

#### 创建文件夹
```
POST /m-open/1/file/create_folder
```

### 权限管理

#### 获取权限
```
POST /m-open/1/file/get_permission
```

#### 设置权限
```
POST /m-open/2/file/set_permission
```

#### 设置权限继承
```
POST /m-open/2/file/set_permission_inherit
```

#### 删除权限
```
POST /m-open/2/file/del_permission
```

### 分享协作

#### 创建外链
```
POST /m-open/1/file/link
```
**参数：** org_client_id, fullpath, deadline(可选), password(可选), auth(可选)

**权限类型：**
- `preview` - 仅预览
- `download` - 预览和下载
- `upload` - 预览、下载、上传

#### 关闭外链
```
POST /m-open/1/file/link_close
```

#### 协同编辑
```
POST /m-open/1/file/cedit_url
```

### 版本管理

#### 获取历史版本
```
POST /m-open/1/file/history
```

### 标签管理

#### 添加标签
```
POST /m-open/1/file/add_tag
```

#### 删除标签
```
POST /m-open/1/file/del_tag
```

### 统计信息

#### 库统计
```
POST /m-open/1/file/stat
```

**返回：**
```json
{
  "org_id": 库 ID,
  "org_name": "库名称",
  "mount_id": 库空间 ID,
  "capacity": 空间配额（字节）,
  "size": 已使用空间,
  "size_recycle": 回收站占用,
  "count_file": 文件数量,
  "storage_point": 存储点
}
```

---

## 权限对照表

| 权限代码 | 说明 | 级别 |
|----------|------|------|
| ls | 显示 | VIEWER |
| cd | 进入目录 | VIEWER |
| pv | 预览文件 | VIEWER |
| dl | 下载/打开文件 | VIEWER |
| w | 写入/编辑文件 | EDITOR |
| ul | 添加新文件 | EDITOR |
| mk | 新建文件夹 | EDITOR |
| ren | 重命名 | EDITOR |
| rm | 删除 | ADMIN |
| ln | 外链分享 | EDITOR |
| h | 查看历史版本 | EDITOR |
| hr | 还原历史版本 | EDITOR |
| rmk | 查看评论 | VIEWER |
| rmka | 添加评论 | EDITOR |
| t | 添加标签 | EDITOR |
| trm | 删除标签 | EDITOR |
| p | 查看共享参与人 | VIEWER |
| ps | 管理共享参与人 | ADMIN |
| ss | 显示当前项 | VIEWER |
| sren | 重命名当前项 | EDITOR |
| srm | 删除当前项 | ADMIN |
| mls | 修改库设置 | OWNER |
| b | 查看回收站文件 | VIEWER |
| br | 还原回收站文件 | EDITOR |
| be | 清空回收站 | ADMIN |
| mln | 管理外链 | ADMIN |

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 401041 | 签名验证失败 |
| 403 | 权限不足 |
| 404 | 文件不存在 |
| 500 | 服务器错误 |

---

## 最佳实践

### 1. 错误处理

```python
try:
    result = adapter.download_file(fullpath="/docs/file.pdf")
except PermissionError:
    print("权限不足")
except FileNotFoundError:
    print("文件不存在")
except Exception as e:
    print(f"其他错误：{e}")
```

### 2. 批量操作

```python
# 使用批量接口而非循环
files_to_copy = ["/file1.pdf", "/file2.pdf", "/file3.pdf"]

# ❌ 不推荐
for f in files_to_copy:
    adapter.copy_file(f, f"/backup/{f}")

# ✅ 推荐：使用批量接口（如果支持）
adapter.batch_copy(files_to_copy, "/backup/")
```

### 3. 大文件上传

```python
# 分块上传大文件
def upload_large_file(fullpath, file_size, chunk_size=10*1024*1024):
    # 获取上传服务器
    upload_info = adapter.get_upload_server(fullpath)
    
    # 分块上传
    for start in range(0, file_size, chunk_size):
        end = min(start + chunk_size, file_size)
        chunk = file_content[start:end]
        adapter.upload_chunk(upload_info, chunk, start, end)
```

### 4. 权限缓存

```python
# 缓存权限检查结果，减少 API 调用
@cache(ttl=300)  # 5 分钟缓存
def check_user_permission(user_id, file_path):
    return adapter.get_permission(file_path, member_id=user_id)
```

---

## 参考资料

- 原始文档位置：`/Users/may/Downloads/developer/yk3/`
- [文件操作 API](file.md)
- [权限管理 API](permission.md)
- [部门成员 API](ent.md)
- [库操作 API](library.md)
- [访问控制](../overview/sign.md)
