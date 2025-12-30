# Auto-Claude 代码架构研究报告

> [!NOTE]
> 本报告基于对 Auto-Claude 代码库的静态分析，结合 Google Code Wiki 定义的 "Agentic Research Framework" 进行解读。

## 1. 核心定义

**Auto-Claude** 是一个多会话自主编码框架 (Multi-Session Autonomous Coding Framework)。它不仅仅是一个简单的代码生成脚本，而是一个具备完整生命周期管理的智能体系统。

其核心设计理念与 **Google Code Wiki** 框架高度契合：
- **理解 (Understand)**: 通过 `Insight Extractor` 深入理解代码上下文。
- **文档化 (Document)**: 通过 `Memory Manager` 和 `Graphiti` 实时更新项目知识库（类似 Code Wiki）。
- **行动 (Act)**: 通过 `Planner` 和 `Coder` 智能体执行具体的编码任务。

## 2. 系统架构

系统整体采用分层架构，确保了交互、逻辑与底层资源的解耦。

```mermaid
graph TD
    User[用户指令] --> CLI[CLI (run.py/cli)]
    CLI --> CMD[Command Handlers]
    
    subgraph Agents [智能体层]
        CMD --> Planner[Planner Agent]
        CMD --> Coder[Coder Agent]
        Planner --更新计划--> Plan[Implementation Plan]
        Coder --读取计划--> Plan
        Coder --执行循环--> Session[Agent Session]
    end

    subgraph Core [核心服务层]
        Session --> Client[Claude SDK Client]
        Session --> Insight[Insight Extractor]
        Session --> Memory[Memory Manager]
    end

    subgraph Infrastructure [基础设施层]
        Coder --> Worksapce[Workspace Manager]
        Worksapce --> Worktree[Git Worktree]
        Memory --> Graphiti[Graphiti / File Storage]
    end
```

### 关键组件解析

| 组件 | 路径 | 职责 |
|------|------|------|
| **CLI** | `apps/backend/cli/` | 入口分发，解析 `--spec`、`--merge` 等指令。 |
| **Session** | `apps/backend/agents/session.py` | 智能体交互的核心循环，负责发送 Prompt、处理工具调用 (Tool Use) 和错误恢复。 |
| **Planner** | `apps/backend/agents/planner.py` | 规划师，负责生成或更新 `implementation_plan.json`，将大任务拆解为子任务 (Subtasks)。 |
| **Workspace** | `apps/backend/core/workspace.py` | 资源隔离层，确保 Agent 在独立的环境（Git Worktree）中工作，不污染主分支。 |
| **Memory** | `apps/backend/agents/memory_manager.py` | 长期记忆管理，将 Session 中的洞察 (Insights) 持久化，模拟 "Code Wiki" 的功能。 |

## 3. 核心工作流 (Core Workflows)

### 3.1 启动与规划 (Startup & Planning)
1. **入口**: 用户运行 `python apps/backend/run.py --spec 001`.
2. **初始化**: `apps/backend/cli/main.py` 启动环境，`apps/backend/cli/build_commands.py` 接管控制权。
3. **规划**: 如果没有计划，调用 `Planner` Agent。
   - `Planner` 读取需求 (`FOLLOWUP_REQUEST.md` 或初始 Spec)。
   - 生成结构化的 `implementation_plan.json`，包含多个 `Phases` 和 `Subtasks`。

### 3.2 编码与执行 (Coding & Execution)
1. **循环**: `Build Loop` 遍历计划中的 `pending` 子任务。
2. **会话**: 为每个子任务启动一个 `Session`（`apps/backend/agents/session.py`）。
3. **交互**:
   - `ClaudeSDKClient` 发送由 `prompts/` 生成的指令。
   - 模型返回 `ToolUseBlock` (如 `Edit`, `Run`, `Grep`)。
   - `Session` 执行工具，并将结果反馈给模型。
4. **收尾**:
   - 子任务完成后，`post_session_processing` 被触发（`apps/backend/agents/session.py`）。
   - **Insight Extraction**: 分析代码变更，提取模式和洞察。
   - **Memory Update**: 更新项目的“知识库”。

### 3.3 隔离与合并 (Isolation & Merge)
- 所有修改默认发生在 `Git Worktree` 隔离环境中。
- 用户满意后，通过 `--merge` 命令将变更合并回主项目。

## 4. 与 Google Code Wiki 框架的对齐

用户提到的 **Google Code Wiki Research Framework** 强调利用 AI 进行深度理解和文档化。Auto-Claude 完美实践了这一点：

1. **动态文档化**: 代码库中的 `Memory` 模块实际上就是一个动态维护的 Wiki。每次 Session 结束后，系统都会自动提炼 "Insights" 并保存，保证了在该框架下工作的 Agent 总是拥有最新的上下文。
2. **结构化思维**: 区别于 chat-based coding，Auto-Claude 强制要求先通过 `Planner` 生成结构化计划，这符合 "Research First" 的方法论。
3. **闭环验证**: 每一轮修改都通过 `QA` 环节（代码中有 `apps/backend/cli/qa_commands.py`）进行验证，确保生成的不仅仅是代码，而是**可工作的软件**。

## 5. 总结

Auto-Claude 代码库展示了一个高度成熟的**Agentic Coding** 范式。它并没有把 LLM 仅仅当作一个补全工具，而是将其通过 `Session`、`Tools` 和 `Memory` 封装成了一个能够自主规划、执行、反思和记录的虚拟工程师。

这正是 Google Code Wiki 理念在工程工具链上的具体落地。
