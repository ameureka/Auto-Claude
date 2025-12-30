# 基础 Skill 示例

这是一个简单的 Skill 示例，展示基本的文件结构和内容格式。

## 文件结构

```
.claude/skills/
└── format-code/
    └── SKILL.md
```

## SKILL.md 内容

```markdown
---
name: format-code
description: 格式化项目代码并检查代码规范
version: 1.0.0
tags:
  - code-quality
  - formatting
updated: 2024-12-20
---

# 代码格式化

## Quick Reference

**一句话说明**: 使用 Prettier 和 ESLint 格式化代码并检查规范

**核心命令**:
- `npm run format` - 格式化所有代码
- `npm run lint` - 检查代码规范
- `npm run lint:fix` - 自动修复规范问题

**快速检查**:
- [ ] 所有文件已格式化
- [ ] 无 lint 错误
- [ ] 无 lint 警告

## Standard Workflow

### 准备阶段

1. **检查工具是否安装**

   ```bash
   npm list prettier eslint
   ```

   确保 Prettier 和 ESLint 已安装

   如果未安装，运行：
   ```bash
   npm install --save-dev prettier eslint
   ```

### 执行阶段

2. **格式化代码**

   ```bash
   npm run format
   ```

   Prettier 会自动格式化所有支持的文件

   **预期输出**:
   ```text
   ✓ src/index.js 52ms
   ✓ src/utils.js 23ms
   ✓ src/components/App.js 31ms
   ```

3. **检查代码规范**

   ```bash
   npm run lint
   ```

   ESLint 会检查代码规范问题

   **预期输出**:
   ```text
   ✓ 0 errors
   ✓ 0 warnings
   ```

4. **自动修复问题**（如果有错误）

   ```bash
   npm run lint:fix
   ```

   ESLint 会自动修复可以修复的问题

### 验证阶段

5. **再次检查**

   ```bash
   npm run lint
   ```

   确认所有问题已解决

## Common Scenarios

### 场景 1: 首次运行

**背景**: 项目首次配置代码格式化工具

**步骤**:
1. 安装依赖
   ```bash
   npm install --save-dev prettier eslint
   ```

2. 创建配置文件
   ```bash
   echo '{"semi": true, "singleQuote": true}' > .prettierrc
   ```

3. 格式化所有代码
   ```bash
   npm run format
   ```

4. 提交变更
   ```bash
   git add .
   git commit -m "chore: format code with prettier"
   ```

---

### 场景 2: 提交前检查

**背景**: 在提交代码前确保代码规范

**步骤**:
1. 格式化修改的文件
   ```bash
   npm run format
   ```

2. 检查规范
   ```bash
   npm run lint
   ```

3. 如果有错误，修复后重新检查
   ```bash
   npm run lint:fix
   npm run lint
   ```

4. 提交代码
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

---

### 场景 3: CI/CD 集成

**背景**: 在 CI/CD 流程中自动检查代码规范

**步骤**:
1. 在 `.github/workflows/ci.yml` 中添加：
   ```yaml
   - name: Check code format
     run: npm run lint
   ```

2. 推送代码触发 CI
   ```bash
   git push origin main
   ```

3. 查看 CI 结果，确保通过

## Critical Rules

### ✅ ALWAYS

1. **ALWAYS 在提交前格式化代码**
   - **原因**: 保持代码风格一致
   - **方法**: 运行 `npm run format`
   - **示例**: 每次 `git commit` 前执行

2. **ALWAYS 修复所有 lint 错误**
   - **原因**: 避免潜在的代码问题
   - **方法**: 运行 `npm run lint:fix`
   - **示例**: 不允许有 lint 错误的代码进入主分支

3. **ALWAYS 使用项目配置的规则**
   - **原因**: 保持团队代码风格统一
   - **方法**: 不要修改 `.prettierrc` 和 `.eslintrc` 除非团队同意
   - **示例**: 遵循 `.prettierrc` 中定义的规则

### ❌ NEVER

1. **NEVER 忽略 lint 错误**
   - **原因**: 可能导致运行时错误或安全问题
   - **后果**: 代码质量下降，难以维护
   - **替代**: 修复错误或与团队讨论是否需要调整规则

2. **NEVER 手动格式化代码**
   - **原因**: 容易出错且不一致
   - **后果**: 代码风格混乱
   - **替代**: 使用 Prettier 自动格式化

3. **NEVER 在代码中使用 eslint-disable**
   - **原因**: 绕过代码检查可能隐藏问题
   - **后果**: 降低代码质量
   - **替代**: 修复问题或与团队讨论规则调整

## Verification Checklist

### 代码格式

- [ ] **所有文件已格式化**
  ```bash
  npm run format
  ```
  预期: 无文件被修改（说明已经格式化）

- [ ] **无格式化差异**
  ```bash
  git diff
  ```
  预期: 无未提交的格式化变更

### 代码规范

- [ ] **无 lint 错误**
  ```bash
  npm run lint
  ```
  预期: `0 errors`

- [ ] **无 lint 警告**
  ```bash
  npm run lint
  ```
  预期: `0 warnings`

### Git 状态

- [ ] **所有变更已暂存**
  ```bash
  git status
  ```
  预期: 所有格式化的文件已 `git add`

- [ ] **提交信息清晰**
  - 如果只是格式化，使用 `chore: format code`
  - 如果包含功能，使用 `feat: add feature`

## Reference Commands

### Prettier 命令

```bash
# 格式化所有文件
npm run format

