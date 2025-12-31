# Phase 3: Protection Plan (保护计划)

> **目标**: 制定保护策略和可执行任务清单
> **输入**: `conflict-analysis.md`
> **输出**: `protection-strategy.md`, `tasks.md`

---

## 操作步骤

### Step 3.1: 制定保护策略

基于 Phase 2 的分析，为每个冲突文件制定具体策略：

| 策略类型 | 命令 | 适用场景 |
|---------|------|---------|
| **强制保留本地** | `git checkout --ours <file>` | 设计冲突，必须保留本地 |
| **强制使用上游** | `git checkout --theirs <file>` | 本地改动可丢弃 |
| **手动合并** | 编辑文件解决冲突标记 | 需要保留双方改动 |
| **重新生成** | `pnpm install` 等 | 依赖锁文件 |

### Step 3.2: 定义保护文件列表

```markdown
## 强制保留本地 (--ours)

| 文件 | 保护原因 |
|------|---------|
| `apps/backend/core/auth.py` | 多认证系统核心 |
| `apps/backend/core/client.py` | 认证逻辑集成 |

## 手动合并

| 文件 | 合并要点 |
|------|---------|
| `apps/backend/.env.example` | 保留本地认证配置，合并上游新配置 |
| `apps/frontend/src/shared/i18n/index.ts` | 保留中文 locale，合并上游新 locale |

## 重新生成

| 文件 | 生成命令 |
|------|---------|
| `apps/frontend/package-lock.json` | `cd apps/frontend && pnpm install` |
```

### Step 3.3: 生成任务清单

将保护策略转化为可执行的任务清单：

```markdown
## Implementation Plan

- [ ] 1. 准备工作
  - [ ] 1.1 创建备份分支
  - [ ] 1.2 确保工作区干净

- [ ] 2. 执行合并
  - [ ] 2.1 获取上游最新代码
  - [ ] 2.2 执行合并

- [ ] 3. 解决冲突 - 核心保护
  - [ ] 3.1 保护 auth.py (--ours)
  - [ ] 3.2 保护 client.py (--ours)

- [ ] 4. 解决冲突 - 手动合并
  - [ ] 4.1 手动合并 .env.example
  - [ ] 4.2 手动合并 i18n/index.ts

- [ ] 5. 解决冲突 - 重新生成
  - [ ] 5.1 重新生成 package-lock.json

- [ ] 6. 完成合并
  - [ ] 6.1 标记冲突已解决 (git add .)
  - [ ] 6.2 提交合并 (git commit)

- [ ] 7. 验证
  - [ ] 7.1 运行测试
  - [ ] 7.2 构建验证
  - [ ] 7.3 核心功能检查
```

### Step 3.4: (可选) FPF 第一性原理校验

如果启用 `--fpf` 选项，执行 FPF 校验：

```markdown
## FPF 校验维度

| 维度 | 检查项 | 预期分数 |
|------|--------|---------|
| D1: 数据准确性 | 文件数、提交数与 Git 一致 | ≥0.95 |
| D2: 文件清单准确性 | 冲突文件列表完整 | ≥0.95 |
| D3: 策略合理性 | 保护策略与分析一致 | ≥0.95 |

## R_eff 计算

R_eff = min(D1, D2, D3)

- R_eff ≥ 0.95: 直接执行
- R_eff 0.90-0.94: 小幅修正后执行
- R_eff < 0.90: 重新分析
```

---

## 输出模板

### protection-strategy.md

