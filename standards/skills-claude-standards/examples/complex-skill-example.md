# 复杂 Skill 示例

这是一个复杂的 Skill 示例，展示如何使用 operations 子目录组织详细内容。

## 文件结构

```
.claude/skills/
└── version-bump/
    ├── SKILL.md
    └── operations/
        ├── workflow.md
        ├── scenarios.md
        └── troubleshooting.md
```

## SKILL.md 内容

```markdown
---
name: version-bump
description: 更新项目版本号并创建 Git 标签
version: 2.1.0
author: Development Team
tags:
  - release
  - versioning
  - git
requires:
  - code-review
updated: 2024-12-20
---

# 版本号更新

## Quick Reference

**一句话说明**: 使用语义化版本规范更新项目版本号

**核心命令**:
- `npm version patch` - 补丁版本 (1.0.0 → 1.0.1)
- `npm version minor` - 次版本 (1.0.0 → 1.1.0)
- `npm version major` - 主版本 (1.0.0 → 2.0.0)

**版本规则**:
- **MAJOR** (x.0.0): 不兼容的 API 变更
- **MINOR** (0.x.0): 向后兼容的功能新增
- **PATCH** (0.0.x): 向后兼容的问题修复

**快速检查**:
- [ ] 所有测试通过
- [ ] CHANGELOG 已更新
- [ ] Git 标签已创建

## Standard Workflow

### 准备阶段

1. **确认当前分支**

   ```bash
   git branch --show-current
   ```

   必须在 `main` 或 `master` 分支

2. **拉取最新代码**

   ```bash
   git pull origin main
   ```

   确保本地代码是最新的

3. **检查工作区状态**

   ```bash
   git status
   ```

   预期: `nothing to commit, working tree clean`

### 执行阶段

4. **运行完整测试**

   ```bash
   npm test
   ```

   预期: 所有测试通过

   详细测试流程见 [operations/workflow.md](./operations/workflow.md#testing)

5. **确定版本类型**

   根据变更内容选择版本类型：
   - 修复 bug → `patch`
   - 新增功能 → `minor`
   - 破坏性变更 → `major`

6. **更新版本号**

   ```bash
   npm version [patch|minor|major]
   ```

   这会自动：
   - 更新 `package.json` 中的版本号
   - 创建 Git commit
   - 创建 Git 标签

   **预期输出**:
   ```text
   v1.2.3
   ```

### 验证阶段

7. **验证版本号**

   ```bash
   node -p "require('./package.json').version"
   ```

   确认版本号正确

8. **检查 Git 标签**

   ```bash
   git tag -l | tail -1
   ```

   确认标签已创建

### 完成阶段

9. **推送到远程**

   ```bash
   git push origin main --tags
   ```

   同时推送代码和标签

10. **验证远程状态**

    在 GitHub/GitLab 上确认：
    - 新的 commit 已推送
    - 新的 tag 已创建

详细工作流程请参考 [operations/workflow.md](./operations/workflow.md)

## Common Scenarios

详细场景说明请参考 [operations/scenarios.md](./operations/scenarios.md)

### 快速场景索引

1. **首次发布** - 从 0.1.0 到 1.0.0
2. **补丁更新** - 修复 bug
3. **功能更新** - 添加新功能
4. **重大更新** - 破坏性变更
5. **预发布版本** - alpha, beta, rc

## Critical Rules

### ✅ ALWAYS

1. **ALWAYS 在 main 分支上更新版本**
   - **原因**: 确保版本历史清晰
   - **方法**: 切换到 main 分支后再执行
   - **验证**: `git branch --show-current` 显示 `main`

2. **ALWAYS 在更新版本前运行测试**
   - **原因**: 避免发布有问题的版本
   - **方法**: `npm test` 必须全部通过
   - **验证**: 测试输出显示 `0 failed`

3. **ALWAYS 更新 CHANGELOG.md**
   - **原因**: 用户需要知道版本变更内容
   - **方法**: 在更新版本前手动更新
   - **格式**: 遵循 [Keep a Changelog](https://keepachangelog.com/) 标准

4. **ALWAYS 使用语义化版本号**
   - **原因**: 清晰表达变更的影响范围
   - **规则**: MAJOR.MINOR.PATCH
   - **参考**: [Semantic Versioning](https://semver.org/)

5. **ALWAYS 推送标签到远程**
   - **原因**: 团队成员需要看到版本标签
   - **方法**: `git push --tags`
   - **验证**: 在 GitHub 上查看 Tags 页面

### ❌ NEVER

1. **NEVER 在 feature 分支上更新版本**
   - **原因**: 版本号应该在主分支上统一管理
   - **后果**: 版本历史混乱，可能产生冲突
   - **替代**: 合并到 main 后再更新版本

2. **NEVER 手动修改版本号**
   - **原因**: 容易出错且不会创建 Git 标签
   - **后果**: 版本号和标签不一致
   - **替代**: 使用 `npm version` 命令

3. **NEVER 跳过测试就更新版本**
   - **原因**: 可能发布有 bug 的版本
   - **后果**: 用户遇到问题，需要紧急修复
   - **替代**: 确保所有测试通过后再更新

4. **NEVER 重用已存在的版本号**
   - **原因**: 版本号必须唯一
   - **后果**: 包管理器可能拒绝发布
   - **替代**: 使用新的版本号

5. **NEVER 删除已发布的版本标签**
   - **原因**: 可能有用户依赖该版本
   - **后果**: 破坏用户的依赖关系
   - **替代**: 发布新版本修复问题

## Verification Checklist

### 代码质量

- [ ] **所有测试通过**
  ```bash
  npm test
  ```
  预期: `Tests: X passed, X total`

- [ ] **无 lint 错误**
  ```bash
  npm run lint
  ```
  预期: `0 errors, 0 warnings`

- [ ] **代码已审查**
  - 至少一人批准 PR
  - 所有评论已解决

### 版本管理

- [ ] **版本号已更新**
  ```bash
  cat package.json | grep version
  ```
  预期: 显示新版本号

- [ ] **版本号符合语义化规范**
  - MAJOR: 不兼容的变更
  - MINOR: 向后兼容的新功能
  - PATCH: 向后兼容的修复

- [ ] **CHANGELOG.md 已更新**
  - 包含本次变更的所有内容
  - 日期和版本号正确
  - 遵循 Keep a Changelog 格式

### Git 管理

- [ ] **Git 标签已创建**
  ```bash
  git tag -l | grep v1.2.3
  ```
  预期: 显示对应的标签

- [ ] **标签格式正确**
  - 格式: `vX.Y.Z`
  - 示例: `v1.2.3`

- [ ] **代码已推送到远程**
  ```bash
  git log origin/main..main
  ```
  预期: 无输出（说明已同步）

- [ ] **标签已推送到远程**
  - 在 GitHub/GitLab 上查看 Tags 页面
  - 确认新标签存在

### 文档

- [ ] **README.md 已更新**（如需要）
  - 版本号引用正确
  - 安装说明准确

- [ ] **API 文档已更新**（如需要）
  - 新功能已记录
  - 废弃功能已标注

## Reference Commands

### NPM Version 命令

```bash
# 补丁版本 (1.0.0 → 1.0.1)
npm version patch

