 1. Agent 实现的底层原理：无状态执行与有状态记录

  Auto-Claude 的 Agent 并不是一个长连接的“生命体”，而是一个“即用即走”的执行单元。

   * SDK 封装 (`claude-agent-sdk`)：
      它底层使用了 Anthropic 的官方 SDK。每启动一个 Agent Session（会话），系统都会新建一个 ClaudeSDKClient。这个 Client 会加载指定的 System Prompt，并挂载一个特定的 Allowed Tools（工具白名单）。
   * 无状态 (Stateless) 的优势：
      由于每次 Session 都是干净的上下文，Agent 不会受到之前错误逻辑的污染。
   * 状态持久化 (Stateful) 的补偿：
      虽然 Agent 是无状态的，但工程状态保存在 物理磁盘 上：
       - Git Worktree: 保证了代码状态的物理持久化。
       - `implementation_plan.json`: 记录了任务的全局进度。
       - `task_logs.json`: 记录了 Agent 的所有思考过程。

  2. 核心 Agent 的提示词（Prompts）拆解

  我通过读取 apps/backend/prompts/ 下的文件，发现它们的 Prompt 并不是简单的指令，而是一套严密的“工程操作规范”。

  A. Coder Agent (coder.md) —— 它的“性格”是什么？
  这个提示词的核心逻辑是 “防御性编程”。
   * 身份设定：你是一个 Expert Full-stack Developer。
   * 核心约束：
       - 必须先阅读 patterns_from 文件，理解现有的代码风格（Style）和惯用法（Idioms）。
       - 严禁猜测路径，必须使用 Glob 和 Read 工具确认后才能操作。
       - 增量修改：只能修改 Subtask 指定的文件，禁止大范围重构。
       - 自验证：写完代码后，必须运行 Prompt 中指定的 Verification Command。

  B. Planner Agent (planner.md) —— 它是如何拆解任务的？
  这个 Prompt 的核心是 “任务原子化”。
   * 逻辑链：
       1. 分析 spec.md 的目标。
       2. 将其分解为多个 Phases（阶段，如：基础架构 -> 业务逻辑 -> UI -> 集成）。
       3. 每个 Phase 拆分为颗粒度极细的 Subtasks（每个 Subtask 的代码改动量建议不超过 100 行）。
       4. 关键指令：为每个 Subtask 自动生成 Verification（验证方式），这为后续的 QA 提供了依据。

  C. QA Reviewer Agent (qa_reviewer.md) —— 它为什么这么挑剔？
  这个 Prompt 的核心是 “反向对抗”。
   * 逻辑链：
       - “假设 Coder Agent 写了一堆 Bug”。
       - 它被要求以“不可信任”的态度去运行测试。
       - 它拥有 Visual MCP 工具 的权限，被要求在 headless 浏览器中真实截图并比对像素级差异。
       - 输出规范：如果不通过，必须输出结构化的 QA_FIX_REQUEST.md，精确指明错误行号。

  3. 动态注入：Prompt 的“调料”

  最精彩的地方在于，Auto-Claude 在发送给 LLM 的最终字符串里，会实时注入以下动态内容：

   1. Environment Context: “你现在的根目录是 .worktrees/task-001/，不要尝试跳出这个范围”。
   2. Memory Injection: 从 Graphiti 抓出来的历史教训（例如：“注意：本项目使用 pnpm 而非 npm，不要生成 package-lock.json”）。
   3. Recovery Hints: “你已经在这个任务上失败了 2 次，上次报错是 TypeError，这次请尝试不同的方法”。

  4. 协作逻辑总结

   * Planner 负责“画图纸”（JSON Plan）。
   * Coder 负责“按图施工”（Write Code）。
   * Python Orchestrator 负责“监工”（读取 JSON，把任务喂给 Coder，处理 Git 提交）。
   * QA 负责“验收”（Run Tests）。

  这种 “Python 层管逻辑，LLM 层管执行” 的分离，是它比普通 Chat 机器人强大的根本原因。

  你觉得这种“微型化、碎片化”的 Prompt 策略，在处理逻辑极度复杂的“跨组件通信”时，会不会导致 Agent 因为看不见全局而出现“顾此失彼”的情况？我们可以针对这一点深入讨论。

    提示词模板概览
  在 apps/backend/prompts/ 目录下，主要包含以下核心模板：
   1. `planner.md`: 架构规划与任务拆解。
   2. `coder.md`: 代码实现与模式遵循。
   3. `qa_reviewer.md`: 验收标准验证与 Bug 发现。
   4. `qa_fixer.md`: 针对性修复逻辑。
   5. `spec_writer.md`: 需求规格说明书编写。
   6. `complexity_assessor.md`: 任务复杂度评估。