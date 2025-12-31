# Implementation Plan: 上游代码合并

> **生成时间**: {{TIMESTAMP}}
> **基于**: protection-strategy.md

---

## 概述

合并 {{UPSTREAM_BRANCH}} 的 {{COMMIT_COUNT}} 个新提交到本地 fork，同时保护本地的核心改动。

---

## 潜在冲突文件 ({{CONFLICT_COUNT}} 个)

| 文件 | 处理策略 |
|------|---------|
{{CONFLICT_FILES_TABLE}}

---

## Implementation Plan

- [ ] 1. 准备工作
  - 创建备份分支
  - 验证当前工作区干净

- [ ] 1.1 创建备份分支
  - 执行 `git branch backup-$(date +%Y%m%d)`
  - 验证 `git branch | grep backup`

- [ ] 1.2 确保工作区干净
  - 执行 `git status` 确认无未提交改动
  - 如有改动，先提交或暂存

- [ ] 2. 执行合并

- [ ] 2.1 获取上游最新代码
  - 执行 `git fetch upstream`

- [ ] 2.2 执行合并
  - 执行 `git merge {{UPSTREAM_BRANCH}}`

- [ ] 3. 解决冲突 - 核心保护
  - 保护设计冲突文件

{{PROTECTION_TASKS}}

- [ ] 4. 解决冲突 - 手动合并

{{MANUAL_MERGE_TASKS}}

- [ ] 5. 解决冲突 - 重新生成

{{REGENERATE_TASKS}}

- [ ] 6. 完成合并

- [ ] 6.1 标记冲突已解决
  - 执行 `git add .`

- [ ] 6.2 提交合并
  - 执行 `git commit -m "merge: sync with {{UPSTREAM_BRANCH}}, preserve local customizations"`

- [ ] 7. Checkpoint - 确保合并完成
  - 验证合并提交已创建
  - 执行 `git log --oneline -3`

- [ ] 8. 验证

- [ ] 8.1 运行测试
  - 执行 `{{TEST_COMMAND}}`
  - **Validates: 核心功能正常**

- [ ] 8.2 构建验证
  - 执行 `{{BUILD_COMMAND}}`
  - **Validates: 代码可构建**

- [ ] 8.3 核心功能检查
{{CORE_FUNCTION_CHECKS}}

- [ ] 9. 最终 Checkpoint
  - 确保所有验证通过
  - 如有问题，询问用户

---

## 执行命令汇总

### 准备阶段
```bash
git branch backup-$(date +%Y%m%d)
git status
```

### 合并阶段
```bash
git fetch upstream
git merge {{UPSTREAM_BRANCH}}
```

### 冲突解决
```bash
{{ALL_CONFLICT_COMMANDS}}
```

### 完成合并
```bash
git add .
git commit -m "merge: sync with {{UPSTREAM_BRANCH}}, preserve local customizations"
```

### 验证阶段
```bash
{{VERIFY_COMMANDS}}
```

---

## 下一步

按照上述任务清单逐步执行，进入 **Phase 4: Execution**。
