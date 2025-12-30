# Skill 文件结构标准

## 概述

本文档定义 Claude Code Skills 的标准文件结构和组织方式，确保所有 Skills 遵循统一的格式，便于维护和使用。

## 目录结构

### 基础结构（简单 Skill）

```
.claude/skills/
└── skill-name/
    └── SKILL.md                 # 主文档（必需）
```

### 标准结构（中等复杂度）

```
.claude/skills/
└── skill-name/
    ├── SKILL.md                 # 主文档（必需）
    └── operations/              # 详细操作指南（可选）
        ├── workflow.md          # 详细工作流
        └── reference.md         # 参考资料
```

### 完整结构（复杂 Skill）

```
.claude/skills/
└── skill-name/
    ├── SKILL.md                 # 主文档（必需）
    ├── operations/              # 详细操作指南（可选）
    │   ├── workflow.md          # 详细工作流
    │   ├── scenarios.md         # 使用场景
    │   ├── reference.md         # 参考资料
    │   ├── troubleshooting.md   # 故障排查
    │   └── advanced.md          # 高级用法
    └── templates/               # 模板文件（可选）
        ├── config.example.yml
        └── checklist.md
```

## 命名规范

### Skill 目录命名

使用 **kebab-case**（小写字母，单词用连字符分隔）：

✅ **正确示例**:
- `version-bump`
- `code-review`
- `seo-strategy`
- `database-migration`

❌ **错误示例**:
- `versionBump` (camelCase)
- `Version_Bump` (snake_case with capitals)
- `version bump` (包含空格)
- `VERSION-BUMP` (全大写)

### 文件命名

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| 主文档 | `SKILL.md` (固定名称) | `SKILL.md` |
| 操作指南 | kebab-case + .md | `workflow.md`, `troubleshooting.md` |
| 模板文件 | kebab-case + 扩展名 | `config.example.yml` |

## SKILL.md 文件结构

### 必需部分

每个 `SKILL.md` **必须**包含以下部分：

```markdown
---
name: skill-name
description: 简短描述（一句话，不超过 100 字符）
---

# Skill 标题

## Quick Reference
[快速参考内容]

## Standard Workflow
[标准工作流步骤]

## Critical Rules
[关键规则]

## Verification Checklist
[验证检查清单]
```

### 可选部分

根据需要可以添加以下章节：

```markdown
## Common Scenarios
[常见使用场景]

## Reference Commands
[参考命令]

## Troubleshooting
[常见问题]

## Related Skills
[相关 Skills]

## Additional Resources
[额外资源]
```

## YAML Frontmatter 规范

### 必需字段

```yaml
---
name: skill-name              # Skill 名称（必需）
description: Brief description # 简短描述（必需）
---
```

### 可选字段

```yaml
---
name: skill-name
description: Brief description
version: 1.0.0                # 版本号
author: Your Name             # 作者
tags:                         # 标签
  - development
  - testing
requires:                     # 依赖的其他 Skills
  - code-review
  - version-bump
updated: 2024-12-20           # 最后更新日期
---
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | Skill 名称，必须与目录名一致 |
| `description` | string | ✅ | 一句话描述，不超过 100 字符 |
| `version` | string | ❌ | 语义化版本号 (semver) |
| `author` | string | ❌ | 作者名称或团队名称 |
| `tags` | array | ❌ | 分类标签，便于搜索 |
| `requires` | array | ❌ | 依赖的其他 Skills |
| `updated` | string | ❌ | 最后更新日期 (YYYY-MM-DD) |

## 章节结构规范

### 1. Quick Reference（快速参考）

**目的**: 提供最常用的信息，让用户快速上手

**内容要求**:
- 核心命令或操作（3-5 条）
- 关键配置或参数
- 最常见的使用场景
- 快速检查清单

**格式示例**:
```markdown
## Quick Reference

**核心命令**:
- `npm run build` - 构建项目
- `npm test` - 运行测试
- `npm run lint` - 代码检查

**关键文件**:
- `package.json` - 项目配置
- `.eslintrc.js` - 代码规范

**快速检查**:
- [ ] 所有测试通过
- [ ] 无 lint 错误
- [ ] 版本号已更新
```

### 2. Standard Workflow（标准工作流）

**目的**: 提供清晰的、分步骤的操作指南

**内容要求**:
- 使用编号列表
- 每个步骤清晰、可执行
- 包含必要的命令和示例
- 说明每个步骤的目的

**格式示例**:
```markdown
## Standard Workflow

