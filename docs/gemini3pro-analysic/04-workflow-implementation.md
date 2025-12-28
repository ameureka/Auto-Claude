# 04. 核心工作流实现 (Workflow Implementation)

## 1. 概述
Auto-Claude 的核心价值在于其端到端的自动化工作流，从模糊的想法到最终的代码合并。本章节详细分析其四大阶段：Spec 生成、代码实现、QA 验证和合并。

## 2. 第一阶段：动态 Spec 生成 (Spec Creation)

Spec 生成不是一个简单的 Prompt，而是一个由 `spec/pipeline/orchestrator.py` 管理的动态 Pipeline。

### 2.1 复杂性自适应 (Complexity Adaptation)
系统首先运行 "Discovery" 和 "Requirements Gathering" 阶段，然后利用 AI (`_run_ai_assessment`) 或启发式算法评估任务的复杂度。

根据复杂度 (`Low`, `Medium`, `High`)，Orchestrator 动态决定后续运行哪些阶段：
- **Low**: 直接进入 `quick_spec`。
- **High**: 依次运行 `historical_context` -> `research` -> `spec_writing` -> `self_critique` -> `planning`。

### 2.2 上下文压缩 (Context Compaction)
为了防止长 Context 导致模型遗忘或超支，Pipeline 实现了**阶段总结机制**：
1.  每个阶段完成后，`_store_phase_summary` 会调用一个轻量级模型（如 Sonnet）将该阶段的输出压缩为 500 字摘要。
2.  后续阶段只接收之前阶段的摘要 (`prior_phase_summaries`)，而不是原始输出。

## 3. 第二阶段：代码实现 (Implementation)

（详见 *03. AI 代理编排系统*）

此阶段的核心是由 `implementation_plan.json` 驱动的。
- **状态机**: 每个 Subtask 都有状态 (`pending` -> `in_progress` -> `completed` / `stuck`)。
- **记忆**: 使用 `recovery_manager` 记录每个 Subtask 的尝试次数和失败原因，注入到下一次尝试的 Prompt 中。

## 4. 第三阶段：QA 闭环验证 (QA Loop)

实现位于 `qa/loop.py`，采用 **Review-Fix Loop** 模式。

### 4.1 流程逻辑
1.  **Reviewer Agent**: 检查代码是否满足 Spec 中的 Acceptance Criteria。
2.  **判断**: 如果通过，标记 Build Complete；如果失败，生成 Issues List。
3.  **Fixer Agent**: 针对 Issues List 进行修复。
4.  **循环**: 重复上述过程，直到通过或达到 `MAX_QA_ITERATIONS`。

### 4.2 自动升级 (Escalation)
如果同一个 Issue 在多次迭代中重复出现（`Recurring Issue`），系统会触发 `escalate_to_human`，暂停自动化并请求人工介入。

## 5. 第四阶段：智能合并 (Smart Merge)

实现位于 `cli/workspace_commands.py` 和 `merge/` 模块。

### 5.1 双层冲突检测
Auto-Claude 在合并前会进行两层检查：
1.  **Git 冲突**: 使用 `git merge-tree` 在内存中模拟合并，检测文件级冲突。
2.  **语义冲突 (Semantic Conflicts)**: 检查是否有多个并行的 Spec 任务修改了同一个逻辑模块（即使没有物理文件冲突）。

### 5.2 预览与执行
- `handle_merge_preview_command`: 生成 JSON 格式的冲突报告供 UI 展示。
- `handle_merge_command`: 执行实际合并（支持 `--no-commit` 以便人工 Review）。

## 6. 总结
Auto-Claude 的工作流设计体现了**"分而治之"**的思想：
- 将大任务拆解为 Spec Pipeline。
- 将编码拆解为 Subtasks。
- 将质量控制拆解为 QA Loop。
- 将合并拆解为预览和执行。

这种设计最大化了 AI 在每个细分环节的成功率。
