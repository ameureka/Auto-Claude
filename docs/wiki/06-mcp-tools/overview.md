# MCP 工具概览

MCP (Model Context Protocol) 是 Auto-Claude 用于扩展 AI 能力的协议。

---

## 什么是 MCP？

MCP 允许 AI 代理连接到外部工具和服务：

```
┌─────────────┐     MCP      ┌────────────────┐
│   Claude    │ ←──────────→ │  外部工具/服务  │
│   Agent     │   协议       │  (记忆/测试等)  │
└─────────────┘              └────────────────┘
```

---

## 可用的 MCP 服务器

| 服务器 | 功能 | 配置 |
|--------|------|------|
| **Graphiti** | 跨会话记忆、知识图谱 | `GRAPHITI_ENABLED=true` |
| **Electron** | UI 自动化、E2E 测试 | `ELECTRON_MCP_ENABLED=true` |
| **Linear** | 项目管理同步 | `LINEAR_API_KEY=...` |
| **Context7** | 代码上下文分析 | 自动启用 |

---

## Graphiti 记忆

### 能做什么

- ✅ 记住之前会话中的代码模式
- ✅ 搜索历史实现方案
- ✅ 跨项目知识共享

### 配置

```bash
# apps/backend/.env
GRAPHITI_ENABLED=true
OPENAI_API_KEY=sk-xxx  # 用于嵌入向量
```

### 使用场景

```
用户: "上次我们是怎么实现用户认证的？"
AI: [搜索 Graphiti 记忆]
AI: "在之前的会话中，我们使用了 JWT + Redis 方案..."
```

---

## Electron E2E 测试

### 能做什么

- ✅ 自动操作 UI 界面
- ✅ 截图验证
- ✅ 表单填写和提交

### 配置

```bash
# apps/backend/.env
ELECTRON_MCP_ENABLED=true
ELECTRON_DEBUG_PORT=9222
```

### 使用场景

```
QA Agent: 点击"登录"按钮
QA Agent: 填写邮箱输入框
QA Agent: 截图验证结果
```

---

## 查看 MCP 状态

进入 **MCP Overview** 页面（侧边栏 → MCP Overview）查看：

- 已连接的 MCP 服务器
- 可用的工具列表
- 调用历史
