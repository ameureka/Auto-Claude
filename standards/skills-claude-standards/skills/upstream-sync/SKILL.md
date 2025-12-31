# Skill: upstream-sync

> **版本**: 1.0.0
> **作者**: AMEUREKA
> **创建日期**: 2024-12-31
> **触发命令**: `/upstream-sync`

---

## 概述

`upstream-sync` 是一个用于安全同步 Fork 仓库与上游代码的 Skill。它通过 6 个阶段的工作流，确保在合并上游更新时保护本地核心改动（如多认证支持、i18n 定制等）。

### 核心价值

| 特性 | 说明 |
|------|------|
| **保护优先** | 自动识别本地核心改动，优先保护 |
| **FPF 集成** | 可选的第一性原理校验，确保文档准确性 |
| **可追溯** | 每个阶段生成文档，完整记录决策过程 |
| **可恢复** | 自动创建备份分支，支持回滚 |
| **验证闭环** | 测试 + 构建 + 功能检查，确保合并质量 |

---

## 适用场景

- Fork 仓库需要与上游保持同步
- 本地有核心改动需要保护（设计分歧）
- 需要可追溯的合并记录
- 团队协作中的上游同步规范化

---

## 工作流概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     upstream-sync Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1          Phase 2          Phase 3                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │Discovery │───▶│ Analysis │───▶│Protection│                   │
│  │  发现    │    │   分析   │    │   计划   │                   │
│  └──────────┘    └──────────┘    └──────────┘                   │
│       │                               │                          │
│       ▼                               ▼                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │ Publish  │◀───│Validation│◀───│Execution │                   │
│  │   发布   │    │   验证   │    │   执行   │                   │
│  └──────────┘    └──────────┘    └──────────┘                   │
│  Phase 6          Phase 5          Phase 4                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阶段详情

### Phase 1: Discovery (发现)

**目标**: 收集仓库状态信息，识别同步需求

**输入**: Git 仓库
**输出**: `discovery-report.md`

**操作**:
1. `git fetch upstream` 获取上游最新代码
2. 统计本地领先/落后提交数
3. 列出本地改动文件清单
4. 列出上游改动文件清单
5. 识别潜在冲突文件 (`comm -12`)

**关键命令**:
```bash
git fetch upstream
git log --oneline upstream/develop..HEAD  # 本地领先
git log --oneline HEAD..upstream/develop  # 落后上游
git diff --name-only $(git merge-base HEAD upstream/develop) HEAD  # 本地改动
git diff --name-only $(git merge-base HEAD upstream/develop) upstream/develop  # 上游改动
```

→ 详见 [operations/phase1-discovery.md](operations/phase1-discovery.md)

---

### Phase 2: Analysis (分析)

**目标**: 分析冲突风险，识别保护需求

**输入**: `discovery-report.md`
**输出**: `conflict-analysis.md`

**操作**:
1. 分类冲突文件类型
   - 设计冲突：本地与上游设计理念不同
   - 代码冲突：同一文件双方都修改
   - 配置冲突：配置文件冲突
   - 依赖冲突：package-lock.json 等
2. 识别核心保护文件
3. 评估冲突风险等级 (高/中/低)
4. 生成处理策略建议

→ 详见 [operations/phase2-analysis.md](operations/phase2-analysis.md)

---

### Phase 3: Protection Plan (保护计划)

**目标**: 制定保护策略和可执行任务清单

**输入**: `conflict-analysis.md`
**输出**:
- `protection-strategy.md`
- `tasks.md`

**操作**:
1. 定义 `--ours` 强制保留文件列表
2. 定义手动合并文件列表
3. 定义重新生成文件列表
4. 生成可执行的任务清单
5. (可选) FPF 第一性原理校验

**保护策略类型**:
| 策略 | 适用场景 | 命令 |
|------|---------|------|
| `--ours` | 设计冲突，必须保留本地 | `git checkout --ours <file>` |
| 手动合并 | 需要保留双方改动 | 手动编辑解决冲突标记 |
| 重新生成 | 依赖文件 | `pnpm install` / `npm install` |

→ 详见 [operations/phase3-protection.md](operations/phase3-protection.md)

---

### Phase 4: Execution (执行合并)

**目标**: 执行合并并解决冲突

**输入**: `tasks.md`
**输出**: Merge Commit

**操作**:
1. 创建备份分支 `backup-YYYYMMDD`
2. 确保工作区干净
3. 执行 `git merge upstream/develop`
4. 按策略解决冲突
5. `git add .` 标记冲突已解决
6. `git commit` 完成合并

