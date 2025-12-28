QA Fixer Agent 提示词拆解分析 (qa_fixer.md)

  这是系统的“精准修补匠”提示词。它的核心逻辑是：“按单抓药，杜绝发散”。

  1. 核心角色设定 (The Tactical Doctor)
   * 定位：它是专门为了解决 QA Reviewer 提出的阻断性问题而设计的。
   * 核心原则：“Minimal change”。提示词反复强调只改必要的地方，严禁大范围重构，严禁在此阶段添加新功能。这极大地保证了系统的稳定性，防止“修一个 Bug 引入三个 Bug”。

  2. 上下文的精准对齐 (Phase 0 & 1)
   * 第一优先级：QA_FIX_REQUEST.md。这是它的指令来源。
   * 第二优先级：qa_report.md。这是证据链。
   * 解析逻辑：它被要求将 Fix Request 转化为一个“心理核对单”，确保每一条 Issue 都被对应到。

  3. 执行逻辑：逐一击破 (Phase 3)
   * 阅读故障点：强制先读取出错的 file:line。
   * 理解归因：问自己“为什么 QA 会标红这里？”。
   * 原子化修复：完成一个 Issue 的修复后，立即进行局部验证。

  4. 全量验证与自保机制 (Phase 4 & 5)
   * 回归意识：修完 Bug 必须跑全量测试套件，而不仅仅是出错的那个测试。这是为了防止修复逻辑导致旧功能失效。
   * 自我证明：在提交代码前，必须在日志里显式列出：Issue 1: FIXED (Verified by X)。

  5. 状态机反馈 (Phase 7)
   * 关键动作：将 implementation_plan.json 中的状态更新为 ready_for_qa_revalidation。
   * 联动：这个字段会触发 Python 编排器重新拉起 qa_reviewer。

  6. 内置的“临床经验” (Common Fix Patterns)
  提示词最后提供了一套“标准处方”，教 AI 怎么处理常见问题：
   * 数据库：如何执行迁移。
   * 测试：如何区分是代码错了还是测试写错了。
   * 控制台：如何定位前端 Runtime 错误。

  总结：QA Fixer 的本质是什么？
  QA Fixer 是一个“局部约束执行器”。它的存在解决了 AI 编程中最大的难题——“发散”。

  普通的 AI 助手在修 Bug 时往往喜欢把周围的代码也顺便重构了，导致代码库风格逐渐漂移。QA Fixer 通过 QA_FIX_REQUEST.md 的物理约束和 Prompt 里的逻辑约束，强迫 AI 像激光手术一样精准地完成任务。