# 次版本 (1.0.0 → 1.1.0)
npm version minor

# 主版本 (1.0.0 → 2.0.0)
npm version major

# 预发布版本
npm version prerelease --preid=alpha  # 1.0.0 → 1.0.1-alpha.0
npm version prerelease --preid=beta   # 1.0.0 → 1.0.1-beta.0
npm version prerelease --preid=rc     # 1.0.0 → 1.0.1-rc.0

# 指定具体版本
npm version 2.0.0

# 不创建 Git 标签（不推荐）
npm version patch --no-git-tag-version
```

### Git 命令

```bash
# 查看所有标签
git tag -l

# 查看最新标签
git tag -l | tail -1

# 查看标签详情
git show v1.2.3

# 推送所有标签
git push --tags

# 推送特定标签
git push origin v1.2.3

# 删除本地标签（谨慎使用）
git tag -d v1.2.3

# 删除远程标签（谨慎使用）
git push origin :refs/tags/v1.2.3
```

### 版本查询

```bash
# 查看当前版本
npm version

# 查看 package.json 中的版本
node -p "require('./package.json').version"

# 查看已发布的版本
npm view <package-name> versions
```

## Troubleshooting

详细故障排查请参考 [operations/troubleshooting.md](./operations/troubleshooting.md)

### 常见问题快速索引

1. **工作区不干净** - 有未提交的变更
2. **版本号冲突** - 标签已存在
3. **推送失败** - 权限或网络问题
4. **测试失败** - 无法更新版本

## Related Skills

- `/changelog-update` - 更新变更日志
- `/release-notes` - 生成发布说明
- `/npm-publish` - 发布到 npm
- `/github-release` - 创建 GitHub Release

## Additional Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [npm version 文档](https://docs.npmjs.com/cli/v8/commands/npm-version)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

## Changelog

### v2.1.0 (2024-12-20)
- 添加预发布版本支持
- 更新故障排查指南
- 添加更多使用场景

### v2.0.0 (2024-11-01)
- 重构文档结构，使用 operations 子目录
- 添加详细的验证清单
- 改进错误处理指南

### v1.0.0 (2024-09-15)
- 初始版本
```

