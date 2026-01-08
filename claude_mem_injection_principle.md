# Claude-Mem 原理解析：自动注入与 Token 经济学

本文档详细解释 `claude-mem` 如何通过自动注入机制实现上下文管理，以及它是如何大幅节省 Token 消耗的。

## 1. 自动注入机制 (Automatic Injection)

`claude-mem` 不需要用户手动粘贴历史记录，它通过 Claude Code 的生命周期钩子实现全自动化管理：

1.  **触发 (Trigger)**：
    每当您启动 `claude` 或开始一个新的 Session 时，`SessionStart` 钩子（`src/hooks/context-hook.ts`）会被自动触发。

2.  **请求 (Request)**：
    Hook 脚本是一个轻量级的 HTTP 客户端，它向本地运行的 Worker 服务（默认端口 `37777`）发送 `/api/context/inject` 请求。

3.  **检索与组装 (Retrieval & Assembly)**：
    Worker 服务接收到请求后，执行以下操作：
    *   **查询数据库**：从 `claude-mem.db` 中检索当前项目最近的“观察结果” (Observations) 和“会话摘要” (Summaries)。
    *   **应用过滤器**：根据配置文件（`settings.json`）过滤掉敏感或低价值的信息。
    *   **构建上下文**：将检索到的数据格式化为结构化的 Markdown 文本。

4.  **注入 (Injection)**：
    最终生成的上下文文本被返回给 Claude Code，并作为**系统提示 (System Prompt)** 的一部分隐式地包含在当前对话的最前端。

## 2. Token 节省原理 (Context Economics)

传统的长对话模式通常会导致 Token 消耗呈**二次方 (O(N²))** 增长，而 `claude-mem` 将其优化为**线性 (O(N))** 增长。

### 对比分析

| 特性 | 原始上下文 (Raw Context) | Claude-Mem 压缩上下文 |
| :--- | :--- | :--- |
| **内容形式** | 包含所有用户输入、完整的工具输出（可能通过 `ls` 或 `read` 产生数千行）、思考过程等。 | 仅保留经过 AI 提炼的“观察结果”和“摘要”。 |
| **单次操作成本** | 一次 `read_file` 可能消耗 2,000+ Tokens。 | 提炼为一条观察记录仅需 ~50-100 Tokens (包含 ID、类型、标题、关键事实)。 |
| **长期增长** | 随着对话轮数增加，每次发送的 Prompt 都会包含之前的所有冗余信息。 | 旧的观察结果会被定期汇总为更高级别的“摘要”，原始细节从上下文中移除（但仍可检索）。 |
| **增长曲线** | **指数级/二次方爆炸** | **线性平稳增长** |

### 核心技术点

1.  **渐进式披露 (Progressive Disclosure)**：
    *   初始注入的只是**“索引”**（Index）。
    *   Claude 只看到：“#1042 [Refactor] 优化了登录模块”。
    *   只有当 Claude 觉得这条记录与当前任务相关时，它才会调用 `mem-search` 技能去读取 #1042 的详细内容。
    *   **效果**：默认情况下不占用详细内容的 Token。

2.  **语义去重 (Semantic Deduplication)**：
    *   Worker 会识别相似的操作。例如，如果您连续 5 次列出同一个目录，`claude-mem` 可能只会在上下文中保留最新或最具代表性的一条记录，而不是 5 条重复的日志。

3.  **概念标签 (Concept Tagging)**：
    *   每条记忆都标记有 `how-it-works`, `problem-solution`, `gotcha` 等标签。这使得 LLM 可以通过概念进行检索，而不是仅仅依赖关键词，进一步提高了检索的精准度和 Token 效率。

## 3. 验证效果

您可以通过以下方式验证 `claude-mem` 是否在工作以及节省了多少 Token：

1.  **查看启动日志**：
    Claude Code 启动时会显示如下横幅：
    ```text
    📚 Context Economics
    ━━━━━━━━━━━━━━━━━━━━
    Reading: 1.2k tokens | Full work: 48.5k tokens saved (97.5% compression)
    ```
    这表示原本 48.5k 的历史记录被压缩到了 1.2k，节省了 97.5% 的成本。

2.  **Web UI 可视化**：
    访问 `http://localhost:37777`，在 Timeline 页面可以看到每一条被作为“记忆”存储下来的记录，以及它们对应的 Token 消耗估算。

3.  **手动检查**：
    在 Claude Code 中输入 `/context` 命令（如果支持）或询问 Claude：“你现在的上下文中包含了哪些关于这个项目的历史记忆？”，它会列出注入的观察结果列表。
