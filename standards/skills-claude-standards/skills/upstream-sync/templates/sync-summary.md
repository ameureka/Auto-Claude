# 上游同步摘要

> **同步时间**: {{TIMESTAMP}}
> **执行者**: {{EXECUTOR}}

---

## 同步概览

| 指标 | 值 |
|------|-----|
| 合并提交 | `{{MERGE_COMMIT}}` |
| 上游提交数 | {{UPSTREAM_COMMIT_COUNT}} |
| 冲突文件数 | {{CONFLICT_COUNT}} |
| 保护文件数 | {{PROTECTED_COUNT}} |

---

## 合并的上游提交

| # | Commit | 说明 |
|---|--------|------|
{{UPSTREAM_COMMITS_TABLE}}

---

## 冲突解决记录

| 文件 | 策略 | 说明 |
|------|------|------|
{{CONFLICT_RESOLUTION_TABLE}}

---

## 保护的核心功能

### {{CORE_FEATURE_1_NAME}} ✅

{{CORE_FEATURE_1_DETAILS}}

### {{CORE_FEATURE_2_NAME}} ✅

{{CORE_FEATURE_2_DETAILS}}

---

## 新增上游功能

| 功能 | 来源 | 说明 |
|------|------|------|
{{NEW_FEATURES_TABLE}}

---

## 验证结果

| 检查项 | 结果 |
|--------|------|
| 测试通过 | {{TEST_RESULT}} |
| 构建成功 | {{BUILD_RESULT}} |
| 核心功能 | {{CORE_RESULT}} |
| GitHub 状态 | {{GITHUB_RESULT}} |

---

## 后续建议

1. **监控**: 观察是否有用户报告问题
2. **文档**: 如有新功能，更新相关文档
3. **下次同步**: 建议在上游有重要更新时再次同步

---

## 备份信息

| 项目 | 值 |
|------|-----|
| 备份分支 | `backup-{{DATE}}` |
| 回滚命令 | `git reset --hard backup-{{DATE}}` |

---

## 相关文件

- [discovery-report.md](discovery-report.md)
- [conflict-analysis.md](conflict-analysis.md)
- [protection-strategy.md](protection-strategy.md)
- [tasks.md](specs/tasks.md)
- [validation-report.md](validation-report.md)

---

## 🎉 同步完成！

Fork 已与上游同步，核心改动已保护。
