# 02. 应用程序核心 (Application Core)

## 1. 概述
本章节深入分析 Auto-Claude 的启动流程、配置管理和核心命令分发机制。主要涉及 `run.py` 入口及其调用的 `cli` 模块。

## 2. 启动流程分析

### 2.1 入口点 (`run.py`)
`run.py` 是系统的唯一入口点，其职责非常精简：
1.  **环境检查**: 强制要求 Python 3.10+。
2.  **平台兼容性**: 在 Windows 上强制设置 stdout/stderr 为 UTF-8 编码，解决 Unicode 打印问题。
3.  **转交控制权**: 导入并调用 `cli.main()`。

```python
# apps/backend/run.py
if sys.version_info < (3, 10):
    sys.exit("Error: Auto Claude requires Python 3.10 or higher...")

if sys.platform == "win32":
    # ... Windows encoding fix ...

from cli import main
if __name__ == "__main__":
    main()
```

### 2.2 核心 CLI 逻辑 (`cli/main.py`)
`main()` 函数是真正的编排者，遵循以下流程：

1.  **环境初始化**: 调用 `setup_environment()` 加载 `.env` 文件。
2.  **参数解析**: 使用 `argparse` 定义丰富的命令行参数（`--spec`, `--qa`, `--merge` 等）。
3.  **调试启动**: 初始化 Debug 系统。
4.  **命令分发**: 根据参数标志位调用对应的 Handler。

#### 命令分发逻辑 (伪代码)
```python
def main():
    setup_environment()
    args = parse_args()
    
    if args.list:
        print_specs_list()
        return

    # 必须指定 --spec (除非是 list 或 cleanup 操作)
    if not args.spec:
        exit(1)
        
    spec_dir = find_spec(args.spec)
    
    if args.merge:
        handle_merge_command(...)
    elif args.qa:
        handle_qa_command(...)
    elif args.followup:
        handle_followup_command(...)
    else:
        # 默认进入构建流程
        handle_build_command(...)
```

## 3. 核心模块详解

### 3.1 环境配置 (`cli/utils.py`)
`setup_environment` 负责加载配置，它支持开发模式的路径回退。

- **加载逻辑**: 优先加载 `apps/backend/.env`，如果不存在则尝试 `dev/apps/backend/.env`。
- **验证逻辑** (`validate_environment`):
    - 检查 OAuth Token (`CLAUDE_CODE_OAUTH_TOKEN`)。
    - 检查 `spec.md` 是否存在。
    - 检查可选集成 (Linear, Graphiti) 的状态。

### 3.2 构建命令处理器 (`cli/build_commands.py`)
这是最复杂的处理器，负责协调整个构建生命周期。

#### 核心职责:
1.  **模型选择**: 通过 `phase_config` 获取不同阶段（Planning, Coding, QA）的模型配置。
2.  **审查检查**: 检查 `ReviewState`，确保 Spec 已被人批准（除非使用 `--force`）。
3.  **工作区设置**:
    - `ISOLATED` (默认): 创建 Git Worktree。
    - `DIRECT`: 在当前目录直接操作。
4.  **异步执行**:
    - `asyncio.run(run_autonomous_agent(...))`
    - `asyncio.run(run_qa_validation_loop(...))`
5.  **中断处理**: 捕获 `KeyboardInterrupt`，提供交互式菜单（保存指令、跳过、退出）。

### 3.3 交互式中断处理
`_handle_build_interrupt` 提供了一个非常人性化的功能：当用户按下 Ctrl+C 时，不会直接退出，而是暂停并允许用户输入新的自然语言指令。这些指令会被保存到 `HUMAN_INPUT.md`，供 Agent 在恢复运行时读取。

```python
# 交互式菜单选项
options = [
    MenuOption(key="type", label="Type instructions", ...),
    MenuOption(key="paste", label="Paste from clipboard", ...),
    MenuOption(key="file", label="Read from file", ...),
    # ...
]
```

## 4. 配置与依赖
- **配置文件**: `.env` (环境变量), `task_metadata.json` (任务元数据), `ReviewState` (审批状态)。
- **外部依赖**:
    - `claude-code`: 提供基础 LLM 能力。
    - `git`: 提供 Worktree 管理能力。

## 5. 总结
Application Core 层设计得非常健壮，特别强调了：
- **安全性**: 默认隔离环境，严格的 Token 检查。
- **可交互性**: 优雅的中断处理，丰富的 CLI 反馈。
- **模块化**: 命令处理逻辑被清晰地拆分到不同的模块中。
