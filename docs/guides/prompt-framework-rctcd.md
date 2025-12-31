# Auto-Claude Prompting Framework: The R.C.T.C.D Model

基于 Claude Code 内核与 Auto-Claude Agent 架构的最佳实践。

## 1. 核心哲学
在 Agent 系统中，**Prompt = Code**。
一个好的提示词不应是自然语言的聊天，而应是一份**结构化的任务说明书 (Spec)**。我们提出 **R.C.T.C.D** 模型：

| 模块 | 英文 | 关键作用 | Auto-Claude 特性结合 |
| :--- | :--- | :--- | :--- |
| **R** | **Role** | 设定思维模式与权限 | 决定调用哪个 Sub-agent (Plan/Code/QA) |
| **C** | **Context** | 划定数据边界 | 使用 `@` 挂载文件，防止 Context 爆炸 |
| **T** | **Task** | 定义原子操作 | 动词驱动 (Refactor, Create, Analyze) |
| **C** | **Constraints** | 设定安全围栏 | 禁止 `grep` 全局，禁止修改非相关文件 |
| **D** | **Deliverables** | 定义物理产出 | 指定文件路径、格式 (JSON/Markdown) |

---

## 2. 框架详解

### Role (角色设定)
不要只说 "帮我写代码"。要定义专精领域。
*   *Bad*: "写个登录页面"
*   *Good*: "你是一个 **Security-First Frontend Architect**。请基于 OWASP 标准设计登录页。"

### Context (上下文注入)
**这是 Auto-Claude 中最关键的一环。**
*   **黄金法则**: **Explicit over Implicit (显式优于隐式)**。
*   **操作**: 必须使用 `@filename` 或 `@directory` 明确挂载。
*   **反模式**: "查看项目中的历史代码..." (导致 Agent 遍历全盘，触发超时)。
*   **最佳实践**: "参考 `@src/auth/` 下的逻辑..."

### Task (任务指令)
清晰的动作指令，避免歧义。
*   使用 **CoT (Chain of Thought)** 引导： "First analyze..., then plan..., finally implement..."

### Constraints (约束条件)
Agent 就像精力过剩的实习生，必须管好手脚。
*   **Scope Constraints**: "只修改 `src/components/ui`，不要动 `src/core`。"
*   **Tool Constraints**: "禁止使用 `grep` 搜索 `node_modules`。"
*   **Tech Constraints**: "使用 Tailwind CSS，禁止写行内样式。"

### Deliverables (交付标准)
明确“做完”的标准。
*   **File-based**: "产出必须保存为 `docs/specs/01-auth.md`。"
*   **Format-based**: "输出必须是合法的 JSON，且通过 Schema 校验。"

---

## 3. 标准模板 (Copy & Paste)

在 Auto-Claude 的 **Create New Task** 界面中，推荐使用此模板：

```markdown
# Role
[定义角色，如: Senior React Refactoring Expert]

# Context (Inputs)
Please focus strictly on these resources:
1. @[关键文件1]
2. @[关键目录2]
(Note: Do NOT scan the entire repository.)

# Task
[一句话核心目标]
Step 1: Analyze...
Step 2: Plan...
Step 3: Implement...

# Constraints
- [ ] No changes to [敏感目录]
- [ ] Must use [特定技术栈]
- [ ] No global grep searches

# Deliverables
Create/Update the following files:
1. `path/to/file1.ts`
2. `path/to/doc.md` (Format: ...)
```

## 4. 实例演示

**需求**: 给现有 API 增加速率限制 (Rate Limiting)。

**Optimized Prompt**:
```markdown
# Role
Backend Security Engineer

# Context
Reference:
1. @apps/backend/core/server.py
2. @apps/backend/middleware/ (Directory)

# Task
Implement a Redis-based rate limiter middleware for the API.
1. Design the middleware class.
2. Integrate it into the server startup sequence.
3. Add unit tests.

# Constraints
- Use `redis-py` library.
- Rate limit: 100 requests/minute per IP.
- Do NOT modify existing auth logic.

# Deliverables
- `apps/backend/middleware/rate_limit.py`
- `tests/test_rate_limit.py`
```