## operations/workflow.md 内容

```markdown
# 详细工作流程

本文档提供版本更新的详细工作流程说明。

## 概述

版本更新是一个严格的流程，需要确保代码质量、文档完整性和版本一致性。

## 完整工作流程

### 阶段 1: 准备工作 (5-10 分钟)

#### 1.1 环境检查

**检查 Node.js 版本**:
```bash
node --version
```
要求: v16.0.0 或更高

**检查 npm 版本**:
```bash
npm --version
```
要求: v8.0.0 或更高

**检查 Git 配置**:
```bash
git config user.name
git config user.email
```
确保配置正确

#### 1.2 分支管理

**确认当前分支**:
```bash
git branch --show-current
```
必须在 `main` 或 `master` 分支

**如果不在主分支**:
```bash
git checkout main
```

**拉取最新代码**:
```bash
git pull origin main --rebase
```

**检查是否有冲突**:
```bash
git status
```
如果有冲突，先解决冲突

#### 1.3 工作区清理

**检查未提交的变更**:
```bash
git status
```

**如果有未提交的变更**:

选项 A - 提交变更:
```bash
git add .
git commit -m "chore: prepare for version bump"
```

选项 B - 暂存变更:
```bash
git stash
```

选项 C - 放弃变更:
```bash
git reset --hard HEAD
```

### 阶段 2: 质量检查 (10-20 分钟)

#### 2.1 依赖检查

**安装依赖**:
```bash
npm ci  # 比 npm install 更快更可靠
```

**检查过期依赖**:
```bash
npm outdated
```

**检查安全漏洞**:
```bash
npm audit
```

如果有高危漏洞，先修复:
```bash
npm audit fix
```

#### 2.2 代码质量检查 {#testing}

**运行 linter**:
```bash
npm run lint
```

如果有错误:
```bash
npm run lint:fix
```

**运行类型检查**（如果使用 TypeScript）:
```bash
npm run type-check
```

**运行单元测试**:
```bash
npm test
```

**运行集成测试**:
```bash
npm run test:integration
```

**运行端到端测试**:
```bash
npm run test:e2e
```

**生成测试覆盖率报告**:
```bash
npm run test:coverage
```

检查覆盖率是否达标（通常要求 > 80%）

#### 2.3 构建验证

**运行生产构建**:
```bash
npm run build
```

**检查构建产物**:
```bash
ls -lh dist/
```

确认文件已生成且大小合理

**本地测试构建产物**:
```bash
npm run serve:dist
```

在浏览器中测试功能是否正常

### 阶段 3: 文档更新 (10-15 分钟)

#### 3.1 更新 CHANGELOG.md

**添加新版本条目**:

```markdown
## [1.2.3] - 2024-12-20

### Added
- 新增功能 A
- 新增功能 B

### Changed
- 修改功能 C
- 优化功能 D

### Fixed
- 修复 bug E
- 修复 bug F

### Deprecated
- 废弃功能 G

### Removed
- 移除功能 H

