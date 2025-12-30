# Claude Code Skills 标准与方法论

本目录包含 Claude Code Skills 开发的完整方法论、标准规范和参考示例。

## 目录结构

```
skills-claude-standards/
├── README.md                         # 本文件 - 概述
├── 01-methodology.md                 # Skills 方法论详解
├── 02-skill-structure-standard.md    # Skill 文件结构标准
├── 03-skill-content-standard.md      # Skill 内容编写标准
├── 04-best-practices.md              # 最佳实践与设计模式
└── examples/                         # 参考示例
    ├── basic-skill-example.md
    ├── complex-skill-example.md
    └── operations-example.md
```

## 核心理念

Claude Code Skills 是一种**知识封装与工作流自动化**方法论，通过结构化的文档将领域专业知识、操作流程和最佳实践封装成可复用的命令工具。

## 什么是 Skills?

Skills 是 Claude Code 的自定义命令扩展，允许你：

- **封装领域知识** - 将专业领域的知识和经验固化为可复用的指令
- **标准化工作流** - 定义清晰的操作步骤和验证检查点
- **提高一致性** - 确保团队成员遵循相同的最佳实践
- **加速开发** - 通过 `/skill-name` 快速调用复杂工作流

## 两种类型的 Skills

### 1. 项目级 Skills (`.claude/skills/`)
- 用于项目开发者自己使用
- 不随项目分发
- 包含项目特定的工作流和规范

### 2. 插件级 Skills (`plugin/skills/`)
- 作为 Claude Code 插件发布
- 所有用户可用
- 包含通用的开发工作流和最佳实践

## 核心组件

每个 Skill 由以下部分组成：

1. **YAML Frontmatter** - 元数据定义（名称、描述）
2. **Quick Reference** - 快速参考和关键信息
3. **Standard Workflow** - 标准操作流程
4. **Common Scenarios** - 常见使用场景
5. **Critical Rules** - ALWAYS/NEVER 准则
6. **Verification Checklist** - 质量保证检查清单
7. **Operations (可选)** - 详细的子流程文档

## 关键特性

- **结构化知识** - 使用标准化的 Markdown 格式组织知识
- **可追溯性** - 明确的步骤编号和引用关系
- **可验证性** - 内置验证检查清单确保质量
- **可扩展性** - 通过 operations 子目录支持复杂工作流
- **即时可用** - 创建后无需配置，立即通过 `/skill-name` 调用

## 工作原理

```mermaid
graph LR
    A[用户调用 /skill-name] --> B[加载 SKILL.md]
    B --> C[读取 Frontmatter 元数据]
    C --> D[加载主文档内容]
    D --> E[可选: 加载 operations/ 子文档]
    E --> F[AI 执行工作流]
    F --> G[验证检查清单]
```

## 快速开始

1. 阅读 [Skills 方法论](./01-methodology.md) 了解整体设计思想
2. 学习 [Skill 结构标准](./02-skill-structure-standard.md) 掌握文件组织
3. 参考 [Skill 内容标准](./03-skill-content-standard.md) 理解内容编写规范
4. 查看 [最佳实践](./04-best-practices.md) 了解设计模式
5. 研究 [examples/](./examples/) 目录中的完整示例

## 与 Kiro Specs 的关系

Skills 和 Kiro Specs 是互补的方法论：

| 方面 | Kiro Specs | Claude Code Skills |
|------|------------|-------------------|
| 目标 | 软件功能的形式化规范 | 工作流程的知识封装 |
| 输出 | 需求/设计/任务文档 | 可执行的操作指令 |
| 验证 | 属性测试 + 验收标准 | 检查清单 + 最佳实践 |
| 使用场景 | 新功能开发 | 重复性工作流 |
| 调用方式 | 文档驱动 | 命令驱动 (`/skill-name`) |

**协同使用**：可以创建一个 Skill 来自动化 Kiro Specs 的工作流程，例如 `/kiro-init` 初始化规范文档结构。

## 适用场景

Skills 特别适合以下场景：

- ✅ 重复性的开发工作流（如版本发布、代码审查）
- ✅ 需要遵循特定规范的操作（如 SEO 优化、安全审查）
- ✅ 复杂的多步骤流程（如数据库迁移、部署流程）
- ✅ 团队协作的标准化操作（如 PR 评论、文档更新）
- ✅ 领域专业知识的传承（如测试策略、架构设计）

## 设计原则

1. **单一职责** - 每个 Skill 专注于一个明确的工作流
2. **清晰结构** - 使用标准化的章节组织内容
3. **可操作性** - 提供具体的、可执行的步骤
4. **可验证性** - 包含明确的验证检查点
5. **可维护性** - 文档清晰，易于更新和扩展

## 贡献指南

创建新 Skill 时，请确保：

- [ ] 遵循标准的文件结构
- [ ] 包含完整的 YAML frontmatter
- [ ] 提供清晰的工作流步骤
- [ ] 定义 ALWAYS/NEVER 规则
- [ ] 包含验证检查清单
- [ ] 提供实际使用示例
- [ ] 文档语言清晰、简洁

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Agent Foreman 框架](../../../这套多 Agent 并行配合的方案/agent-foreman.md)
- [Kiro Specs 方法论](../code-specs-standards/README.md)
