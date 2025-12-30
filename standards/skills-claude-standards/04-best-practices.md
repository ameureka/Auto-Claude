# Skills 最佳实践与设计模式

## 概述

本文档总结 Claude Code Skills 开发的最佳实践、常见设计模式和实用技巧，帮助你创建高质量、可维护的 Skills。

## 设计模式

### 1. 检查清单模式 (Checklist Pattern)

**适用场景**: 需要执行多个独立检查项的任务

**结构**:
```markdown
## Verification Checklist

### 代码质量
- [ ] 所有测试通过
- [ ] 无 lint 错误
- [ ] 代码已审查

### 文档
- [ ] README 已更新
- [ ] API 文档已同步
- [ ] CHANGELOG 已更新
```

**优点**:
- 清晰的验证步骤
- 不易遗漏关键项
- 可以逐项完成

**示例 Skills**: `/code-review`, `/pre-release-check`

### 2. 工作流模式 (Workflow Pattern)

**适用场景**: 需要按顺序执行的多步骤流程

**结构**:
```markdown
## Standard Workflow

### 准备阶段
1. 检查前提条件
2. 准备环境

### 执行阶段
3. 执行主要操作
4. 验证结果

### 完成阶段
5. 清理和收尾
6. 记录和通知
```

**优点**:
- 步骤清晰有序
- 易于跟踪进度
- 便于错误恢复

**示例 Skills**: `/version-bump`, `/deploy`

### 3. 场景驱动模式 (Scenario-Driven Pattern)

**适用场景**: 根据不同情况有不同处理方式的任务

**结构**:
```markdown
## Common Scenarios

### 场景 1: 首次发布
[特定步骤]

### 场景 2: 补丁更新
[特定步骤]

### 场景 3: 重大版本升级
[特定步骤]
```

**优点**:
- 针对性强
- 避免不必要的步骤
- 更贴近实际使用

**示例 Skills**: `/release-management`, `/migration`

### 4. 决策树模式 (Decision Tree Pattern)

**适用场景**: 需要根据条件选择不同路径的任务

**结构**:
```markdown
## Decision Flow

1. **检查项目类型**
   - 如果是 Node.js 项目 → 执行步骤 A
   - 如果是 Python 项目 → 执行步骤 B
   - 如果是其他类型 → 执行步骤 C

2. **根据环境选择**
   - 开发环境 → 使用配置 X
   - 生产环境 → 使用配置 Y
```

**优点**:
- 灵活适应不同情况
- 逻辑清晰
- 减少不必要的操作

**示例 Skills**: `/environment-setup`, `/build-config`

### 5. 模板生成模式 (Template Generation Pattern)

**适用场景**: 需要创建标准化文件或配置的任务

**结构**:
```markdown
## Standard Workflow

1. **选择模板类型**
   - 基础模板
   - 高级模板
   - 自定义模板

2. **填充变量**
   - 项目名称: [输入]
   - 版本号: [输入]
   - 作者: [输入]

3. **生成文件**
   使用 templates/ 目录中的模板
```

**优点**:
- 确保一致性
- 减少手动错误
- 加速创建过程

**示例 Skills**: `/init-project`, `/create-component`

### 6. 渐进式增强模式 (Progressive Enhancement Pattern)

**适用场景**: 基础功能必需，高级功能可选的任务

**结构**:
```markdown
## Quick Start (基础)
[最小化步骤]

## Standard Workflow (标准)
[完整步骤]

## Advanced Usage (高级)
详见 operations/advanced.md
```

**优点**:
- 降低入门门槛
- 支持不同熟练度用户
- 避免信息过载

**示例 Skills**: `/testing`, `/optimization`

## 最佳实践

### 1. 命名规范

#### Skill 命名

**原则**: 动词 + 名词，清晰表达功能

✅ **好的命名**:
- `version-bump` - 更新版本号
- `code-review` - 代码审查
- `deploy-production` - 生产部署
- `generate-docs` - 生成文档

❌ **不好的命名**:
- `vb` - 太简短，不清晰
- `do-stuff` - 太模糊
- `version-bump-and-release` - 太长，职责不单一
- `helper` - 不明确

#### 章节命名

**原则**: 使用标准名称，保持一致性

**标准章节名**:
- `Quick Reference` (不是 "Quick Start" 或 "Overview")
- `Standard Workflow` (不是 "Steps" 或 "Process")
- `Common Scenarios` (不是 "Examples" 或 "Use Cases")
- `Critical Rules` (不是 "Important" 或 "Notes")
- `Verification Checklist` (不是 "Checks" 或 "Validation")

### 2. 粒度控制

#### 单一职责

每个 Skill 只做一件事：

✅ **好的粒度**:
```
/version-bump     - 只更新版本号
/update-changelog - 只更新变更日志
/git-tag          - 只创建 Git 标签
```

❌ **不好的粒度**:
```
/release - 包含版本更新、变更日志、标签、构建、部署等所有内容
```

#### 组合使用

