# Auto-Claude 记忆系统深度解析

**日期**: 2025-12-22
**分析对象**: Auto-Claude Memory System (Graphiti & File-based)

---

## 1. 记忆系统概览 (System Overview)

Auto-Claude 并不依赖单一的上下文窗口（Context Window）来维持长期记忆，而是设计了一套**双层记忆架构 (Dual-Layer Memory Architecture)**：

| 层级 | 名称 | 技术栈 | 特性 | 适用场景 |
|------|------|--------|------|----------|
| **Primary** | **Graphiti** | Knowledge Graph (LadybugDB) | 语义搜索、跨会话关联、动态检索 | 长期记忆、经验积累、避免重复错误 |
| **Fallback** | **File-based** | JSON Files | 简单持久化、无依赖 | 审计日志、备份、Graphiti 不可用时 |

**核心理念**: 将 Agent 在编码过程中的 "Insights"（如发现的代码模式、踩过的坑、文件依赖关系）结构化存储，并在未来的任务中根据语义相关性自动检索注入。

---

## 2. 核心技术：Graphiti (Knowledge Graph)

Graphiti 是 Auto-Claude 记忆系统的灵魂。它不是简单的向量数据库，而是一个**动态知识图谱**。

### 2.1 架构特点
- **Embedded Database**: 使用 `LadybugDB` 作为嵌入式图数据库。这意味着用户**不需要安装 Docker** 或运行额外的数据库服务，它直接作为 Python 库运行，数据存储在本地文件系统 (`~/.auto-claude/memories`)。
- **Episode-based Memory**: 记忆被组织为 "Episodes"（情节）。支持多种类型：
    - `session_insight`: 会话总结
    - `pattern`: 代码模式
    - `gotcha`: 易错点/坑
    - `task_outcome`: 任务结果
- **Semantic Search**: 利用 Embedding 模型对节点进行向量化，支持语义检索。

### 2.2 多 Provider 支持
系统解耦了 LLM 和 Embedder，支持混合配置（详见 `integrations/graphiti/config.py`）：

- **LLM Provider** (用于生成/整理记忆): OpenAI, Anthropic, Azure, Ollama, Google.
- **Embedder Provider** (用于搜索记忆): OpenAI, Voyage, Azure, Ollama, Google.

---

## 3. 工作流程 (Workflow)

记忆系统介入 Agent 生命周期的两个关键点：**Save (存)** 和 **Retrieve (取)**。

### 3.1 存：Post-Session Processing
每次 Agent 会话结束后，`agents/memory_manager.py` 中的 `save_session_memory` 会被调用：

1.  **提取**: `insight_extractor` 分析本次会话的 Git Diff 和交互日志，提取 Insights。
2.  **结构化**: 将 Insights 整理为 JSON 结构 (`discoveries`, `what_worked`, `what_failed`)。
3.  **存储**:
    - 如果 Graphiti 启用：调用 `GraphitiMemory.save_session_insights`，将数据转化为图节点存入 LadybugDB。
    - 如果 Graphiti 禁用/失败：回退到 `save_file_based_memory`，保存为本地 JSON 文件。

### 3.2 取：Pre-Session Context Injection
在生成 Agent Prompt 之前，`agents/coder.py` 会调用 `get_graphiti_context`：

1.  **查询生成**: 使用当前 Subtask 的描述作为查询语句。
2.  **语义检索**: Graphiti 在知识图谱中搜索语义相关的节点（例如：当前任务涉及 "Auth"，系统会自动检索出之前关于 "Login" 模块的 Gotchas）。
3.  **注入**: 检索到的上下文被格式化为 Markdown (`## Graphiti Memory Context`)，拼接到 Prompt 的末尾。

```python
# agents/memory_manager.py
async def get_graphiti_context(...):
    # ...
    # Build search query from subtask description
    query = f"{subtask_desc} {subtask_id}".strip()
    # Get relevant context
    context_items = await memory.get_relevant_context(query, num_results=5)
    # ...
```

---

## 4. 如何配置与启用

要在你的项目中使用 Graphiti 记忆系统，你需要配置环境变量（通常在 `.env` 文件中）。

### 4.1 基础启用
```bash
GRAPHITI_ENABLED=true
```

### 4.2 选择 Provider (推荐配置)
最常见的配置是使用 Anthropic 做 LLM（因为你已经有了 Key），使用 OpenAI 做 Embedding（成本低效果好）。

```bash
# Core Config
GRAPHITI_LLM_PROVIDER=anthropic
GRAPHITI_EMBEDDER_PROVIDER=openai

# Credentials
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 4.3 纯本地配置 (Ollama)
如果你想完全本地运行（隐私优先）：

```bash
GRAPHITI_LLM_PROVIDER=ollama
GRAPHITI_EMBEDDER_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

---

## 5. 总结

Auto-Claude 的记忆系统是一个**生产级**的设计，它超越了简单的 RAG（检索增强生成），引入了知识图谱的概念。

- **优势**: 能够建立跨会话的关联（例如：A 任务修改了 Utils，B 任务使用 Utils 时能“回想”起之前的修改）。
- **实现**: 通过嵌入式数据库降低了部署门槛，通过多 Provider 支持了灵活性。
- **建议**: 强烈建议启用 Graphiti，这对处理复杂、多阶段的重构任务至关重要。
