  1. 整体架构

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                         Auto-Claude Agent 系统架构                           │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │                                                                             │
  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
  │  │   Planner   │───▶│    Coder    │───▶│ QA Reviewer │───▶│  QA Fixer   │  │
  │  │    Agent    │    │    Agent    │    │    Agent    │    │    Agent    │  │
  │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
  │        │                  │                  │                  │          │
  │        ▼                  ▼                  ▼                  ▼          │
  │  ┌─────────────────────────────────────────────────────────────────────┐   │
  │  │                     Claude Agent SDK (底层)                          │   │
  │  │                     - ClaudeSDKClient                               │   │
  │  │                     - 工具调用 (Bash, Read, Write, Edit, etc.)       │   │
  │  └─────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  └─────────────────────────────────────────────────────────────────────────────┘

  2. Agent 类型与职责

  | Agent       | 提示词文件        | 职责                       | 输出                     |
  |-------------|-------------------|----------------------------|--------------------------|
  | Planner     | planner.md        | 分析 spec.md，创建实现计划 | implementation_plan.json |
  | Coder       | coder.md          | 逐个实现 subtask           | 代码 + commit            |
  | QA Reviewer | qa_reviewer.md    | 验证实现是否符合要求       | qa_report.md             |
  | QA Fixer    | qa_fixer.md       | 修复 QA 发现的问题         | 修复代码                 |
  | Recovery    | coder_recovery.md | 处理失败的 subtask         | 新的实现方案             |

  3. 核心执行流程

  # agents/coder.py - 主循环
  async def run_autonomous_agent(...):
      while True:
          # 1. 检查是否有 PAUSE 文件（人工干预）
          if pause_file.exists():
              return

          # 2. 获取下一个待处理的 subtask
          next_subtask = get_next_subtask(spec_dir)

          # 3. 创建 Claude SDK 客户端
          client = create_client(project_dir, spec_dir, model)

          # 4. 生成提示词
          if first_run:
              prompt = generate_planner_prompt(spec_dir)  # Planner 提示词
          else:
              prompt = generate_subtask_prompt(...)       # Coder 提示词

          # 5. 运行 Agent 会话
          async with client:
              status, response = await run_agent_session(client, prompt, ...)

          # 6. 后处理（更新内存、记录进度）
          await post_session_processing(...)

          # 7. 检查状态
          if status == "complete":
              break
          elif status == "continue":
              await asyncio.sleep(3)  # 自动继续

  4. 提示词系统详解

  4.1 提示词文件列表

  apps/backend/prompts/
  ├── planner.md              # 规划 Agent (917 行)
  ├── coder.md                # 编码 Agent (972 行)
  ├── coder_recovery.md       # 恢复 Agent (291 行)
  ├── qa_reviewer.md          # QA 审查 Agent (605 行)
  ├── qa_fixer.md             # QA 修复 Agent
  ├── followup_planner.md     # 后续规划 Agent
  ├── spec_gatherer.md        # 需求收集 Agent
  ├── spec_writer.md          # 规格编写 Agent
  ├── spec_critic.md          # 规格评审 Agent
  ├── spec_researcher.md      # 研究 Agent
  ├── complexity_assessor.md  # 复杂度评估 Agent
  ├── insight_extractor.md    # 洞察提取 Agent
  ├── ideation_*.md           # 创意生成系列
  └── validation_fixer.md     # 验证修复 Agent

  4.2 Planner 提示词核心结构 (planner.md)

  ## YOUR ROLE - PLANNER AGENT (Session 1 of Many)

  ## PHASE 0: DEEP CODEBASE INVESTIGATION (MANDATORY)
  - 理解项目结构
  - 分析现有模式
  - 记录发现

  ## PHASE 1: READ AND CREATE CONTEXT FILES
  - 读取 spec.md
  - 创建 project_index.json
  - 创建 context.json

  ## PHASE 2: UNDERSTAND THE WORKFLOW TYPE
  - FEATURE: 多服务功能
  - REFACTOR: 重构
  - INVESTIGATION: 调查 bug
  - MIGRATION: 数据迁移
  - SIMPLE: 简单任务

  ## PHASE 3: CREATE implementation_plan.json
  - 定义 phases（阶段）
  - 定义 subtasks（子任务）
  - 设置依赖关系

  ## PHASE 4: ANALYZE PARALLELISM OPPORTUNITIES
  - 分析并行可能性
  - 推荐 worker 数量

  ## PHASE 5-7: 创建 init.sh, 提交, 创建 build-progress.txt

  4.3 Coder 提示词核心结构 (coder.md)

  ## YOUR ROLE - CODING AGENT

  ## STEP 1: GET YOUR BEARINGS (MANDATORY)
  - pwd && ls -la
  - 读取 implementation_plan.json
  - 读取 spec.md
  - 读取 session memory

  ## STEP 2: UNDERSTAND THE PLAN STRUCTURE
  - phases → subtasks 层级
  - 依赖规则

  ## STEP 3: FIND YOUR NEXT SUBTASK
  - 找到 status: "pending" 的 subtask

  ## STEP 4: START DEVELOPMENT ENVIRONMENT
  - 运行 init.sh

  ## STEP 5: READ SUBTASK CONTEXT
  - 读取 files_to_modify
  - 读取 patterns_from
  - 使用 Context7 查询文档

  ## STEP 5.5: GENERATE PRE-IMPLEMENTATION CHECKLIST
  - 预测可能的 bug
  - 检查已知的 gotchas

  ## STEP 6: IMPLEMENT THE SUBTASK
  - 标记为 in_progress
  - 可选使用 subagents 并行

  ## STEP 6.5: RUN SELF-CRITIQUE (MANDATORY)
  - 代码质量检查
  - 实现完整性检查

  ## STEP 7: VERIFY THE SUBTASK
  - 运行 verification 命令

  ## STEP 8-13: 更新计划、提交、记录进度

  4.4 动态提示词生成 (prompt_generator.py)

  def generate_subtask_prompt(spec_dir, project_dir, subtask, phase, attempt_count, recovery_hints):
      """
      生成精简的 subtask 提示词（~100 行而非 900 行）
      
      包含:
      - 环境上下文 (工作目录、spec 位置)
      - Subtask 描述
      - 重试上下文 (如果是重试)
      - 文件列表 (files_to_modify, files_to_create, patterns_from)
      - 验证方法
      - 指令和质量检查清单
      """

  5. 会话管理 (session.py)

  async def run_agent_session(client, message, spec_dir, verbose, phase):
      """
      运行单个 Agent 会话
      
      1. 发送 prompt 到 Claude SDK
      2. 流式接收响应
      3. 处理工具调用 (ToolUseBlock)
      4. 处理工具结果 (ToolResultBlock)
      5. 检查构建是否完成
      """

      await client.query(message)

      async for msg in client.receive_response():
          # 处理 AssistantMessage (文本 + 工具调用)
          # 处理 UserMessage (工具结果)
          pass

      if is_build_complete(spec_dir):
          return "complete", response_text
      return "continue", response_text

  6. 后处理系统 (post_session_processing)

  async def post_session_processing(...):
      """
      会话后处理（100% 可靠，不依赖 Agent）
      
      1. 同步 implementation_plan 到源目录
      2. 检查 subtask 状态
      3. 检查新 commit
      4. 记录成功/失败尝试
      5. 提取会话洞察 (LLM 分析)
      6. 保存会话记忆 (Graphiti 或文件)
      7. 更新 Linear (如果启用)
      """

  7. 记忆系统

  spec_dir/memory/
  ├── codebase_map.json       # 文件用途映射
  ├── patterns.md             # 代码模式
  ├── gotchas.md              # 已知陷阱
  ├── attempt_history.json    # 尝试历史
  ├── build_commits.json      # 提交记录
  └── session_insights/       # 会话洞察
      ├── session_001.json
      ├── session_002.json
      └── ...

  8. 恢复机制

  # RecoveryManager 跟踪:
  - 每个 subtask 的尝试次数
  - 失败原因
  - 成功的 commit hash
  - 卡住的 subtask

  # 恢复策略:
  - 3 次失败后标记为 "stuck"
  - 检测循环修复（相同方法重复尝试）
  - 提供恢复提示给下一次尝试

  9. 关键设计原则

  1. 无状态 Agent: 每个会话都是全新的上下文窗口，所有状态通过文件传递
  2. 单一职责: 每个 subtask 只做一件事
  3. 验证驱动: 每个 subtask 必须有验证方法
  4. 依赖感知: 阶段之间有明确的依赖关系
  5. 自动恢复: 失败后自动重试，使用不同方法
  6. 记忆持久化: 会话洞察保存到文件，供后续会话使用

  ---
  这就是 Auto-Claude 的 Agent 实现原理和提示词系统的完整分析。核心思想是：

  1. 提示词即指令: 每个 Agent 的行为完全由其提示词定义
  2. Python 编排: 复杂的状态管理和后处理由 Python 代码处理，不依赖 Agent
  3. 文件即状态: 所有状态通过 JSON/MD 文件传递，实现无状态 Agent
  4. 动态提示词: 根据当前 subtask 动态生成精简的提示词，减少 token 消耗