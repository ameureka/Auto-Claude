# Auto-Claude 项目核心架构与 Agent 系统深度分析报告

**日期**: 2025-12-30
**分析者**: Antigravity (AMEUREKA)
**分析范围**: 包含 Agent 逻辑、提示词拆解、架构体系、及与 ProxyCast 的集成

---

## 1. 项目全景：Auto-Claude 的核心本质

Auto-Claude 不仅仅是一个 AI 聊天界面，它是一个**基于“规范驱动 (Spec-Driven)”的自主编码框架**。其核心公式为：
`Python 编排逻辑 + Claude Code 执行能力 + Git Worktree 物理隔离 = 生产级 AI 编码`

### 核心价值
- **自主性**: 除了定义需求 (spec.md)，用户无需干预具体编码过程。
- **安全性**: 即使 AI 误删文件，也只发生在隔离的 Worktree 分支中。
- **一致性**: 强制性的 Pattern Matching 确保 AI 写的代码风格与项目原有风格一致。

---

## 2. 深度拆解：Agent 系统与提示词哲学

### 2.1 角色分工 (Functional Agents)
系统并未采用重型的 Agent 类，而是通过**函数式编排**动态切换角色。

| 角色 | 核心文件 | 心理模型 (Mindset) |
|------|---------|-------------------|
| **Planner** | `planner.md` | **“图纸设计师”**: 极度细致，将任务拆解为 < 100 行代码的 Subtasks。 |
| **Coder** | `coder.md` | **“防御性施工队”**: 绝不盲目操作，必须先 ls/glob 确认，必须运行验证命令。 |
| **QA Reviewer** | `qa_reviewer.md` | **“挑剔的验收官”**: 假设 Coder 写了 Bug，使用 Headless 浏览器进行视觉验证。 |
| **QA Fixer** | `qa_fixer.md` | **“精密的修复工”**: 针对 QA 报告精确修复，不改动无关代码。 |
| **Recovery** | `coder_recovery.md` | **“自愈系统”**: 当任务卡住时，分析之前的失败模式并更换技术路线。 |

### 2.2 提示词策略：微型化与动态注入
- **碎片化 (Fragmentation)**: 每个 Agent Session 的上下文窗口是干净的。Planner 只管规划，Coder 只管当前的 Subtask。
- **上下文注入 (Context Injection)**: 提示词在发送前由 Python 注入实时的“调料”：
    - **Environment**: 限制其只能在特定 Worktree 目录工作。
    - **Memory**: 注入 `patterns.md`（现成的写法）和 `gotchas.md`（由于历史失败学到的教训）。
    - **Recovery Hints**: 如果是重试，会明确告知：“你上次在这里用了方法 A 失败了，这次请尝试方法 B”。

---

## 3. 架构体系：隔离、安全与记忆

### 3.1 环境隔离：Git Worktree
- **机制**: 1 个 Spec → 1 个 Worktree → 1 个 Git 分支。
- **优势**: 允许并行开发（最多支持 12 个并行终端），且完全不污染主开发环境。

### 3.2 三层安全防御
1. **OS 沙箱**: 所有的 Bash 命令在隔离受限的运行环境中执行。
2. **文件系统 ACL**: 限制 AI 只能读写项目根目录内的文件。
3. **动态命令白名单**: 系统在启动时分析 `package.json` 或 `pyproject.toml`，动态决定允许运行哪些测试/构建命令。

### 3.3 记忆系统：双层架构
- **Layer 1 (文件级)**: 存储在 `specs/XX/memory/`，包含 `codebase_map.json`。始终可用。
- **Layer 2 (Graphiti)**: 基于图数据库的语义检索。赋予了 AI 跨任务、跨会话引用历史知识的能力。

---

## 4. ProxyCast：打通“最后一公里”

在使用 Claude Code 时，ProxyCast 扮演了至关重要的基础设施角色：

- **认证绕过**: 通过注入 `ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_BASE_URL`，成功使 Claude Code 绕过官方服务器限制，使用 Kiro 或 Gemini Pro 资源。
- **Live Sync 自动注入**: ProxyCast 后台监听配置变化，自动写回 `~/.claude.json` 和 `~/.claude/settings.json`，确保无缝切换。
- **故障排除**: 项目文档总结了 401 Unauthorized 和 Key 被 Rejected 的一键修复脚本。

---

## 5. 针对 Gemini 3 Pro 的特别洞察

- **角色定位**: 在 `gemini3pro-analysic` 中，系统强调了 Gemini 作为高效分析 Agent 的能力。
- **知识沉淀**: 实施计划中包含利用 Gemini 的长上下文特性，对项目进行全量深度扫描并生成 `analysis-summary.md`。

---

## 6. 总结与建议

Auto-Claude 的精髓在于**“把 LLM 当成不可靠的执行引擎，把 Python 当成可靠的编排轨道”**。

**对于后续开发/使用的建议**:
1. **维护 Spec 质量**: 输入的 `spec.md` 决定了输出的上限。
2. **监控 Gotchas**: 定期检查并手动优化 `memory/gotchas.md`，这能极大提高 AI 的任务成功率。
3. **分段执行**: 像文档中指出的那样，即使是 151 个文件的任务，由于系统采用 Subtask 拆解，仍能稳定输出。

---
**报告完成。所有关键文档已汇聚。**