### Security
- 修复安全漏洞 I
```

**提交 CHANGELOG**:
```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for v1.2.3"
```

#### 3.2 更新其他文档

**更新 README.md**（如需要）:
- 版本号引用
- 安装说明
- 使用示例

**更新 API 文档**（如需要）:
- 新增 API
- 修改的 API
- 废弃的 API

**提交文档变更**:
```bash
git add README.md docs/
git commit -m "docs: update documentation for v1.2.3"
```

### 阶段 4: 版本更新 (2-5 分钟)

#### 4.1 确定版本类型

**分析变更内容**:

查看自上次发布以来的提交:
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

**决策规则**:
- 有 `BREAKING CHANGE` → `major`
- 有 `feat:` → `minor`
- 只有 `fix:` → `patch`

#### 4.2 执行版本更新

**更新版本号**:
```bash
npm version [patch|minor|major] -m "chore: bump version to %s"
```

`%s` 会被替换为新版本号

**验证更新**:
```bash
git log -1
git tag -l | tail -1
cat package.json | grep version
```

### 阶段 5: 发布 (5-10 分钟)

#### 5.1 推送到远程

**推送代码**:
```bash
git push origin main
```

**推送标签**:
```bash
git push origin --tags
```

或者一次性推送:
```bash
git push origin main --tags
```

#### 5.2 验证远程状态

**在 GitHub/GitLab 上检查**:
1. 访问仓库页面
2. 查看 Commits - 确认最新提交
3. 查看 Tags - 确认新标签
4. 查看 Releases - 准备创建 Release

#### 5.3 创建 Release（可选）

**在 GitHub 上**:
1. 进入 Releases 页面
2. 点击 "Draft a new release"
3. 选择刚创建的标签
4. 填写 Release 标题和说明
5. 从 CHANGELOG 复制内容
6. 发布 Release

**使用 GitHub CLI**:
```bash
gh release create v1.2.3 --title "v1.2.3" --notes-file CHANGELOG.md
```

### 阶段 6: 后续工作 (5-10 分钟)

#### 6.1 通知团队

**发送通知**:
- Slack/Discord 消息
- 邮件通知
- 项目管理工具更新

**通知内容**:
```
🎉 新版本发布: v1.2.3

主要变更:
- 新增功能 A
- 修复 bug B
- 性能优化 C

详细信息: https://github.com/org/repo/releases/tag/v1.2.3
```

#### 6.2 更新依赖项目

**如果是库项目**:
- 通知依赖此库的项目更新版本
- 更新示例项目
- 更新文档站点

#### 6.3 监控

**监控指标**:
- 下载量
- 错误报告
- 用户反馈

**设置告警**:
- 错误率异常
- 性能下降
- 兼容性问题

## 时间估算

| 阶段 | 预计时间 | 说明 |
|------|---------|------|
| 准备工作 | 5-10 分钟 | 环境检查、分支管理 |
| 质量检查 | 10-20 分钟 | 测试、构建验证 |
| 文档更新 | 10-15 分钟 | CHANGELOG、README |
| 版本更新 | 2-5 分钟 | 执行 npm version |
| 发布 | 5-10 分钟 | 推送、创建 Release |
| 后续工作 | 5-10 分钟 | 通知、监控 |
| **总计** | **37-70 分钟** | 根据项目复杂度 |

## 自动化建议

可以创建脚本自动化部分流程:

```bash
#!/bin/bash
# release.sh

set -e

echo "🔍 Running checks..."
npm run lint
npm test
npm run build

echo "📝 Updating changelog..."
# 提示用户更新 CHANGELOG

echo "🏷️  Bumping version..."
npm version $1

echo "🚀 Pushing to remote..."
git push origin main --tags

echo "✅ Done!"
```

使用方式:
```bash
./release.sh patch  # 或 minor, major
```

## 相关链接

- [返回主文档](../SKILL.md)
- [查看使用场景](./scenarios.md)
- [查看故障排查](./troubleshooting.md)
```

## 说明

这个复杂示例展示了：

1. **主文档简洁** - SKILL.md 保持简洁，详细内容在 operations/
2. **模块化组织** - 将详细工作流、场景、故障排查分离
3. **内部链接** - 主文档和子文档之间相互链接
4. **完整的元数据** - 包含版本、作者、依赖等信息
5. **渐进式披露** - 从快速参考到详细流程
6. **实用的工具** - 提供脚本和自动化建议

这种结构适合复杂的、需要详细说明的 Skills。