通过组合多个 Skills 完成复杂任务：

```markdown
## Related Skills

完整的发布流程需要依次执行：
1. `/version-bump` - 更新版本号
2. `/update-changelog` - 更新变更日志
3. `/run-tests` - 运行测试
4. `/build` - 构建项目
5. `/git-tag` - 创建标签
6. `/deploy` - 部署
```

### 3. 文档组织

#### 信息层次

遵循"金字塔原则"：

```
Level 1: Quick Reference (最常用，80% 的场景)
    ↓
Level 2: Standard Workflow (标准流程，15% 的场景)
    ↓
Level 3: Common Scenarios (特殊场景，4% 的场景)
    ↓
Level 4: operations/ (高级用法，1% 的场景)
```

#### 渐进式披露

不要一次性展示所有信息：

```markdown
## Quick Reference
[核心信息，5-10 行]

## Standard Workflow
[标准流程，20-30 步]

详细说明请参考 [operations/workflow.md](./operations/workflow.md)

## Advanced Usage
详见 [operations/advanced.md](./operations/advanced.md)
```

### 4. 错误处理

#### 预防性检查

在执行前检查前提条件：

```markdown
1. **检查前提条件**

   ```bash
   # 检查 Node.js 版本
   node --version
   ```

   要求: v18.0.0 或更高

   如果版本过低，请先升级 Node.js
```

#### 错误恢复

提供错误恢复方法：

```markdown
3. **执行构建**

   ```bash
   npm run build
   ```

   **如果构建失败**:

   1. 清理缓存
      ```bash
      rm -rf node_modules dist
      npm install
      ```

   2. 重新构建
      ```bash
      npm run build
      ```
```

#### 回滚机制

对于有风险的操作，提供回滚方法：

```markdown
## Rollback Procedure

如果发布后发现问题，执行以下步骤回滚：

1. **恢复代码**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **重新部署**
   ```bash
   npm run deploy
   ```
```

### 5. 验证和测试

#### 内置验证

每个关键步骤都应该有验证：

```markdown
2. **安装依赖**

   ```bash
   npm install
   ```

   **验证**: 检查 node_modules 目录存在
   ```bash
   ls node_modules
   ```
```

#### 端到端验证

在最后提供完整的验证清单：

```markdown
## Verification Checklist

### 功能验证
- [ ] 所有功能正常工作
- [ ] 无控制台错误
- [ ] 性能符合预期

### 文档验证
- [ ] README 准确
- [ ] API 文档完整
- [ ] 示例代码可运行

### 发布验证
- [ ] 版本号正确
- [ ] 标签已创建
- [ ] 部署成功
```

### 6. 可维护性

#### 版本管理

在 frontmatter 中记录版本：

```yaml
---
name: skill-name
version: 1.2.0
updated: 2024-12-20
---
```

#### 变更日志

在文档末尾添加变更历史：

```markdown
## Changelog

### v1.2.0 (2024-12-20)
- 添加自动化测试步骤
- 更新依赖版本要求

### v1.1.0 (2024-11-15)
- 添加错误处理指南
- 优化工作流程

### v1.0.0 (2024-10-01)
- 初始版本
```

#### 定期审查

建立定期审查机制：

```markdown
> **维护提示**: 本文档应每季度审查一次，确保与最新工具和最佳实践保持同步
```

### 7. 用户体验

#### 清晰的预期

明确告诉用户每个步骤的预期结果：

```markdown
1. **运行测试**

   ```bash
   npm test
   ```

   **预期输出**:
   ```text
   Test Suites: 5 passed, 5 total
   Tests:       42 passed, 42 total
   ```

   **执行时间**: 约 30 秒
```

#### 进度指示

对于长时间操作，提供进度指示：

```markdown
3. **构建项目** (预计 2-3 分钟)

   ```bash
   npm run build
   ```

   构建过程中会看到：
   - ⏳ Compiling...
   - ✓ Compiled successfully
```

#### 友好的错误信息

提供清晰的错误说明和解决方法：

```markdown
**常见错误**:

❌ `Error: EACCES: permission denied`

   **原因**: 没有文件写入权限

   **解决**:
   ```bash
   sudo chown -R $USER:$USER .
   ```
```

## 常见陷阱

### ❌ 避免的错误

#### 1. 假设用户知识

❌ **错误**:
```markdown
运行 linter 检查代码
```

✅ **正确**:
```markdown
运行 ESLint 检查代码规范

```bash
npm run lint
```

ESLint 是 JavaScript 代码检查工具，会检查代码风格和潜在错误
```

#### 2. 缺少验证步骤

❌ **错误**:
```markdown
1. 安装依赖
2. 运行测试
3. 构建项目
```

✅ **正确**:
```markdown
1. 安装依赖
   ```bash
   npm install
   ```
   验证: 检查 node_modules 目录存在

2. 运行测试
   ```bash
   npm test
   ```
   验证: 所有测试通过（绿色 ✓）

3. 构建项目
   ```bash
   npm run build
   ```
   验证: dist/ 目录包含构建文件
```

