# 上游同步发现报告

> **生成时间**: {{TIMESTAMP}}
> **当前分支**: {{CURRENT_BRANCH}}
> **上游分支**: {{UPSTREAM_BRANCH}}

---

## 仓库状态

| 指标 | 值 | 说明 |
|------|---|------|
| 本地领先提交数 | {{AHEAD_COUNT}} | git log upstream/develop..HEAD |
| 落后上游提交数 | {{BEHIND_COUNT}} | git log HEAD..upstream/develop |
| 本地改动文件数 | {{LOCAL_FILES_COUNT}} | 相对于 merge-base |
| 上游改动文件数 | {{UPSTREAM_FILES_COUNT}} | 相对于 merge-base |
| 潜在冲突文件数 | {{CONFLICT_FILES_COUNT}} | 双方都修改的文件 |

---

## Merge Base

```
Commit: {{MERGE_BASE}}
```

---

## 上游新提交

| # | Commit | 说明 |
|---|--------|------|
{{UPSTREAM_COMMITS}}

---

## 潜在冲突文件

> 这些文件本地和上游都有修改，可能产生冲突

| # | 文件路径 |
|---|---------|
{{CONFLICT_FILES}}

---

## 本地改动文件清单

### 代码文件

| # | 文件路径 | 改动类型 |
|---|---------|---------|
{{LOCAL_CODE_FILES}}

### 文档文件

| # | 文件路径 | 改动类型 |
|---|---------|---------|
{{LOCAL_DOC_FILES}}

### 配置文件

| # | 文件路径 | 改动类型 |
|---|---------|---------|
{{LOCAL_CONFIG_FILES}}

---

## 上游改动文件清单

| # | 文件路径 |
|---|---------|
{{UPSTREAM_FILES}}

---

## 下一步

进入 **Phase 2: Analysis** 分析冲突风险和保护需求。
