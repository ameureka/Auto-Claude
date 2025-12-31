# Phase 6: Publish (发布)

> **目标**: 推送到远程并验证 GitHub 状态
> **输入**: `validation-report.md`
> **输出**: `sync-summary.md`

---

## 操作步骤

### Step 6.1: 确认本地状态

```bash
# 确认工作区干净
git status

# 确认合并提交存在
git log --oneline -5

# 确认领先远程的提交数
git log --oneline origin/develop..HEAD
```

### Step 6.2: 推送到远程

```bash
git push origin develop
```

**可能的结果**：

| 结果 | 说明 | 处理方法 |
|------|------|---------|
| 成功 | 推送完成 | 继续 Step 6.3 |
| `rejected` | 远程有新提交 | 见下方处理 |
| `permission denied` | 权限问题 | 检查 SSH/Token |

**如果推送被拒绝**：

```bash
# 拉取远程新提交
git pull origin develop --rebase

# 解决可能的冲突后重新推送
git push origin develop
```

### Step 6.3: 验证 GitHub 状态

1. 打开 GitHub 仓库页面
2. 检查 "commits behind" 状态是否消失
3. 确认分支已更新

**预期结果**：
- 之前显示 "X commits behind" 应该消失
- 分支显示与上游同步

### Step 6.4: 生成同步摘要

记录本次同步的完整信息，便于追溯。

---

## 输出模板

生成 `sync-summary.md`：

```markdown
# 上游同步摘要

> **同步时间**: YYYY-MM-DD HH:MM
> **执行者**: <username>

---

## 同步概览

| 指标 | 值 |
|------|-----|
| 合并提交 | `<commit-hash>` |
| 上游提交数 | X |
| 冲突文件数 | Y |
| 保护文件数 | Z |

---

## 合并的上游提交

| # | Commit | 说明 |
|---|--------|------|
| 1 | abc1234 | feat: xxx (#123) |
| 2 | def5678 | fix: yyy (#456) |
| ... | ... | ... |

---

## 冲突解决记录

| 文件 | 策略 | 说明 |
|------|------|------|
| `auth.py` | `--ours` | 保留多认证支持 |
| `client.py` | `--ours` | 保留认证逻辑 |
| `.env.example` | 手动合并 | 保留 Method 1/2/3 |
| `i18n/index.ts` | 自动合并 | 中文支持保留 |
| `package-lock.json` | 重新生成 | pnpm install |

---

## 保护的核心功能

### 多认证系统 ✅

- `ANTHROPIC_API_KEY` 支持保留
- `apply_auth_env` 函数保留
- `get_token_type` 函数保留
- `.env.example` 包含 Method 1/2/3

### i18n 中文支持 ✅

- 8 个中文翻译文件保留
- `i18n/index.ts` 中文 locale 注册保留

---

## 新增上游功能

| 功能 | 来源 | 说明 |
|------|------|------|
| GitLab 集成 | #254 | 新增 GitLab MR 审查功能 |
| --base-branch | #428 | spec_runner 支持指定基础分支 |
| PR 过滤器 | #423 | PR 审查页面增强 |
| ... | ... | ... |

---

## 验证结果

| 检查项 | 结果 |
|--------|------|
| 测试通过 | ✅ 31/31 passed |
| 构建成功 | ✅ |
| 核心功能 | ✅ |
| GitHub 状态 | ✅ 已同步 |

---

## 后续建议

1. **监控**: 观察是否有用户报告问题
2. **文档**: 如有新功能，更新相关文档
3. **下次同步**: 建议在上游有重要更新时再次同步

---

## 备份信息

| 项目 | 值 |
|------|-----|
| 备份分支 | `backup-YYYYMMDD` |
| 回滚命令 | `git reset --hard backup-YYYYMMDD` |

---

## 相关文件

- [discovery-report.md](discovery-report.md)
- [conflict-analysis.md](conflict-analysis.md)
- [protection-strategy.md](protection-strategy.md)
- [tasks.md](specs/tasks.md)
- [validation-report.md](validation-report.md)
```

---

## 推送后检查清单

### GitHub 页面检查

- [ ] "X commits behind" 消失
- [ ] 分支显示最新提交
- [ ] 没有 CI/CD 失败

### 本地检查

- [ ] `git status` 显示与远程同步
- [ ] 备份分支仍然存在（以防需要回滚）

---

## 常见问题

### Q: 推送后 GitHub 仍显示 "commits behind"？

可能原因：
1. 页面缓存，刷新页面
2. 推送到了错误的分支
3. 上游在你推送期间又有新提交

```bash
# 检查远程状态
git fetch upstream
git log --oneline HEAD..upstream/develop
```

### Q: 如何回滚这次同步？

```bash
# 本地回滚
git reset --hard backup-YYYYMMDD

# 强制推送（谨慎！）
git push origin develop --force
```

### Q: 如何清理备份分支？

```bash
# 确认同步稳定后，可以删除备份分支
git branch -d backup-YYYYMMDD
```

---

## 检查点

同步完成，确认：

- [ ] 推送成功
- [ ] GitHub "commits behind" 消失
- [ ] `sync-summary.md` 已生成
- [ ] 备份分支保留（建议保留 1 周）

---

## 🎉 同步完成！

恭喜完成上游同步！你的 Fork 现在与上游保持同步，同时保留了所有本地核心改动。
