QA Reviewer Agent 提示词拆解分析 (qa_reviewer.md)

  这是系统的“终极审计员”提示词。它的核心使命是：以怀疑的态度挑战 Coder Agent 的交付物，确保没有任何 Bug 漏网。

  1. 核心角色设定 (Final Line of Defense)
   * 定位：它是自主开发流程的最后一道防线。它的批准意味着代码可以直接上线。
   * 态度：对抗性思维。它被告知 Coder Agent 可能漏掉边缘案例、忘记迁移数据库、或者引入了安全隐患。

  2. 上下文加载与基准对齐 (Phase 0 & 1)
  在进行任何测试前，Agent 必须执行：
   * 差异审计：git diff main --name-only。它不仅看计划，还要看 Agent 实际上偷偷改了哪些文件。
   * 前置检查：检查所有 Subtask 是否真的都是 completed。如果还没写完，QA Agent 必须拒绝工作。

  3. 自动化测试体系 (Phase 3)
  它不仅是“看代码”，它是要“跑代码”：
   * 层级化测试：依次执行 Unit Tests -> Integration Tests -> E2E Tests。
   * 动态指令：它被要求去 project_index.json 里找 test_command。这意味着无论项目是用 pytest, npm test 还是 go test，QA Agent 都能自适应。

  4. 视觉与交互验证 (Phase 4: Browser Verification)
  这是针对前端的“必杀技”：
   * 视觉证据：利用 Puppeteer/Playwright 截图。
   * Console 审计：显式要求检查浏览器控制台是否有报错或警告。这是很多 AI 程序员容易忽略的“隐形 Bug”。

  5. 深度合规性检查 (Phase 6: Code Review)
  这是最高级的 Review 逻辑：
   * 第三方库审计 (Context7)：强制核对第三方库（如 Stripe, Prisma）的用法是否符合官方文档。这是通过 MCP 工具动态查阅文档实现的，有效防止 AI 凭经验写出废弃（Deprecated）的代码。
   * 安全扫描：手动 grep 扫描 eval, innerHTML, exec, shell=True 以及硬编码的密码。

  6. 回归测试 (Phase 7: Regression Check)
   * 核心逻辑：不仅要测新功能，还要跑全量测试确保没把老功能搞挂。这在 AMEUREKA 这种大型框架协作中至关重要。

  7. 结构化反馈与状态流转 (Phase 8 & 9)
  它是“带病”流水线的终结者：
   * 通过 (APPROVED)：更新 implementation_plan.json 并提交 Sign-off Commit。
   * 拒绝 (REJECTED)：必须生成一份详细的 QA_FIX_REQUEST.md。这份文档就是给 QA Fixer Agent 的“病历单”。

  总结：QA Reviewer 的本质是什么？
  QA Reviewer 是一个“规则执行裁判”。它设计的精妙之处在于：它将模糊的“好代码”标准拆解成了 10 个具体的执行阶段。

  它不仅检查“代码是否能跑”，还检查“代码是否安全”、“是否符合风格”、“是否符合官方文档”。

  ---

  讨论思考：
  在 AMEUREKA 框架下，QA Reviewer 是否可以通过增加一个 “AMEUREKA Property Validation” 阶段，专门检查代码是否满足 design.md 中定义的“正确性属性”？这样我们就能把属性测试（Property-Based Testing）也整合进这个自动闭环了。

  接下来，你想看 QA Fixer（如何针对病历单进行治疗）还是 Spec Writer（如何把你的想法变成这份 Spec）的拆解？