### 准备阶段

1. **检查当前分支**
   ```bash
   git branch --show-current
   ```
   确保在正确的分支上工作

2. **拉取最新代码**
   ```bash
   git pull origin main
   ```
   避免合并冲突

### 执行阶段

3. **运行测试**
   ```bash
   npm test
   ```
   确保所有测试通过

4. **构建项目**
   ```bash
   npm run build
   ```
   生成生产版本

### 验证阶段

5. **检查构建产物**
   ```bash
   ls -la dist/
   ```
   确认文件已生成
```

**层级规范**:
- 最多使用 **两级编号**（如 1.1, 1.2）
- 避免过深的嵌套
- 使用小标题分组相关步骤

### 3. Common Scenarios（常见场景）

**目的**: 提供实际使用案例和变体

**内容要求**:
- 3-5 个典型场景
- 每个场景包含背景和解决方案
- 提供具体示例

**格式示例**:
```markdown
## Common Scenarios

### 场景 1: 首次发布

**背景**: 项目第一次发布到生产环境

**步骤**:
1. 设置初始版本号为 `1.0.0`
2. 创建 CHANGELOG.md
3. 配置 CI/CD 流程
4. 执行发布

### 场景 2: 紧急修复

**背景**: 生产环境发现严重 bug，需要快速修复

**步骤**:
1. 从 main 分支创建 hotfix 分支
2. 修复 bug 并测试
3. 更新补丁版本号（如 1.0.0 → 1.0.1）
4. 合并到 main 和 develop
```

### 4. Critical Rules（关键规则）

**目的**: 明确必须遵守和必须避免的规则

**内容要求**:
- 使用 ALWAYS/NEVER 格式
- 每条规则说明原因
- 3-7 条核心规则

**格式示例**:
```markdown
## Critical Rules

### ✅ ALWAYS

1. **ALWAYS 在发布前运行完整测试套件**
   - 原因: 避免将 bug 引入生产环境
   - 命令: `npm test`

2. **ALWAYS 更新 CHANGELOG.md**
   - 原因: 用户需要知道版本变更内容
   - 格式: 遵循 Keep a Changelog 标准

3. **ALWAYS 使用语义化版本号**
   - 原因: 清晰表达变更的影响范围
   - 规则: MAJOR.MINOR.PATCH

### ❌ NEVER

1. **NEVER 直接在 main 分支上提交**
   - 原因: 保护主分支稳定性
   - 替代: 使用 feature 分支 + PR

2. **NEVER 跳过代码审查**
   - 原因: 确保代码质量和知识共享
   - 要求: 至少一人审查批准

3. **NEVER 在未测试的情况下发布**
   - 原因: 避免生产环境故障
   - 要求: 所有测试必须通过
```

### 5. Verification Checklist（验证检查清单）

**目的**: 提供可执行的验证步骤，确保任务正确完成

**内容要求**:
- 使用复选框格式
- 每项可独立验证
- 包含验证方法
- 5-10 个检查项

**格式示例**:
```markdown
## Verification Checklist

### 代码质量

- [ ] 所有测试通过
  ```bash
  npm test
  ```
  预期: 所有测试显示绿色 ✓

- [ ] 无 lint 错误
  ```bash
  npm run lint
  ```
  预期: 0 errors, 0 warnings

- [ ] 代码已审查
  - 至少一人批准 PR
  - 所有评论已解决

### 版本管理

- [ ] 版本号已更新
  - 检查 `package.json` 中的 version 字段
  - 遵循语义化版本规范

- [ ] CHANGELOG.md 已更新
  - 包含本次变更的所有内容
  - 日期和版本号正确

### 发布准备

- [ ] 构建成功
  ```bash
  npm run build
  ```
  预期: dist/ 目录包含所有文件

- [ ] 文档已更新
  - README.md 反映最新功能
  - API 文档已同步

- [ ] Git 标签已创建
  ```bash
  git tag -a v1.0.0 -m "Release version 1.0.0"
  ```
```

### 6. Reference Commands（参考命令）

**目的**: 提供常用命令的快速参考

**格式示例**:
```markdown
## Reference Commands

### Git 操作

```bash
# 创建新分支
git checkout -b feature/new-feature

# 查看状态
git status

# 提交变更
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/new-feature
```

### NPM 操作

