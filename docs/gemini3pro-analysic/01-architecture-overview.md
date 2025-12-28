# 01. Auto-Claude 架构概览

## 1. 系统简介
Auto-Claude 是一个专为 AI 编码工作流设计的桌面应用与 CLI 框架。它通过 "Agentic" 的方式，将复杂的开发任务分解为 Spec Creation、Planning、Implementation 和 Validation 四个阶段，并利用 Git Worktree 实现安全的隔离开发环境。

## 2. 顶层目录结构
项目采用了典型的 Monorepo 结构，包含后端框架、前端 UI 和配置管理。

```
Auto-Claude-main/
├── auto-claude/               # [Backend] Python 核心框架
│   ├── run.py                 # CLI 入口点
│   ├── cli/                   # 命令行交互层
│   ├── agents/                # AI Agent 实现 (Planner, Coder, QA)
│   ├── core/                  # 核心基础设施 (Auth, Context)
│   ├── services/              # 外部服务集成 (LLM, Linear)
│   └── ui/                    # 终端 UI 组件 (Rich TUI)
│
├── auto-claude-ui/            # [Frontend] Electron 桌面应用
│   ├── src/
│   │   ├── main/              # Electron 主进程
│   │   └── renderer/          # React 渲染进程
│   └── package.json
│
├── .auto-claude/              # [Runtime Data] 项目运行时数据 (生成的)
│   ├── specs/                 # 任务规范文档
│   ├── roadmap/               # 项目路线图
│   └── ideation/              # 创意规划
│
└── .worktrees/                # [Isolation] 隔离开发环境 (Git Worktrees)
```

## 3. 核心架构逻辑

Auto-Claude 的核心是一个基于状态机的 Agent 编排系统，辅以严格的环境隔离。

### 3.1 数据流向图 (Data Flow)

```mermaid
graph TD
    User[用户输入] -->|claude /spec| Spec[Spec 文档 (.md)]
    Spec -->|auto-claude/run.py| Planner[Planner Agent]
    
    subgraph "Phase 1: Planning"
        Planner -->|生成| Plan[Implementation Plan (.json)]
    end
    
    subgraph "Phase 2: Execution (Isolated)"
        Plan -->|读取| Coder[Coder Agent]
        Coder -->|Git Worktree| CodeBase[代码库 (Feature Branch)]
        Coder -->|更新| Plan
    end
    
    subgraph "Phase 3: Validation"
        CodeBase -->|测试| QA[QA Agent]
        QA -->|反馈| Coder
        QA -->|批准| MergeReady[准备合并]
    end
    
    MergeReady -->|--merge| MainBranch[主分支]
```

### 3.2 关键组件交互

1.  **CLI 入口 (`run.py`)**: 负责环境初始化、参数解析，并将控制权交给具体的 Command Handler。
2.  **Command Handlers (`cli/*.py`)**: 处理具体的业务逻辑，如构建 (`build_commands`)、QA (`qa_commands`) 或工作区管理 (`workspace_commands`)。
3.  **Agent Orchestrator (`agent.py`)**: 协调 Agent 的运行循环，管理上下文和记忆。
4.  **Workspace Manager (`workspace.py`)**: 负责创建和销毁 Git Worktrees，确保 AI 的操作不会直接污染主分支。

## 4. 关键技术栈

| 领域 | 技术 | 用途 |
|------|------|------|
| **Backend** | Python 3.10+ | 核心逻辑, Agent 编排 |
| **CLI UI** | Rich, Inquirer | 终端交互, 进度显示 |
| **LLM Interface** | Claude Code CLI | 与 Anthropic 模型交互 |
| **Frontend** | Electron, React | 桌面图形界面 |
| **Version Control** | Git Worktree | 环境隔离 |
| **Memory** | Graphiti (Optional) | 跨会话上下文记忆 |

## 5. 设计哲学

- **Safe by Default**: 默认在隔离的 Worktree 中运行，防止 AI 破坏现有代码。
- **Spec-Driven**: 一切始于规范文档，确保 AI "想清楚再动手"。
- **Human-in-the-Loop**: 在关键节点（Spec 审批、QA 验收、Merge）强制要求人工介入。
- **Self-Correcting**: 内置 QA 循环，Agent 会自我修正错误直到通过测试。
