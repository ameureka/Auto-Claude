# Auto-Claude 可观测性与系统恢复机制深度解析

**日期**: 2025-12-22
**分析对象**: Task Logging & Recovery Suite (`apps/backend/task_logger/`, `services/recovery.py`)

---

## 1. 核心理念：透明性与韧性 (Transparency & Resilience)

在一个自主运行的 AI 系统中，**看不见进度**和**无法从失败中恢复**是最大的两个痛点。Auto-Claude 通过“全链路日志”解决了透明性问题，通过“智能回滚与教训注入”解决了韧性问题。

---

## 2. 任务日志系统 (`TaskLogger`)

位于 `apps/backend/task_logger/`，它负责记录 Agent 的每一个呼吸。

### 2.1 结构化存储
- **文件**: 每个任务目录下的 `task_logs.json`。
- **层级**: Phase (阶段) > Session (会话) > Subtask (子任务) > Tool (工具操作)。
- **内容**: 包含原始 Prompt 摘要、LLM 思考过程、工具调用参数、执行结果及耗时。

### 2.2 实时流式标记 (Markers)
- **机制**: 采用 `emit_marker` 函数。
- **作用**: 在控制台输出特定格式的隐藏标记（如 `[MARKER:PHASE_START]`），UI 监听这些标记来实现无感知的状态同步（例如 Kanban 卡片自动从 Backlog 移动到 In Progress）。

---

## 3. 智能恢复管理器 (`RecoveryManager`)

这是系统“无人值守”的核心逻辑，位于 `services/recovery.py`。

### 3.1 错误自动归因 (Failure Classification)
系统通过正则匹配捕获 Stderr 错误，并将其归类：
- `BROKEN_BUILD`: 语法错误、缺少模块。
- `VERIFICATION_FAILED`: 代码写完了但测试没过。
- `CIRCULAR_FIX`: 陷入“修了 A 坏了 B，修了 B 坏了 A”的死循环。

### 3.2 自动化恢复策略
| 失败类型 | 恢复动作 | 逻辑 |
| :--- | :--- | :--- |
| **代码写烂了** | `Rollback` | 自动执行 `git reset --hard` 到上一个记录的 Good Commit。 |
| **逻辑死循环** | `Skip & Escalate` | 识别到重复方案后，强制标记为 `STUCK` 并申请人工介入。 |
| **上下文溢出** | `Continue` | 强制 Commit 当前进度，清空上下文并开启新 Session。 |

---

## 4. 特色黑科技：防死循环算法

系统实现了一个基于 **Jaccard 相似度** 的检查机制：
- **原理**: 记录每次尝试的 `approach`（方法描述）。
- **逻辑**: 如果当前 Agent 提出的修复方案与过去三次失败方案的关键词重合度超过 **30%**，系统判定为 `Circular Fix`。
- **意义**: 极大节省了 Token 浪费，防止 AI 在同一个逻辑坑里打转。

---

## 5. 对 AMEUREKA 协作的启示

1.  **审计追溯**: 在 AMEUREKA 规范下，可以将 `task_logs.json` 作为“交付物凭证”，证明 AI 确实执行了所有的规范检查。
2.  **强制属性检查失败恢复**: 可以定制 `classify_failure`，当 `ameureka` 的属性测试失败时，触发特定的恢复动作（如要求 Agent 重新阅读 `design.md`）。

---

## 6. 总结

Auto-Claude 的恢复机制不仅是“重试”，它包含了**感知、判断、动作、记忆**四个环节。
- **感知**: 捕获 Stderr。
- **判断**: 归类 Failure Type。
- **动作**: Git 回滚或重试。
- **记忆**: 记录失败方案作为下次的“错题提示”。
这种闭环设计使其成为了目前市面上最稳健的自主编码框架之一。