# 检查哪些文件需要格式化（不修改）
npx prettier --check "src/**/*.{js,jsx,ts,tsx,json,css,md}"

# 格式化特定文件
npx prettier --write src/index.js
```

### ESLint 命令

```bash
# 检查所有文件
npm run lint

# 自动修复问题
npm run lint:fix

# 检查特定文件
npx eslint src/index.js

# 检查并显示规则名称
npx eslint --debug src/index.js
```

### Git 命令

```bash
# 查看格式化后的差异
git diff

# 暂存所有变更
git add .

# 提交格式化变更
git commit -m "chore: format code with prettier"
```

## Troubleshooting

### 问题: Prettier 和 ESLint 冲突

**症状**: Prettier 格式化后，ESLint 报错

**原因**: Prettier 和 ESLint 规则冲突

**解决**:
```bash
npm install --save-dev eslint-config-prettier
```

在 `.eslintrc.js` 中添加：
```javascript
{
  "extends": ["prettier"]
}
```

---

### 问题: 格式化速度慢

**症状**: `npm run format` 执行很慢

**原因**: 格式化了不必要的文件（如 node_modules）

**解决**:
创建 `.prettierignore` 文件：
```
node_modules
dist
build
coverage
```

---

### 问题: 某些文件不应该格式化

**症状**: 自动生成的文件被格式化

**原因**: 没有配置忽略规则

**解决**:
在 `.prettierignore` 中添加：
```
# 自动生成的文件
src/generated/**
*.min.js
```

## Related Skills

- `/code-review` - 代码审查流程
- `/pre-commit` - 配置 Git pre-commit 钩子
- `/ci-setup` - 配置 CI/CD 流程

## Additional Resources

- [Prettier 官方文档](https://prettier.io/docs/en/)
- [ESLint 官方文档](https://eslint.org/docs/latest/)
- [Prettier vs ESLint](https://prettier.io/docs/en/comparison.html)
```

## 说明

这个示例展示了：

1. **完整的 YAML frontmatter** - 包含所有推荐字段
2. **清晰的章节结构** - 遵循标准格式
3. **可执行的步骤** - 每个步骤都有具体命令
4. **实际的场景** - 提供 3 个常见使用场景
5. **明确的规则** - ALWAYS 和 NEVER 规则
6. **完整的验证清单** - 可逐项检查
7. **参考命令** - 常用命令快速参考
8. **故障排查** - 常见问题和解决方法

这是一个适合大多数简单 Skill 的标准模板。