**关键命令**:
```bash
git branch backup-$(date +%Y%m%d)
git merge upstream/develop
git checkout --ours <protected-file>
git add .
git commit -m "merge: sync with upstream/develop, preserve local customizations"
```

→ 详见 [operations/phase4-execution.md](operations/phase4-execution.md)

---

### Phase 5: Validation (验证)

**目标**: 验证合并结果正确性

**输入**: Merge Commit
**输出**: `validation-report.md`

**操作**:
1. 运行测试套件 (`pytest`)
2. 构建验证 (`pnpm build`)
3. 核心功能检查
   - 保护的代码是否存在
   - 关键函数/变量是否保留
4. 上游新功能检查
5. 生成验证报告

**验证清单示例**:
```bash
# 认证测试
pytest tests/test_auth_properties.py -v

# 前端构建
cd apps/frontend && pnpm build

# 核心代码检查
grep "ANTHROPIC_API_KEY" apps/backend/core/auth.py
grep "zh" apps/frontend/src/shared/i18n/index.ts
```

→ 详见 [operations/phase5-validation.md](operations/phase5-validation.md)

---

### Phase 6: Publish (发布)

**目标**: 推送到远程并验证 GitHub 状态

**输入**: `validation-report.md`
**输出**: `sync-summary.md`

**操作**:
1. `git push origin <branch>`
2. 验证 GitHub "commits behind" 状态消失
3. 生成同步摘要报告
4. 更新文档（如需要）

**关键命令**:
```bash
git push origin develop
```

→ 详见 [operations/phase6-publish.md](operations/phase6-publish.md)

---

## 使用方法

### 基本用法

```bash
/upstream-sync
```

执行完整的 6 阶段工作流。

### 带 FPF 校验

```bash
/upstream-sync --fpf
```

在 Phase 3 执行 FPF 第一性原理校验，确保文档准确性。

### 指定保护文件

```bash
/upstream-sync --protect "auth.py,i18n/*"
```

显式指定需要保护的文件模式。

### 仅分析不执行

```bash
/upstream-sync --dry-run
```

只执行 Phase 1-3，生成分析报告但不执行合并。

### 从指定阶段继续

```bash
/upstream-sync --from phase4
```

从指定阶段继续执行（用于中断恢复）。

---

## 输出文件

执行完成后，在 `docs/上下游合并策略/` 目录生成：

```
docs/上下游合并策略/
├── discovery-report.md      # Phase 1 输出
├── conflict-analysis.md     # Phase 2 输出
├── protection-strategy.md   # Phase 3 输出
├── specs/
│   ├── tasks.md             # 执行任务清单
│   └── fpf-review.md        # FPF 校验报告 (可选)
├── validation-report.md     # Phase 5 输出
└── sync-summary.md          # 最终摘要
```

---

## 最佳实践

### 1. 定期同步

建议每周或每次上游有重要更新时执行同步，避免积累过多冲突。

### 2. 保护文件清单

维护一个 `.upstream-sync-protect` 文件，列出需要保护的核心文件：

```
# .upstream-sync-protect
# 多认证系统
apps/backend/core/auth.py
apps/backend/core/client.py
apps/backend/.env.example

# i18n 中文支持
apps/frontend/src/shared/i18n/index.ts
apps/frontend/src/shared/i18n/locales/zh/*
```

### 3. 合并前备份

Skill 会自动创建备份分支，但建议重要合并前手动确认：

```bash
git branch  # 确认 backup-YYYYMMDD 存在
```

### 4. 验证优先

不要跳过 Phase 5 验证，确保：
- 测试通过
- 构建成功
- 核心功能正常

---

## 故障排除

### 合并冲突过多

如果冲突文件超过 10 个，考虑：
1. 分批合并（先合并部分上游提交）
2. 检查是否有不必要的本地改动

### 测试失败

1. 检查是否遗漏了保护文件
2. 检查上游是否有破坏性更改
3. 查看测试日志定位问题

### 推送被拒绝

```bash
# 如果远程有新提交
git pull origin develop --rebase
git push origin develop
```

---

## 相关资源

- [operations/](operations/) - 各阶段详细操作指南
- [templates/](templates/) - 文档模板
- [FPF Skill](../fpf-review/) - 第一性原理校验 Skill

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2024-12-31 | 初始版本，基于 Auto-Claude 上游合并实践 |
