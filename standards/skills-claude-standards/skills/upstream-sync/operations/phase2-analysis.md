# Phase 2: Analysis (分析)

> **目标**: 分析冲突风险，识别保护需求
> **输入**: `discovery-report.md`
> **输出**: `conflict-analysis.md`

---

## 操作步骤

### Step 2.1: 分类冲突文件

对 Phase 1 识别的潜在冲突文件进行分类：

| 冲突类型 | 定义 | 示例 |
|---------|------|------|
| **设计冲突** | 本地与上游设计理念不同，必须保留本地 | `auth.py` 多认证 vs 上游单认证 |
| **代码冲突** | 同一文件双方都修改，需要合并 | `client.py` 功能增强 |
| **配置冲突** | 配置文件冲突 | `.env.example` |
| **依赖冲突** | 包管理文件冲突 | `package-lock.json` |
| **文档冲突** | 文档文件冲突 | `README.md` |

### Step 2.2: 查看上游对冲突文件的改动

```bash
# 对每个冲突文件，查看上游的改动
git diff HEAD..upstream/develop -- <conflict-file>

# 示例
git diff HEAD..upstream/develop -- apps/backend/core/auth.py
```

### Step 2.3: 识别核心保护文件

核心保护文件的特征：
1. 本地有意设计与上游不同
2. 包含关键业务逻辑
3. 上游改动会破坏本地功能

**识别方法**：
```bash
# 查看本地改动的关键代码
git diff $MERGE_BASE HEAD -- <file> | grep -E "^\+.*KEY|AUTH|i18n"
```

### Step 2.4: 评估冲突风险等级

| 风险等级 | 定义 | 处理建议 |
|---------|------|---------|
| **高** ⚠️ | 设计冲突，上游故意移除本地功能 | `--ours` 强制保留 |
| **中** ⚠️ | 代码冲突，双方都有有用改动 | 手动合并 |
| **低** ✅ | 简单冲突或可自动解决 | Git 自动合并或重新生成 |

### Step 2.5: 分析上游改动意图

对于设计冲突，需要理解上游为什么这样改：

```bash
# 查看上游相关提交的 commit message
git log --oneline HEAD..upstream/develop -- <file>

# 查看具体提交详情
git show <commit-hash>
```

---

## 分析清单

对每个冲突文件填写：

```markdown
### 文件: <path/to/file>

| 属性 | 值 |
|------|-----|
| 冲突类型 | 设计冲突/代码冲突/配置冲突/依赖冲突 |
| 风险等级 | 高/中/低 |
| 本地改动摘要 | xxx |
| 上游改动摘要 | yyy |
| 上游改动意图 | zzz |
| 建议处理策略 | --ours / 手动合并 / 重新生成 |
| 需要保护 | 是/否 |
```

---

## 输出模板

生成 `conflict-analysis.md`：

```markdown
# 冲突分析报告

> **生成时间**: YYYY-MM-DD HH:MM
> **基于**: discovery-report.md

---

## 冲突文件分类

### 设计冲突 (必须保护)

| # | 文件 | 本地设计 | 上游设计 | 风险 |
|---|------|---------|---------|------|
| 1 | `auth.py` | 多认证支持 | 仅 OAuth | ⚠️ 高 |

### 代码冲突 (需要合并)

| # | 文件 | 本地改动 | 上游改动 | 风险 |
|---|------|---------|---------|------|
| 1 | `client.py` | 认证逻辑 | SDK 权限 | ⚠️ 中 |

### 配置冲突

| # | 文件 | 处理建议 |
|---|------|---------|
| 1 | `.env.example` | 手动合并，保留本地配置 |

### 依赖冲突

| # | 文件 | 处理建议 |
|---|------|---------|
| 1 | `package-lock.json` | 重新生成 |

---

## 核心保护文件清单

> 这些文件必须使用 `--ours` 策略保护

| # | 文件 | 保护原因 |
|---|------|---------|
| 1 | `apps/backend/core/auth.py` | 多认证系统核心 |
| 2 | ... | ... |

---

## 详细分析

### 1. apps/backend/core/auth.py

**冲突类型**: 设计冲突
**风险等级**: ⚠️ 高

**本地设计决策**:
```python
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",  # 本地添加
]
```

**上游设计决策**:
```python
# NOTE: We intentionally do NOT fall back to ANTHROPIC_API_KEY.
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",
    "ANTHROPIC_AUTH_TOKEN",
    # 故意不包含 ANTHROPIC_API_KEY
]
```

**分析**: 上游故意移除 API Key 支持以防止意外计费。本地需要保留多认证支持。

**处理策略**: `git checkout --ours`

---

## 风险统计

| 风险等级 | 数量 |
|---------|------|
| 高 | X |
| 中 | Y |
| 低 | Z |
```

---

## 检查点

在进入 Phase 3 之前，确认：

- [ ] 所有冲突文件已分类
- [ ] 核心保护文件已识别
- [ ] 每个文件的处理策略已确定
- [ ] `conflict-analysis.md` 已生成

---

## 决策原则

### 何时使用 `--ours`

1. 上游故意移除本地需要的功能
2. 本地设计与上游设计理念冲突
3. 本地改动是核心业务需求

### 何时手动合并

1. 双方改动都有价值
2. 改动在不同代码区域
3. 可以同时保留双方改动

### 何时重新生成

1. 依赖锁文件 (`package-lock.json`, `pnpm-lock.yaml`)
2. 自动生成的文件
