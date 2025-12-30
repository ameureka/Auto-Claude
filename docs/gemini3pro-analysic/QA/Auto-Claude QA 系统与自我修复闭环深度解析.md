# Auto-Claude QA 系统与自我修复闭环深度解析

**日期**: 2025-12-22
**分析对象**: QA Loop Orchestration (`apps/backend/qa/`)

---

## 1. 核心流程：Review-Fix 闭环

Auto-Claude 的质量保证不是静态的 Linter 检查，而是一个动态的、基于代理博弈的**自愈循环**。

### 1.1 闭环状态机
1.  **Review 阶段**: `QA Reviewer` Agent 启动，读取 Spec 中的验收标准。
2.  **验证**: 执行单元测试、集成测试或 UI 截图对比。
3.  **判定**:
    - **Pass**: 标记 `approved`，任务进入完成状态。
    - **Fail**: 标记 `rejected`，生成 `QA_FIX_REQUEST.md`。
4.  **Fix 阶段**: `QA Fixer` Agent 读取错误日志和修复请求，修改源码。
5.  **Re-run**: 回到步骤 1，循环往复（最高支持 50 次迭代）。

---

## 2. 关键黑科技：自我纠错 (Self-Correction)

系统针对 AI 代理的常见行为偏差（如忘记更新 JSON 状态）设计了**负反馈机制**。

### 2.1 状态同步修正 (`reviewer.py`)
如果 Agent 在一次 Session 中完成了编码但忘记修改 `implementation_plan.json` 的状态位，系统会检测到这种“逻辑不一致”。
- **干预**: 下一次 Prompt 会包含一段特殊的 `CRITICAL` 指令，告知 Agent：
    - 上次失败的类型（例如：`missing_implementation_plan_update`）。
    - 强制执行的修复动作（必须使用 `Edit` 工具写入 `qa_signoff` 对象）。
- **效果**: 这种强力的反馈回路迫使 Agent “反思”并修正其遵循指令的能力。

---

## 3. 风险控制：人工升级策略 (Escalation)

为了防止 AI 陷入无意义的 Token 消耗黑洞，系统内置了两道防线：

### 3.1 重复问题检测 (`Recurring Issue Detection`)
- **逻辑**: 通过 `report.py` 对每次发现的 Issue 进行相似度对比。
- **阈值**: 同一个 Bug 如果出现 3 次以上，系统判定 AI 无法独立解决。
- **动作**: 触发 `escalate_to_human()`，生成包含证据链的报告，暂停自动化流程。

### 3.2 错误上限控制
- **MAX_QA_ITERATIONS (50)**: 防止逻辑极其复杂的任务陷入无限循环。
- **MAX_CONSECUTIVE_ERRORS (3)**: 如果系统连续 3 次发生底层崩溃或工具调用错误，立即停止并请求人工检查环境。

---

## 4. 与 AMEUREKA 框架的深度集成建议

1.  **注入属性测试 (Property-Based Testing)**: 
    - 修改 `qa_reviewer.md` 模板，要求其在验证时优先执行 `ameureka` 规范中定义的正确性属性检查。
2.  **强制规范验证**: 
    - 在 Review 阶段新增一个“代码准入”步骤，调用 AMEUREKA 的 `code-specs-standards` 进行规范性扫描。

---

## 5. 总结

Auto-Claude 的 QA 系统不仅仅是一个测试执行器，它是一个**具备逻辑纠偏能力的指挥系统**。
- **高韧性**: 能够处理 Agent 的疏忽。
- **高透明度**: 所有的 Review 和 Fix 过程都有详细的 MD 报告。
- **高效率**: 只有在真正遇到“认知天花板”时才会打扰人类开发者。
