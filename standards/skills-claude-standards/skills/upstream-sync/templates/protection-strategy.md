# 保护策略文档

> **生成时间**: {{TIMESTAMP}}
> **基于**: conflict-analysis.md

---

## 策略概览

| 策略 | 文件数 | 说明 |
|------|--------|------|
| 强制保留本地 (`--ours`) | {{OURS_COUNT}} | 设计冲突，必须保护 |
| 手动合并 | {{MANUAL_COUNT}} | 需要保留双方改动 |
| 重新生成 | {{REGENERATE_COUNT}} | 依赖锁文件等 |
| Git 自动合并 | {{AUTO_COUNT}} | 无冲突或简单冲突 |

---

## 强制保留本地 (`--ours`)

> [!CAUTION]
> 这些文件包含核心设计决策，必须强制保留本地版本！

| # | 文件 | 保护原因 | 验证方法 |
|---|------|---------|---------|
{{OURS_FILES_TABLE}}

### 执行命令

```bash
{{OURS_COMMANDS}}
```

### 验证命令

```bash
{{OURS_VERIFY_COMMANDS}}
```

---

## 手动合并

| # | 文件 | 合并要点 |
|---|------|---------|
{{MANUAL_FILES_TABLE}}

### 合并指南

{{MANUAL_MERGE_GUIDE}}

---

## 重新生成

| # | 文件 | 生成命令 |
|---|------|---------|
{{REGENERATE_FILES_TABLE}}

### 执行命令

```bash
{{REGENERATE_COMMANDS}}
```

---

## Git 自动合并

> 这些文件预计可以自动合并，无需特殊处理

| # | 文件 | 说明 |
|---|------|------|
{{AUTO_FILES_TABLE}}

---

## 合并后验证清单

### 必须验证 ✅

{{MUST_VERIFY_CHECKLIST}}

### 建议验证 ⚠️

{{SHOULD_VERIFY_CHECKLIST}}

---

## 回滚计划

如果合并出现问题，执行以下命令回滚：

```bash
# 回滚到合并前
git reset --hard backup-{{DATE}}

# 或回滚到上一个提交
git reset --hard HEAD~1
```

---

## 下一步

进入 **Phase 4: Execution** 执行合并操作。
