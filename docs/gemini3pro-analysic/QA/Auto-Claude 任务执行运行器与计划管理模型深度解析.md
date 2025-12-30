# Auto-Claude 任务执行运行器与计划管理模型深度解析

**日期**: 2025-12-22
**分析对象**: Runner Suite & OOP Implementation Plan (`apps/backend/runners/`, `apps/backend/implementation_plan/`)

---

## 1. 核心理念：从生成到工程化的“对象化”转换

Auto-Claude 并不直接把 LLM 返回的 JSON 字符串传给执行引擎，而是先通过 Python 的**对象模型（OOP）**进行严格的解析、校验和增强。这种设计将“不可靠的 AI 输出”封装进了“可靠的工程容器”。

---

## 2. 计划管理模型 (`ImplementationPlan`)

位于 `apps/backend/implementation_plan/`，这是整个开发任务的“灵魂”。

### 2.1 三层嵌套架构
1.  **`ImplementationPlan` (Top)**: 管理全局元数据（`feature`, `workflow_type`）、整体状态（`status`）和 QA 签发结果。
2.  **`Phase` (Middle)**: 管理阶段性任务集合。核心逻辑：**依赖检查 (`depends_on`)**。
3.  **`Subtask` (Leaf)**: 原子执行单元。包含操作指令（`files_to_modify`）、参考模式（`patterns_from`）和验证方案（`verification`）。

### 2.2 状态自动同步逻辑
模型内部实现了 `update_status_from_subtasks()` 方法：
- **原理**: 当最后一个 Subtask 被标记为 `completed` 时，父级 Phase 会自动完结。
- **UI 对齐**: 状态位（如 `ai_review`, `human_review`）严格遵循 UI 端的状态机定义，确保前后端感官一致。

---

## 3. 任务执行运行器 (`Runners`)

运行器是不同功能模块的“驱动程序”。

### 3.1 规格书运行器 (`spec_runner.py`)
- **功能**: 执行从任务描述到 Spec 文档的完整流水线。
- **特色：链式启动**:
    - 在 Spec 生成并经过人工（或自动）批准后，它会构建一个 `python run.py --spec XXX --auto-continue` 命令。
    - 使用 `os.execv` **替换当前进程**，实现从“需求定义”到“代码编写”的无缝自动化跳转。

### 3.2 洞察提取运行器 (`insights_runner.py`)
- **功能**: 在 Coder 会话结束后，启动后台进程，将 Git Diff 转化为长期记忆。

---

## 4. 关键代码亮点：Subtask 验证元数据

`Subtask` 模型包含一个 `Verification` 字段，支持多种验证类型：
- `api`: 自动组装 `curl` 指令。
- `browser`: 触发 Playwright 视觉检查。
- `command`: 执行 shell 脚本。
这确保了 Agent 在执行 Subtask 时，不仅知道“改哪里”，还知道“怎么测”。

---

## 5. 对 AMEUREKA 协作的启示

1.  **扩展 Phase 类型**: 可以新增 `AMEUREKA_SPEC_PHASE` 枚举，用于在计划中强制插入“属性测试生成”阶段。
2.  **自定义验证器**: 修改 `Verification.from_dict`，使其能够支持 AMEUREKA 特有的 `kiro-test` 命令。

---

## 6. 总结

Auto-Claude 的计划管理系统是一个**具备自我纠偏能力的执行树**。
- **鲁棒性**: 通过 `Auto-Fix` 容忍 AI 的 JSON 错误。
- **严谨性**: 通过 `ImplementationPlan` 对象模型强制执行阶段依赖。
- **连贯性**: 通过 Runner 机制实现了开发全生命周期的自动化衔接。