```markdown
# 保护策略文档

> **生成时间**: YYYY-MM-DD HH:MM
> **基于**: conflict-analysis.md

---

## 策略概览

| 策略 | 文件数 |
|------|--------|
| 强制保留本地 (--ours) | X |
| 手动合并 | Y |
| 重新生成 | Z |

---

## 强制保留本地 (--ours)

> [!CAUTION]
> 这些文件包含核心设计决策，必须强制保留本地版本

| # | 文件 | 保护原因 | 验证方法 |
|---|------|---------|---------|
| 1 | `apps/backend/core/auth.py` | 多认证系统 | `grep ANTHROPIC_API_KEY` |
| 2 | `apps/backend/core/client.py` | 认证逻辑 | `grep apply_auth_env` |

### 执行命令

```bash
git checkout --ours apps/backend/core/auth.py
git checkout --ours apps/backend/core/client.py
```

---

## 手动合并

| # | 文件 | 合并要点 |
|---|------|---------|
| 1 | `.env.example` | 保留 Method 1/2/3 认证配置 |
| 2 | `i18n/index.ts` | 保留中文 locale 注册 |

### 合并指南

#### .env.example

保留本地的认证配置部分：
```
# Method 1: OAuth Token (recommended)
# Method 2: API Key (direct billing)
# Method 3: Proxy/Enterprise
```

合并上游的新配置项（如有）。

---

## 重新生成

| # | 文件 | 生成命令 |
|---|------|---------|
| 1 | `package-lock.json` | `cd apps/frontend && pnpm install` |

---

## 合并后验证清单

- [ ] `ANTHROPIC_API_KEY` 存在于 `auth.py`
- [ ] `apply_auth_env` 函数存在于 `client.py`
- [ ] 中文 locale 注册于 `i18n/index.ts`
- [ ] 测试通过
- [ ] 构建成功
```

### tasks.md

```markdown
# Implementation Plan: 上游代码合并

## 概述

合并 upstream/develop 到本地 fork，保护核心改动。

---

## 潜在冲突文件

| 文件 | 处理策略 |
|------|---------|
| `auth.py` | `--ours` 保留本地 |
| `client.py` | `--ours` 保留本地 |
| `.env.example` | 手动合并 |
| `i18n/index.ts` | 手动合并 |
| `package-lock.json` | 重新生成 |

---

## Implementation Plan

- [ ] 1. 准备工作
- [ ] 1.1 创建备份分支
  - 执行 `git branch backup-$(date +%Y%m%d)`
- [ ] 1.2 确保工作区干净
  - 执行 `git status` 确认无未提交改动

- [ ] 2. 执行合并
- [ ] 2.1 获取上游最新代码
  - 执行 `git fetch upstream`
- [ ] 2.2 执行合并
  - 执行 `git merge upstream/develop`

- [ ] 3. 解决冲突 - 核心保护
- [ ] 3.1 保护 auth.py
  - 执行 `git checkout --ours apps/backend/core/auth.py`
  - 验证 `ANTHROPIC_API_KEY` 存在
- [ ] 3.2 保护 client.py
  - 执行 `git checkout --ours apps/backend/core/client.py`

- [ ] 4. 解决冲突 - 手动合并
- [ ] 4.1 手动合并 .env.example
  - 保留本地认证配置
  - 合并上游新配置项
- [ ] 4.2 手动合并 i18n/index.ts
  - 保留中文 locale 注册

- [ ] 5. 解决冲突 - 重新生成
- [ ] 5.1 重新生成 package-lock.json
  - 执行 `cd apps/frontend && pnpm install`

- [ ] 6. 完成合并
- [ ] 6.1 标记冲突已解决
  - 执行 `git add .`
- [ ] 6.2 提交合并
  - 执行 `git commit -m "merge: sync with upstream/develop, preserve local customizations"`

- [ ] 7. Checkpoint
  - 确保合并提交已创建

- [ ] 8. 验证
- [ ] 8.1 运行测试
  - 执行 `pytest tests/test_auth_properties.py -v`
- [ ] 8.2 构建验证
  - 执行 `cd apps/frontend && pnpm build`
- [ ] 8.3 核心功能检查
  - 验证多认证支持
  - 验证中文 i18n

- [ ] 9. 最终 Checkpoint
  - 确保所有验证通过
```

---

## 检查点

在进入 Phase 4 之前，确认：

- [ ] 保护策略已制定
- [ ] 任务清单已生成
- [ ] (可选) FPF 校验通过
- [ ] `protection-strategy.md` 已生成
- [ ] `tasks.md` 已生成
