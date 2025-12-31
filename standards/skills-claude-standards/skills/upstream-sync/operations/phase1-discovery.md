# Phase 1: Discovery (发现)

> **目标**: 收集仓库状态信息，识别同步需求
> **输入**: Git 仓库
> **输出**: `discovery-report.md`

---

## 操作步骤

### Step 1.1: 获取上游最新代码

```bash
git fetch upstream
```

确保本地有上游仓库的最新引用。

### Step 1.2: 统计提交差异

```bash
# 本地领先上游的提交数
git log --oneline upstream/develop..HEAD | wc -l

# 落后上游的提交数
git log --oneline HEAD..upstream/develop | wc -l

# 查看上游新提交详情
git log --oneline HEAD..upstream/develop
```

### Step 1.3: 获取 Merge Base

```bash
# 获取共同祖先
MERGE_BASE=$(git merge-base HEAD upstream/develop)
echo "Merge Base: $MERGE_BASE"
```

### Step 1.4: 列出本地改动文件

```bash
# 本地相对于 merge-base 的改动
git diff --name-only $MERGE_BASE HEAD > /tmp/local_changes.txt
cat /tmp/local_changes.txt | wc -l  # 统计数量
```

### Step 1.5: 列出上游改动文件

```bash
# 上游相对于 merge-base 的改动
git diff --name-only $MERGE_BASE upstream/develop > /tmp/upstream_changes.txt
cat /tmp/upstream_changes.txt | wc -l  # 统计数量
```

### Step 1.6: 识别潜在冲突文件

```bash
# 双方都修改的文件 = 潜在冲突
comm -12 \
  <(sort /tmp/local_changes.txt) \
  <(sort /tmp/upstream_changes.txt) > /tmp/conflict_files.txt

cat /tmp/conflict_files.txt
```

---

## 输出模板

生成 `discovery-report.md`：

```markdown
# 上游同步发现报告

> **生成时间**: YYYY-MM-DD HH:MM
> **当前分支**: develop
> **上游分支**: upstream/develop

---

## 仓库状态

| 指标 | 值 | 说明 |
|------|---|------|
| 本地领先提交数 | X | git log upstream/develop..HEAD |
| 落后上游提交数 | Y | git log HEAD..upstream/develop |
| 本地改动文件数 | A | 相对于 merge-base |
| 上游改动文件数 | B | 相对于 merge-base |
| 潜在冲突文件数 | C | 双方都修改的文件 |

---

## 上游新提交

| # | Commit | 说明 |
|---|--------|------|
| 1 | abc1234 | feat: xxx |
| 2 | def5678 | fix: yyy |
| ... | ... | ... |

---

## 潜在冲突文件

| # | 文件路径 |
|---|---------|
| 1 | path/to/file1 |
| 2 | path/to/file2 |
| ... | ... |

---

## 本地核心改动文件

> 需要在 Phase 2 中分析是否需要保护

| # | 文件路径 | 改动类型 |
|---|---------|---------|
| 1 | path/to/file1 | 新增/修改 |
| ... | ... | ... |
```

---

## 检查点

在进入 Phase 2 之前，确认：

- [ ] `git fetch upstream` 执行成功
- [ ] 已统计本地/上游提交差异
- [ ] 已识别潜在冲突文件
- [ ] `discovery-report.md` 已生成

---

## 常见问题

### Q: upstream 远程不存在？

```bash
# 添加 upstream 远程
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO.git
git fetch upstream
```

### Q: 如何查看特定文件的上游改动？

```bash
git diff HEAD..upstream/develop -- path/to/file
```