#### 3. 步骤过于笼统

❌ **错误**:
```markdown
1. 准备环境
2. 执行操作
3. 完成任务
```

✅ **正确**:
```markdown
1. 检查 Node.js 版本 (需要 v18+)
2. 安装项目依赖
3. 配置环境变量
4. 运行数据库迁移
5. 启动开发服务器
```

#### 4. 忽略错误情况

❌ **错误**:
```markdown
运行 `npm install` 安装依赖
```

✅ **正确**:
```markdown
运行 `npm install` 安装依赖

如果遇到网络错误，尝试：
```bash
npm install --registry=https://registry.npmmirror.com
```
```

#### 5. 文档过时

❌ **错误**:
```markdown
运行 `gulp build` 构建项目
```
(项目已经改用 webpack)

✅ **正确**:
```markdown
运行 `npm run build` 构建项目

> 注意: v2.0 之前使用 gulp，现已迁移到 webpack
```

## 高级技巧

### 1. 条件执行

提供基于条件的不同路径：

```markdown
2. **选择构建模式**

   **开发模式** (快速，包含 source maps):
   ```bash
   npm run build:dev
   ```

   **生产模式** (优化，压缩):
   ```bash
   npm run build:prod
   ```

   **分析模式** (包含 bundle 分析):
   ```bash
   npm run build:analyze
   ```
```

### 2. 参数化操作

支持自定义参数：

```markdown
3. **创建 Git 标签**

   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```

   替换 `v1.0.0` 为实际版本号
   替换消息内容为实际的发布说明
```

### 3. 自动化脚本

提供可复制的自动化脚本：

```markdown
## Quick Script

如果需要一键执行所有步骤，可以使用以下脚本：

```bash
#!/bin/bash
set -e

echo "Running tests..."
npm test

echo "Building project..."
npm run build

echo "Creating tag..."
git tag -a v1.0.0 -m "Release v1.0.0"

echo "Done!"
```

保存为 `release.sh` 并执行 `chmod +x release.sh && ./release.sh`
```

### 4. 集成其他工具

与其他 Skills 或工具集成：

```markdown
## Integration

### 与 Agent Foreman 集成

```bash
# 初始化项目
/agent-foreman:init

# 执行当前 Skill
/version-bump

# 标记任务完成
/agent-foreman:done
```

### 与 CI/CD 集成

在 `.github/workflows/release.yml` 中使用：
```yaml
- name: Bump version
  run: npm version patch
```
```

### 5. 性能优化

提供性能优化建议：

```markdown
## Performance Tips

### 加速构建

1. **使用缓存**
   ```bash
   npm ci  # 比 npm install 更快
   ```

2. **并行执行**
   ```bash
   npm run lint & npm run test  # 并行运行
   wait
   ```

3. **增量构建**
   ```bash
   npm run build -- --incremental
   ```
```

## 质量检查清单

创建 Skill 后，使用此清单确保质量：

### 结构完整性
- [ ] 包含所有必需章节
- [ ] YAML frontmatter 完整
- [ ] 文件命名符合规范
- [ ] 目录结构正确

### 内容质量
- [ ] 步骤清晰可执行
- [ ] 包含验证方法
- [ ] 提供错误处理
- [ ] 示例真实可用

### 用户体验
- [ ] 新人能够理解
- [ ] 预期结果明确
- [ ] 错误信息友好
- [ ] 文档易于导航

### 可维护性
- [ ] 版本号已标注
- [ ] 更新日期准确
- [ ] 有变更历史
- [ ] 定期审查计划

### 实际测试
- [ ] 按文档执行成功
- [ ] 验证清单有效
- [ ] 错误处理正确
- [ ] 性能可接受

## 持续改进

### 收集反馈

建立反馈机制：

```markdown
## Feedback

如果你在使用过程中遇到问题或有改进建议，请：

1. 在项目中创建 Issue
2. 标记为 `skill:version-bump`
3. 描述问题或建议
```

### 迭代优化

根据使用情况持续优化：

1. **监控使用频率** - 了解哪些部分最常用
2. **收集错误报告** - 识别常见问题
3. **分析用户反馈** - 发现改进点
4. **定期更新** - 保持与技术同步

### 知识沉淀

将使用经验沉淀到文档：

```markdown
## Lessons Learned

### 常见误区

1. **误区**: 认为可以跳过测试
   **正确**: 测试是必需的，确保质量

2. **误区**: 手动修改版本号
   **正确**: 使用 `npm version` 自动更新
```

## 总结

创建高质量 Skills 的关键要素：

1. **清晰的结构** - 遵循标准格式
2. **可执行的步骤** - 每步都具体明确
3. **完善的验证** - 确保正确完成
4. **友好的体验** - 考虑用户感受
5. **持续的维护** - 保持文档更新

通过应用这些最佳实践和设计模式，你可以创建出真正有用、易用、可维护的 Skills。
