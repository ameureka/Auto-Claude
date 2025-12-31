# Phase 4: Execution (执行合并)

> **目标**: 执行合并并解决冲突
> **输入**: `tasks.md`
> **输出**: Merge Commit

---

## 操作步骤

### Step 4.1: 创建备份分支

```bash
git branch backup-$(date +%Y%m%d)

# 验证备份分支已创建
git branch | grep backup
```

> [!TIP]
> 备份分支允许在合并出问题时快速回滚：
> ```bash
> git reset --hard backup-YYYYMMDD
> ```

### Step 4.2: 确保工作区干净

```bash
git status
```

如果有未提交的改动：
```bash
# 选项 1: 提交改动
git add . && git commit -m "chore: save work before upstream merge"

# 选项 2: 暂存改动
git stash

# 选项 3: 丢弃改动 (谨慎!)
git checkout -- .
```

### Step 4.3: 获取上游最新代码

```bash
git fetch upstream
```

### Step 4.4: 执行合并

```bash
git merge upstream/develop
```

**可能的结果**：

| 结果 | 说明 | 下一步 |
|------|------|--------|
| `Already up to date` | 已是最新 | 无需操作 |
| `Fast-forward` | 快进合并成功 | 跳到验证 |
| `Automatic merge` | 自动合并成功 | 跳到验证 |
| `CONFLICT` | 有冲突需要解决 | 继续 Step 4.5 |

### Step 4.5: 解决冲突 - 强制保留本地

对于 `--ours` 策略的文件：

```bash
# 强制使用本地版本
git checkout --ours apps/backend/core/auth.py
git checkout --ours apps/backend/core/client.py

# 验证关键代码存在
grep "ANTHROPIC_API_KEY" apps/backend/core/auth.py
grep "apply_auth_env" apps/backend/core/client.py
```

### Step 4.6: 解决冲突 - 手动合并

对于需要手动合并的文件，编辑文件解决冲突标记：

```bash
# 查看冲突文件
git status | grep "both modified"

# 编辑文件，解决冲突标记
# <<<<<<< HEAD
# 本地内容
# =======
# 上游内容
# >>>>>>> upstream/develop
```

**手动合并原则**：
1. 保留本地核心配置
2. 合并上游新增内容
3. 删除冲突标记

### Step 4.7: 解决冲突 - 重新生成

对于依赖锁文件：

```bash
# 删除冲突的锁文件
rm apps/frontend/package-lock.json

# 重新生成
cd apps/frontend && pnpm install
```

### Step 4.8: 标记冲突已解决

```bash
git add .

# 验证所有冲突已解决
git status
# 应显示 "All conflicts fixed but you are still merging"
```

### Step 4.9: 完成合并提交

```bash
git commit -m "merge: sync with upstream/develop, preserve local customizations

- Preserve multi-auth support (ANTHROPIC_API_KEY)
- Preserve Chinese i18n support
- Merge upstream new features
- Regenerate package-lock.json"
```

---

## 冲突解决速查表

### 强制保留本地 (--ours)

```bash
git checkout --ours <file>
git add <file>
```

### 强制使用上游 (--theirs)

```bash
git checkout --theirs <file>
git add <file>
```

### 手动合并

```bash
# 1. 打开文件编辑
# 2. 找到冲突标记 <<<<<<<
# 3. 决定保留哪些内容
# 4. 删除冲突标记
# 5. 保存文件
git add <file>
```

### 重新生成

```bash
# package-lock.json / pnpm-lock.yaml
rm <lock-file>
pnpm install  # 或 npm install

git add <lock-file>
```

---

## 常见问题

### Q: 合并后发现遗漏了保护文件？

```bash
# 回滚到合并前
git reset --hard HEAD~1

# 重新合并
git merge upstream/develop

# 这次记得保护文件
git checkout --ours <forgotten-file>
```

### Q: 合并冲突太多，想放弃？

```bash
git merge --abort
```

### Q: 如何查看合并引入了哪些改动？

```bash
# 查看合并提交的改动
git diff HEAD~1..HEAD

# 查看特定文件的改动
git diff HEAD~1..HEAD -- <file>
```

---

## 检查点

在进入 Phase 5 之前，确认：

- [ ] 备份分支已创建
- [ ] 合并已执行
- [ ] 所有冲突已解决
- [ ] 保护文件的关键代码存在
- [ ] 合并提交已创建
- [ ] `git status` 显示工作区干净