```bash
# 安装依赖
npm install

# 运行测试
npm test

# 构建项目
npm run build

# 发布包
npm publish
```

### 版本管理

```bash
# 更新补丁版本 (1.0.0 → 1.0.1)
npm version patch

# 更新次版本 (1.0.0 → 1.1.0)
npm version minor

# 更新主版本 (1.0.0 → 2.0.0)
npm version major
```
```

## Operations 子目录规范

### 何时使用 Operations

当满足以下条件时，应该创建 operations 子目录：

- ✅ 主文档超过 300 行
- ✅ 包含多个复杂的子流程
- ✅ 需要详细的故障排查指南
- ✅ 有高级用法或特殊场景
- ✅ 需要大量的参考资料

### 标准文件

| 文件名 | 用途 | 何时创建 |
|--------|------|---------|
| `workflow.md` | 详细的工作流程 | 主流程超过 20 步 |
| `scenarios.md` | 详细的使用场景 | 有 5+ 个场景 |
| `reference.md` | 参考资料和命令 | 有大量参考内容 |
| `troubleshooting.md` | 故障排查指南 | 有常见问题 |
| `advanced.md` | 高级用法 | 有专家级功能 |

### Operations 文件格式

每个 operations 文件应该遵循以下结构：

```markdown
# [主题名称]

## 概述
[简要说明本文档的内容和目的]

## [章节 1]
[详细内容]

## [章节 2]
[详细内容]

## 相关链接
- [返回主文档](../SKILL.md)
- [其他相关文档](./other.md)
```

## Templates 子目录规范

### 何时使用 Templates

当 Skill 需要用户创建或修改配置文件时：

- ✅ 需要特定格式的配置文件
- ✅ 有标准的检查清单模板
- ✅ 需要生成特定格式的文档

### 模板文件命名

```
templates/
├── config.example.yml       # 配置文件示例
├── checklist.md            # 检查清单模板
├── report-template.md      # 报告模板
└── .gitignore.example      # Git 忽略文件示例
```

**命名规则**:
- 使用 `.example` 后缀表示示例文件
- 使用 `-template` 后缀表示模板文件
- 保持原始文件的扩展名

## 文件大小指南

| 文件类型 | 推荐大小 | 最大大小 | 超过时的处理 |
|---------|---------|---------|-------------|
| SKILL.md | 100-300 行 | 500 行 | 拆分到 operations/ |
| operations/*.md | 50-200 行 | 300 行 | 进一步拆分 |
| 模板文件 | 无限制 | - | - |

## 版本控制

### Git 管理

所有 Skills 应该纳入版本控制：

```bash
# 添加新 Skill
git add .claude/skills/new-skill/

# 提交变更
git commit -m "feat(skills): add new-skill for [purpose]"

# 更新现有 Skill
git commit -m "docs(skills): update version-bump workflow"
```

### 版本号管理

在 YAML frontmatter 中使用语义化版本号：

```yaml
---
name: skill-name
version: 1.2.3
---
```

**版本号规则**:
- **MAJOR** (1.x.x): 不兼容的重大变更
- **MINOR** (x.1.x): 向后兼容的功能新增
- **PATCH** (x.x.1): 向后兼容的问题修复

## 检查清单

创建新 Skill 时，确认以下事项：

### 文件结构
- [ ] 目录名使用 kebab-case
- [ ] 包含 SKILL.md 主文档
- [ ] 如需要，创建 operations/ 子目录
- [ ] 如需要，创建 templates/ 子目录

### SKILL.md 内容
- [ ] 包含完整的 YAML frontmatter
- [ ] 包含 Quick Reference 章节
- [ ] 包含 Standard Workflow 章节
- [ ] 包含 Critical Rules 章节
- [ ] 包含 Verification Checklist 章节
- [ ] 所有章节内容完整

### 质量检查
- [ ] 所有步骤清晰可执行
- [ ] 包含必要的命令示例
- [ ] 验证检查清单可用
- [ ] 文档语言清晰无歧义
- [ ] 已测试实际可用性

### 版本控制
- [ ] 已添加到 Git
- [ ] 提交信息清晰
- [ ] 版本号正确（如使用）

## 示例参考

完整的示例请参考：
- [基础 Skill 示例](../examples/basic-skill-example.md)
- [复杂 Skill 示例](../examples/complex-skill-example.md)
- [Operations 示例](../examples/operations-example.md)
