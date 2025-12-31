# Auto-Claude 上游同步工作流 (FPF 校对版)

> **校对时间**: 2024-12-31
> **FPF 审查**: R_eff = 0.95 (修正后)
> **数据来源**: Git 仓库实际记录

---

## 📊 当前仓库状态

| 指标 | 值 | 说明 |
|------|---|------|
| 本地领先提交数 | 7 | git log upstream/develop..HEAD |
| 落后上游提交数 | 11 | git log HEAD..upstream/develop |
| 本地改动文件总数 | 123 个 | 含代码、文档、配置 |
| 本地核心代码改动 | 16 个 | 多认证 + i18n + 测试 |
| 潜在冲突文件 | 5 个 | 双方都修改的文件 |

---

## 🔴 本地核心改动文件完整清单

### 一、多认证改动 (5 个文件)

| # | 文件路径 | 改动量 | 冲突风险 |
|---|---------|--------|---------|
| 1 | `apps/backend/core/auth.py` | +116 行 | ⚠️ **高** (上游也修改) |
| 2 | `apps/backend/core/client.py` | +24 行 | ⚠️ 中 (上游也修改) |
| 3 | `apps/backend/core/simple_client.py` | +10 行 | ✅ 低 (上游无改动) |
| 4 | `apps/backend/cli/utils.py` | +50 行 | ✅ 低 (上游无改动) |
| 5 | `apps/backend/.env.example` | +27 行 | ⚠️ 中 (上游也修改) |

### 二、多语言改动 (10 个文件)

| # | 文件路径 | 冲突风险 |
|---|---------|---------|
| 6 | `apps/frontend/src/shared/constants/i18n.ts` | ✅ 低 |
| 7 | `apps/frontend/src/shared/i18n/index.ts` | ⚠️ **中** (上游也修改) |
| 8 | `apps/frontend/src/shared/i18n/locales/zh/common.json` | ✅ 低 |
| 9 | `apps/frontend/src/shared/i18n/locales/zh/dialogs.json` | ✅ 低 |
| 10 | `apps/frontend/src/shared/i18n/locales/zh/navigation.json` | ✅ 低 |
| 11 | `apps/frontend/src/shared/i18n/locales/zh/onboarding.json` | ✅ 低 |
| 12 | `apps/frontend/src/shared/i18n/locales/zh/settings.json` | ✅ 低 |
| 13 | `apps/frontend/src/shared/i18n/locales/zh/taskReview.json` | ✅ 低 |
| 14 | `apps/frontend/src/shared/i18n/locales/zh/tasks.json` | ✅ 低 |
| 15 | `apps/frontend/src/shared/i18n/locales/zh/welcome.json` | ✅ 低 |

### 三、测试文件 (1 个文件)

| # | 文件路径 | 冲突风险 |
|---|---------|---------|
| 16 | `tests/test_auth_properties.py` | ✅ 低 (新增) |

---

## ⚠️ 潜在冲突文件清单 (5 个)

> **定义**: 本地和上游都修改了同一文件

| # | 文件路径 | 冲突类型 | 处理策略 |
|---|---------|---------|---------|
| 1 | `apps/backend/core/auth.py` | **设计冲突** | 🔒 保留本地 |
| 2 | `apps/backend/core/client.py` | 代码冲突 | 🔒 保留本地 |
| 3 | `apps/backend/.env.example` | 配置冲突 | 🔒 保留本地 |
| 4 | `apps/frontend/src/shared/i18n/index.ts` | 代码冲突 | 手动合并 |
| 5 | `apps/frontend/package-lock.json` | 依赖冲突 | 重新生成 |

---

## 🛡️ 设计冲突保护策略 (ANTHROPIC_API_KEY)

> [!CAUTION]
> **这是最关键的设计分歧，必须强制保留本地设计！**

### 上游设计决策

上游在 `auth.py` 中**故意移除了 ANTHROPIC_API_KEY 支持**：

```python
# 上游代码
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_AUTH_TOKEN",
    # 注意：没有 ANTHROPIC_API_KEY
]

# 上游注释
# NOTE: We intentionally do NOT fall back to ANTHROPIC_API_KEY.
# This prevents silent billing to user's API credits when OAuth fails.
```

### 你的设计决策 (必须保留)

```python
# 你的代码 - 多认证支持
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",  # OAuth token (highest priority)
    "ANTHROPIC_AUTH_TOKEN",      # Proxy/CCR token
    "ANTHROPIC_API_KEY",         # Direct API key support [你的改动]
]
```

### 合并时的强制操作

在合并 `auth.py` 时，**无论上游如何修改，必须执行以下步骤**：

```bash
# 1. 把你的版本标记为需要保留
git checkout --ours apps/backend/core/auth.py

# 2. 如果上游有其他有用的修改，手动添加进来
# 3. 确保以下关键代码存在：

# AUTH_TOKEN_ENV_VARS 必须包含：
"ANTHROPIC_API_KEY",

# SDK_ENV_VARS 必须包含：
"ANTHROPIC_API_KEY",

# get_token_type 函数必须存在
# apply_auth_env 函数必须存在
# validate_proxy_config 函数必须存在
```

---

## 📋 合并检查清单

### 合并前

- [ ] `git fetch upstream` 获取最新代码
- [ ] 查看上游新提交：`git log --oneline HEAD..upstream/develop`
- [ ] 检查冲突文件：运行下面的检测脚本

### 合并时

- [ ] 对于 `auth.py`：**强制保留本地版本** (`--ours`)
- [ ] 对于 `client.py`：保留本地多认证逻辑 (`--ours`)
- [ ] 对于 `.env.example`：手动合并，保留本地认证配置示例
- [ ] 对于 `i18n/index.ts`：手动合并，保留中文支持
- [ ] 对于 `package-lock.json`：重新 `pnpm install` 生成

> **注意**: `simple_client.py` 和 `cli/utils.py` 上游无改动，不会产生冲突，无需特殊处理。

### 合并后

- [ ] 运行认证测试：`pytest tests/test_auth_properties.py`
- [ ] 验证 API Key 模式可用
- [ ] 验证 OAuth 模式可用
- [ ] 验证 Proxy 模式可用
- [ ] 验证 i18n 中文显示正常

---

## 🔧 冲突检测脚本

```bash
#!/bin/bash
# 文件: check-upstream-conflicts.sh

git fetch upstream

echo "=== 潜在冲突文件 ==="
comm -12 \
  <(git diff --name-only $(git merge-base HEAD upstream/develop) HEAD | sort) \
  <(git diff --name-only $(git merge-base HEAD upstream/develop) upstream/develop | sort)

echo ""
echo "=== 上游对 auth.py 的改动 ==="
git diff HEAD..upstream/develop -- apps/backend/core/auth.py

echo ""
echo "=== 建议 ==="
echo "1. 对 auth.py 使用 --ours 策略"
echo "2. 手动检查其他冲突文件"
```

---

## 📦 合并命令参考

### 推荐：带策略的 Merge

```bash
# 1. 创建备份
git branch backup-$(date +%Y%m%d)

# 2. 合并，对冲突文件优先使用本地版本
git merge upstream/develop

# 3. 如果 auth.py 和 client.py 冲突，强制使用本地版本
git checkout --ours apps/backend/core/auth.py
git checkout --ours apps/backend/core/client.py

# 4. 对于 .env.example 和 i18n/index.ts 需要手动合并
# 注意: simple_client.py 和 cli/utils.py 上游无改动，不会冲突

# 5. 标记冲突已解决
git add .

# 6. 完成合并
git commit -m "merge: sync with upstream, preserve multi-auth design"
```
