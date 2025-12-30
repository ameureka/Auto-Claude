# Auto-Claude Prompt 工程与知识提取机制深度解析

**日期**: 2025-12-22
**分析对象**: Prompt Generation & Insight Extraction (`apps/backend/prompts_pkg/`, `apps/backend/analysis/`)

---

## 1. 核心理念：精准、专注、闭环

Auto-Claude 的核心竞争力在于其对 LLM 通讯的极致控制。它遵循两个基本原则：
1.  **Context Minimization (上下文最小化)**: 仅向 AI 展示完成当前子任务所必需的信息。
2.  **Autonomous Reflection (自主复盘)**: 自动从每一次改动中提炼经验并固化为记忆。

---

## 2. 动态 Prompt 生成器 (`prompt_generator.py`)

系统弃用了静态的庞大提示词，转而采用一种“积木式”的组装逻辑：

### 2.1 任务裁剪 (Task Scoping)
- **Files Section**: 明确区分 `Files to Modify`（操作目标）和 `Pattern Files`（学习样本）。
- **Verification Section**: 根据任务元数据，动态注入 `curl` 命令、`pytest` 指令或 `browser` 检查步骤。
- **作用**: 将 AI 的注意力锁定在当前子任务的 100 行代码内，而非整个工程。

### 2.2 恢复暗示 (Recovery Injection)
- **逻辑**: 如果 `attempt_count > 0`，Prompt 会自动开启“警告模式”。
- **内容**: 注入来自 `RecoveryManager` 的失败洞察（Previous attempt insights），强制要求 AI 必须更换实现路径。

---

## 3. 自动化知识提取引擎 (`insight_extractor.py`)

这是系统“越用越聪明”的秘密武器。

### 3.1 提取流程 (Post-Session Processing)
1.  **数据收集**: 抓取本次 Session 产生的 Git Diff（限制在 15000 字符内，防止溢出）。
2.  **分析模型**: 调用低成本、高速度的 `claude-3-5-haiku`。
3.  **结构化产出**:
    - `patterns_discovered`: 发现了哪些可复用的代码写法？
    - `gotchas_discovered`: 这个模块有哪些不符合常理的坑？
    - `recommendations`: 对下一个 Session 的建议。

### 3.2 记忆闭环
这些提取出的 JSON 数据通过 `memory_manager.py` 写入 `Graphiti` 知识图谱。在下一个 Agent 启动前，这些知识会通过语义搜索重新回到 Prompt 中。

---

## 4. 关键代码解析

### 4.1 环境上下文注入
```python
def generate_environment_context(project_dir, spec_dir):
    # 显式告知 AI 它是被禁锢在 Worktree 目录下的
    # 彻底杜绝绝对路径导致的执行错误
    return f"**Working Directory:** `{project_dir}` ... Your filesystem is restricted..."
```

### 4.2 智能 Prompt 组装
```python
def generate_subtask_prompt(...):
    # 根据验证类型动态切换验证指令（CLI vs API vs Browser）
    if v_type == "api":
        # 自动生成 curl 指令供 AI 直接复制执行
```

---

## 5. 对 AMEUREKA 协作的启示

1.  **注入规范模板**: 在 `generate_subtask_prompt` 的 Instructions 部分，我们可以永久性注入 AMEUREKA 的“代码质量检查清单”。
2.  **自定义洞察维度**: 可以修改 `insight_extractor.py` 的 JSON 结构，让它专门提取符合 AMEUREKA 规范的“架构洞察”。

---

## 6. 总结

Auto-Claude 的 Prompt 工程是一套精密的**信息过滤器**。它通过：
- **前置过滤**: 剔除无关文件上下文。
- **后置提炼**: 留存高价值工程经验。
实现了 Agent 蜂群在复杂工程中的稳定航行。
