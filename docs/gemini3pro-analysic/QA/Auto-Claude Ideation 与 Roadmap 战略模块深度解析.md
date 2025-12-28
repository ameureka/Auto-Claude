# Auto-Claude Ideation 与 Roadmap 战略模块深度解析

**日期**: 2025-12-22
**分析对象**: Ideation Orchestrator & Prediction Engine

---

## 1. 模块定位 (Strategic Positioning)

Auto-Claude 的 Ideation 和 Roadmap 模块超越了传统的代码补全，它们负责**“定义做什么”**和**“如何做得更好”**。

| 模块 | 核心职责 | 处理维度 | 技术特征 |
| :--- | :--- | :--- | :--- |
| **Ideation** | 发现项目潜在改进点 | 横向全方位扫描 | 并行 Agent 蜂群、RAG 增强 |
| **Prediction**| 预测实现过程中的 Bug | 纵向 Subtask 深度分析 | 模式匹配、风险预防清单 |
| **Roadmap**  | 规划功能迭代路径 | 战略演进 | 受众分析、优先级排序 |

---

## 2. Ideation 并行编排架构 (`ideation/runner.py`)

系统实现了一套名为 `IdeationOrchestrator` 的状态机，将创意生成分解为四个高效阶段：

### 2.1 阶段 1：项目全索引 (Project Indexing)
- **动作**: 扫描文件树、依赖关系、技术栈（Tech Stack）。
- **优化**: 具备智能缓存机制，仅在依赖文件修改时才重新构建索引。

### 2.2 阶段 2：上下文与图谱增强 (Context Gathering)
- **动作**: 并行拉取 `Graphiti` 知识图谱中的历史记忆和代码模式暗示。
- **作用**: 确保创意不是凭空捏造，而是基于项目历史“Gotchas”（踩过的坑）。

### 2.3 阶段 3：多维并行生成 (Parallel Generation)
- **核心**: 使用 `asyncio.gather` 同时运行 6+ 个专用 Agent。
- **维度**:
    - `Security`: 漏洞扫描建议。
    - `Performance`: 瓶颈分析建议。
    - `Code Quality`: 重构与设计模式建议。
    - `UI/UX`: 交互体验提升。
- **优势**: 将原本需要数小时的人工架构评审缩短至分钟级。

### 2.4 阶段 4：合并与持久化 (Merge & Finalize)
- **动作**: 汇总所有 Agent 的 JSON 产出，生成最终的 `ideation.json`。

---

## 3. 预测性 Bug 预防引擎 (`prediction/main.py`)

这是 Auto-Claude 的另一项核心技术，旨在实现 **"Shift Left"（测试左移）**：

- **触发时机**: 在 Planner 拆解出 Subtask 后，但在 Coder 开始写代码前。
- **逻辑流程**:
    1. 读取 Subtask 的受影响文件。
    2. 检索这些文件的 `patterns_from`（参考代码）。
    3. **AI 推理**: “如果你参照 A 模式修改 B 文件，通常会忘记修改 C 处的配置”。
- **产出物**: `checklist.md`。这份清单会被注入到 Coder Agent 的 Prompt 中，强制其在编写代码时自我检查这些潜在风险。

---

## 4. 与 AMEUREKA 框架的协作建议

1.  **注入 AMEUREKA 规范**: 在 Ideation 阶段，将 AMEUREKA 的 `03-design-standard.md` 作为全局上下文。这样生成的“创意”会自动倾向于“符合规范的重构”。
2.  **基于属性的 Checklist**: 修改 Prediction 模块，使其生成的 Checklist 包含 AMEUREKA 定义的**正确性属性（Correctness Properties）**。

---

## 5. 总结

Auto-Claude 的这两个模块体现了其**“架构师思维”**：
- 它不仅仅完成了你分配的任务，还主动告诉你“你的安全配置可以优化”、“你的 UI 性能有待提升”。
- 通过**并行 Agent 扫描**，它实现了极高的诊断密度，是目前 AI 编程领域中最接近“虚拟高级工程师”的实现方案。
