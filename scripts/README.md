# 飞书群文件自动上传脚本

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `feishu_auto_upload.py` | 独立版本，可手动运行或配置定时任务 |
| `openclaw_feishu_upload.py` | OpenClaw 集成版本，可通过心跳/定时任务触发 |
| `README.md` | 本说明文档 |

## 🚀 快速开始

### 1. 配置飞书凭证

**方式 A：环境变量（推荐）**
```bash
export FEISHU_APP_ID="cli_xxxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxx"
```

**方式 B：配置文件**
编辑 `config/feishu_upload.yaml`，填入你的飞书应用凭证。

### 2. 获取群聊 ID

飞书群聊 ID 格式：`chat:xxxxxxxxxxxxx`

- 从飞书群 URL 获取
- 从飞书事件 payload 获取
- 当前群 ID 已配置为：`chat:oc_8866d74caa0813e3763ab71f8f0dd272`

### 3. 运行脚本

```bash
# 进入脚本目录
cd ~/.openclaw/workspace/skills/goukuai-connector

# 运行 OpenClaw 集成版本
python3 scripts/openclaw_feishu_upload.py
```

## ⚙️ OpenClaw 集成

### 心跳定时任务

在 `HEARTBEAT.md` 中添加：

```markdown
# 每 4 小时检查一次飞书群文件
- [ ] 飞书群文件自动上传 → 每 4 小时
```

然后在 OpenClaw 中配置定时调用脚本。

### 手动触发

在飞书群里发送消息：
```
@bot 上传群文件
```

## 📋 配置选项

编辑 `config/feishu_upload.yaml`：

```yaml
upload:
  # 目标文件夹
  target_folder: "销售支持"
  
  # 文件类型过滤（空=全部）
  file_types: ["pdf", "docx", "xlsx"]
  
  # 文件大小限制（MB）
  max_size_mb: 100
  
  # 保留原文件名
  keep_original_name: true
  
  # 文件名前缀
  # name_prefix: "{date}_"
```

## 📊 日志

- 运行日志：`logs/feishu_upload.log`
- 已处理文件记录：`logs/processed_files.json`

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| 飞书令牌获取失败 | 检查 app_id/app_secret 是否正确 |
| 文件下载失败 | 检查 `im:resource` 权限是否开通 |
| 上传失败 | 检查够快云库配置和权限 |
| 重复上传 | 检查 `logs/processed_files.json` 记录 |

## 📝 注意事项

1. **避免重复上传** - 脚本会自动记录已处理的文件 key
2. **文件大小限制** - 默认 100MB，可在配置中调整
3. **文件名冲突** - 自动添加时间戳避免覆盖
4. **权限安全** - 建议使用环境变量存储敏感信息
