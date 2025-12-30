# 03. AI 代理编排系统 (Agent System)

## 1. 概述
Auto-Claude 的 Agent 系统并未采用复杂的面向对象框架（如 LangChain 的 Agent 类），而是采用了**函数式编排 (Functional Orchestration)** 的设计模式。核心逻辑集中在 `agents/coder.py` 的无限循环中，通过动态切换 Prompt 和 Context 来模拟不同的 "Agent" 角色。

## 2. 核心组件

### 2.1 Agent 角色定义

尽管代码中没有显式的 `class Planner(Agent)`，但系统逻辑上定义了以下角色：

| 角色 | 职责 | 触发条件 | 对应的 Prompt 文件 |
|------|------|----------|-------------------|
| **Planner** | 分析 Spec，生成 `implementation_plan.json` | 首次运行 (`is_first_run`) 或 `--followup` | `planner.md`, `followup_planner.md` |
| **Coder** | 执行具体的 Subtask，编写代码 | 存在 `pending` 状态的 Subtask | `coder.md` |
| **QA Reviewer** | 验证代码是否符合 Spec | 所有 Subtask 完成后 | `qa_reviewer.md` |
| **QA Fixer** | 修复 QA 发现的问题 | QA 验证失败 | `qa_fixer.md` |

### 2.2 核心执行引擎 (`agents/coder.py`)

`run_autonomous_agent` 函数是整个系统的“心脏”。它维护了一个状态机循环：

```python
async def run_autonomous_agent(...):
    # 1. 初始化管理器 (Recovery, Status, Logger)
    recovery_manager = RecoveryManager(...)
    
    # 2. 检查是否为 Planning 阶段
    if is_first_run(spec_dir):
        prompt = generate_planner_prompt(...)
    
    # 3. 主循环
    while True:
        # 3.1 检查人工干预 (PAUSE 文件)
        if check_pause(): return

        # 3.2 获取下一个任务
        next_subtask = get_next_subtask(spec_dir)
        
        # 3.3 生成动态 Prompt
        # 包含：任务描述、相关文件内容、Graphiti 记忆、重试提示
        prompt = generate_subtask_prompt(..., subtask=next_subtask, ...)
        
        # 3.4 执行会话 (调用 Claude SDK)
        status, response = await run_agent_session(client, prompt, ...)
        
        # 3.5 后处理 (Post-Processing)
        # 验证结果、提交代码、更新 Linear、提取 Insights
        success = await post_session_processing(...)
        
        # 3.6 状态流转
        if status == "complete": break
        if status == "error": retry()
```

### 2.3 会话管理 (`agents/session.py`)

`run_agent_session` 封装了与 Claude SDK 的底层交互：

- **流式处理**: 实时解析 `TextBlock` (思考过程) 和 `ToolUseBlock` (工具调用)。
- **工具执行**: 拦截 LLM 的工具调用，执行本地工具（文件读写、Shell 执行），并将结果回传给 LLM。
- **安全拦截**: 在工具执行前进行安全检查（虽然代码中主要是 try-catch，但 `utils.py` 中有命令白名单逻辑）。

## 3. 上下文与记忆管理

Auto-Claude 采用了多层上下文策略来突破 Context Window 限制：

1.  **Task Context**: 每个 Prompt 只包含当前 Subtask 相关的上下文，而非整个项目。
2.  **File Context**: 动态加载相关文件内容 (`load_subtask_context`)。
3.  **Graphiti Memory**: 集成 Graphiti 数据库，提供跨会话的长期记忆（Knowledge Graph）。
4.  **Recovery Hints**: 如果任务失败重试，会将之前的失败原因 (`recovery_hints`) 注入新的 Prompt，防止重蹈覆辙。

## 4. Prompt 工程架构

所有 Prompt 模板存储在 `apps/backend/prompts/` 目录下，采用 Markdown 格式。

- **模块化**: 将不同阶段的指令分离（Ideation, Spec, Coding, QA）。
- **动态注入**: 使用 Python 字符串格式化或 Jinja2 (推测) 将运行时数据（如文件列表、Git Diff）注入模板。

## 5. 总结

Agent 系统的设计极其**务实**：
- **无状态**: 每次 Session 都是一个新的 Client 实例，依赖文件系统 (`implementation_plan.json`) 和 Git 持久化状态。
- **容错性强**: 内置重试机制和 Recovery Manager，能够处理 LLM 的偶发错误。
- **可观测性**: 所有的操作都通过 `TaskLogger` 和 `StatusManager` 暴露给用户（CLI 输出和 UI 状态条）。
