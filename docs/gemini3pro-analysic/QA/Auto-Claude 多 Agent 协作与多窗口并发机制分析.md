# Auto-Claude 多 Agent 协作与多窗口并发机制分析

**日期**: 2025-12-22
**分析对象**: Agent Roles & Terminal Concurrency (`auto-claude/services/`, `auto-claude-ui/src/main/terminal/`)

---

## 1. Agent 系统角色设计 (Agent Roles)

Auto-Claude 并非只有一种 Agent，它通过不同的 Prompt 模板和工具权限，定义了一套完整的开发流水线角色：

| Agent 角色 | 实现位置 | 核心功能 |
| :--- | :--- | :--- |
| **Planner** | `agents/planner.py` | 静态分析 Spec，生成 Subtask 清单（Implementation Plan）。 |
| **Coder** | `agents/coder.py` | 核心实现者，负责读取 Subtask 并编写代码。 |
| **QA Reviewer** | `qa/reviewer.py` | 验证者，按照验收标准（Acceptance Criteria）检查代码。 |
| **QA Fixer** | `qa/fixer.py` | 修复者，根据 Reviewer 的报错信息进行针对性修复。 |
| **Orchestrator**| `services/orchestrator.py` | 环境编排，管理 Docker/Local 服务的启动与健康监测。 |

---

## 2. 并发窗口机制 (Multi-Terminal Architecture)

Auto-Claude 最显著的特性是支持同时开启多个 `claude-code` 窗口。其底层实现原理如下：

### 2.1 PTY 虚拟化 (Pseudo-Terminal)
Electron 主进程利用 `node-pty` 库为每个 Tab 开启一个独立的子进程。
- **管理器**: `src/main/terminal/terminal-manager.ts` 负责维护一个 `Map<string, TerminalProcess>`。
- **通信**: 输入（Stdin）和输出（Stdout）通过 IPC 实现实时双向流转。

### 2.2 环境隔离的核心：Git Worktree
这是多窗口并发不冲突的**技术保障**。
- 每个终端窗口通常对应一个独立的 **Git Worktree**。
- **原理**: `claude-code` 需要操作 `.git` 索引。传统的单目录多分支切换会导致冲突。通过 Worktree，每个窗口拥有独立的物理目录和独立的 Git 状态，从而允许 12 个 `claude-code` 实例同时读写代码。

---

## 3. 多 Agent 并发处理逻辑

并发处理分为两个层级：

### 3.1 任务级并发
用户可以同时启动多个 Feature Spec。每个任务都会触发：
1.  **Worktree 创建**: 为新任务分配物理目录。
2.  **PTY 启动**: 在该目录下启动一个新的 `claude-code` 会话。
3.  **上下文注入**: UI 自动发送指令给终端，使其加载特定任务的 `implementation_plan.json`。

### 3.2 服务级并发 (`ServiceOrchestrator`)
在进行 QA 或测试时，Python 后端能够：
- 自动解析 `docker-compose.yml`。
- 并行启动多个依赖服务（如 DB, Redis, API）。
- 通过 `socket` 监听端口直到服务 Ready，再让 QA Agent 开始测试。

---

## 4. 关键代码解析

### 4.1 终端管理中枢 (`TerminalManager`)
```typescript
// pro-Auto-Claude/Auto-Claude-main/auto-claude-ui/src/main/terminal/terminal-manager.ts
export class TerminalManager {
  private terminals: Map<string, TerminalProcess> = new Map();
  // 创建新窗口并启动 Claude 实例
  async create(options: TerminalCreateOptions) {
    return TerminalLifecycle.createTerminal(options, this.terminals, ...);
  }
}
```

### 4.2 环境编排器 (`ServiceOrchestrator`)
```python
# pro-Auto-Claude/Auto-Claude-main/auto-claude/services/orchestrator.py
class ServiceOrchestrator:
    def start_services(self):
        if self._compose_file:
            return self._start_docker_compose() # 启动容器化并发环境
        else:
            return self._start_local_services() # 启动本地多进程环境
```

---

## 5. 总结

**设计哲学**: 
Auto-Claude 并没有尝试在一个进程里处理所有事情，而是采用了 **"分而治之"** 的策略：
1.  **物理隔离**: 靠 Git Worktree 解决文件冲突。
2.  **进程隔离**: 靠 PTY 解决交互冲突。
3.  **逻辑编排**: 靠 Python 后端解决环境依赖。

这种架构使得它成为了一个真正的“**AI 蜂群开发工具**”，而非简单的聊天机器人。
