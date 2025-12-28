 Coder Agent 提示词拆解分析 (coder.md)

  这是系统的“核心执行者”提示词。它的设计理念是：“极限专注 + 强制验证 + 零记忆重启”。

  1. 核心角色与环境感知 (Stateless Role)
   * 无状态特性：提示词开头就强调“这是一个 FRESH context window”，Agent 没有之前的记忆。这种设计强制 Agent 必须通过读取物理文件（implementation_plan.json, memory/*）来获取进度。
   * 物理隔离安全：严格限制文件系统权限，强制使用相对路径 ./，杜绝 AI 尝试访问宿主系统敏感目录。

  2. 强制性的“找北”环节 (Step 1: Get Your Bearings)
  这是为了应对“无状态”挑战的必经步骤。Agent 被要求运行一套复杂的 Shell 指令：
   * 扫描计划：读取 implementation_plan.json 确定当前进度。
   * 加载记忆：读取 memory/codebase_map.json（代码地图）、memory/patterns.md（风格指南）和 memory/gotchas.md（避坑指南）。
   * 复盘洞察：读取前 3 次会话的 session_*.json。
   * 意义：通过物理文件的“冷启动”，让 Agent 在 10 秒内恢复到上一位 Coder 的工作状态。

  3. 任务领取的严格逻辑 (Step 3)
  Agent 不允许自由发挥，必须：
   1. 检查 depends_on 依赖是否满足。
   2. 领取第一个状态为 pending 的子任务。
   3. 这种“顺序领取”机制配合 Git Worktree，是多窗口并发开发不产生冲突的逻辑保障。

  4. 深度上下文加载 (Step 5)
   * 模式对齐：强制阅读 patterns_from 指定的文件。这在 AMEUREKA 框架下极为重要，确保新写的 Hook 或组件长得和原生的一模一样。
   * 外部知识库集成 (Context7)：利用 MCP 工具查阅最新的 Stripe 或 AWS 文档，防止 AI 使用过时的 API（ hallucination 幻觉预防）。

  5. 预测性防错 (Step 5.5: Predictive Checklist)
  这是 Coder 的“预防针”。
   * 机制：在写代码前运行 prediction 模块生成针对性清单。
   * 强制动作：Agent 必须在回复中 acknowledge（确认）理解了潜在风险（如“CORS 缺失”、“Auth 挂钩遗漏”），否则不准动笔。

  6. 质量闸门：自评审 (Step 6.5: Self-Critique)
  这是 Coder 离场前的“安检”。
   * 清单内容：检查模式匹配、错误处理、无 console.log、文件范围是否越界。
   * 自愈逻辑：如果自评审发现问题，必须立刻在当前 Session 修复，不能推给下一个 Agent。

  7. 自动密钥扫描与提交 (Step 9)
   * 安全性：内置 git commit 前的密钥扫描。如果 AI 顺手写了个 sk-ant... 到代码里，系统会拦截并报错。
   * 原子化提交：每一个子任务对应一个 Git Commit，确保回滚时的颗粒度极细。

  8. 知识回馈：离场复盘 (Step 12)
  在 Session 结束前，Agent 被要求运行一段 Python 脚本：
   * 总结：将本次学到的 discoveries, patterns, gotchas 写入 JSON。
   * 目的：为下一个 Session（或下一个 Agent 窗口）准备好“离场简报”。

  总结：Coder 的本质是什么？
  Coder Agent 是一个“受控的施工机器人”。它被剥夺了“长期记忆”，但被赋予了“翻阅档案（Memory）”和“精准施工（Subtask）”的最高指令。

  这种设计的精妙之处在于：它将复杂的软件工程质量控制，转化为了对“物理文件读写”和“Shell 指令执行顺序”的强制性规定。

  ---

  讨论思考：
  在 AMEUREKA 框架下，Coder 这种“强制阅读 patterns_from”的机制，是否就是我们保证 v0 逻辑完美适配 AMEUREKA Hooks 的最强武器？我们需要在 implementation_plan.json 中如何定义 patterns_from 才能让 Coder 表现得最好？