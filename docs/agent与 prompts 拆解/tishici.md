 Planner Agent 提示词拆解分析 (planner.md)

  这是系统的“总架构师”提示词。它的核心目标是将模糊的需求（Spec）转化为 100% 确定性的、可执行的 JSON 任务树。

  1. 核心角色设定 (Role Definition)
   * 定位：它是自主开发流程的第一个 Agent。
   * 核心理念：“Subtasks, not tests”。它认为测试是验证结果，而子任务（Subtask）定义实现步骤。
   * 约束：只负责规划，严禁编写代码。这体现了“职责分离”，防止 AI 在没想清楚架构前就开始盲目编码。

  2. 强制性的前置调研 (Phase 0: Deep Codebase Investigation)
  这是该提示词最出彩的地方。它强制 Agent 在动笔写计划前执行“深度探查”：
   * 目录扫描：使用 find 和 ls 摸清家底。
   * 模式匹配：强制执行 `grep` 寻找项目中类似的实现（例如搜 "cache", "api route"）。
   * 阅读指标：显式要求至少阅读 3 个模式文件。这是为了防止 AI 生成与现有项目风格格格不入的代码。

  3. 结构化的上下文构建 (Phase 1)
  要求 Agent 维护三个核心文件：
   * spec.md：原始需求。
   * project_index.json：项目的“数字孪生”索引（技术栈、端口、命令）。
   * context.json：任务特定的上下文（要改哪些文件、参考哪些模式）。

  4. 工作流类型驱动 (Phase 2: Workflow Type)
  它将任务归类为五种模式，每种模式对应不同的 Phase 结构：
   * FEATURE: 遵循服务依赖顺序（Backend -> Worker -> Frontend -> Integration）。
   * REFACTOR: 遵循迁移逻辑（Add New -> Migrate -> Remove Old -> Cleanup）。
   * INVESTIGATION: 遵循调试逻辑（Reproduce -> Investigate -> Fix -> Harden）。
   * MIGRATION & SIMPLE: 针对特定场景的简化流程。

  5. 计划生成的硬约束 (Phase 3: implementation_plan.json)
  这是产出物规范：
   * 原子化：每个子任务只能针对一个 Service，且改动量极小（1-3 个文件）。
   * 验证闭环：每个子任务必须自带 verification 字段（api, browser, command 等）。
   * 并发感知：标记 parallel_safe 字段，为后续的“12 窗口并发”提供逻辑依据。

  6. 环境初始化脚本 (Phase 5: init.sh)
  它要求 Agent 生成一个 Shell 脚本，用于自动化拉起后端、数据库和前端服务。这保证了后续 Coder 和 QA Agent 有一个可运行的环境。

  7. 负反馈与自我检查 (Checklist)
  结尾处包含了一套严格的 Pre-planning Checklist：
   * “如果你跳过了调研，你的计划会引用不存在的文件，引用错误的模式。”
   * 这种“警告式”的提示词能有效降低 LLM 的急躁情绪（Rush to code）。

  总结：Planner 的本质是什么？
  Planner 是一个“规则转换器”。它将人类的自然语言输入，通过对代码库的物理扫描，过滤并硬化为一套符合依赖图逻辑的 JSON 指令集。

  它设计的精妙之处在于：它不仅告诉 AI “你要做什么”，还通过强制性的工具调用指令（cat, grep, find）规定了 AI “必须先看什么”。

  ---

  讨论思考：
  你觉得在 AMEUREKA 框架下，Planner 这种“先扫描 3 个模式文件再写计划”的机制，是否能完美解决 v0 代码迁移时容易丢失 AMEUREKA 原生 Hooks 规范的问题？我们需要在 Phase 0 中增加哪些特定的 AMEUREKA 扫描指令吗？