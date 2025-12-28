# CLI 编码代理工具设计模式与最佳实践

> 基于 Auto-Claude 项目的深度分析
> 适用于构建 AI 编码代理 CLI 工具

---

## 目录

1. [CLI 架构设计](#1-cli-架构设计)
2. [命令行参数设计](#2-命令行参数设计)
3. [子命令组织模式](#3-子命令组织模式)
4. [配置管理策略](#4-配置管理策略)
5. [错误处理和用户反馈](#5-错误处理和用户反馈)
6. [安全性设计](#6-安全性设计)
7. [可扩展性设计](#7-可扩展性设计)
8. [实战案例](#8-实战案例)

---

## 1. CLI 架构设计

### 1.1 分层架构模式

**推荐架构：**

```
┌─────────────────────────────────────┐
│   CLI Entry Point (main.py)        │  ← 参数解析、命令路由
├─────────────────────────────────────┤
│   Command Handlers                  │  ← 业务逻辑封装
│   - build_commands.py               │
│   - spec_commands.py                │
│   - qa_commands.py                  │
├─────────────────────────────────────┤
│   Core Services                     │  ← 核心功能服务
│   - Agent Orchestrator              │
│   - Worktree Manager                │
│   - Security Manager                │
├─────────────────────────────────────┤
│   Infrastructure                    │  ← 基础设施
│   - File System                     │
│   - Git Operations                  │
│   - API Clients                     │
└─────────────────────────────────────┘
```

**关键原则：**

1. **单一入口点**：所有命令通过一个入口文件路由
2. **命令处理器分离**：每类命令独立模块
3. **服务层抽象**：核心逻辑与 CLI 解耦
4. **基础设施隔离**：底层操作独立封装

### 1.2 命令路由模式

**Pattern: Command Router**

```python
def main() -> None:
    """主入口：解析参数并路由到对应的命令处理器"""
    args = parse_args()

    # 路由逻辑：优先级从高到低
    if args.list:
        return handle_list_command(args)

    if args.merge:
        return handle_merge_command(args)

    if args.review:
        return handle_review_command(args)

    if args.discard:
        return handle_discard_command(args)

    if args.qa:
        return handle_qa_command(args)

    if args.qa_status:
        return handle_qa_status_command(args)

    # 默认命令
    return handle_build_command(args)
```

**优势：**
- ✅ 清晰的命令优先级
- ✅ 易于添加新命令
- ✅ 集中的路由逻辑

---

## 2. 命令行参数设计

### 2.1 互斥组（Mutually Exclusive Groups）

**问题：** 某些选项不能同时使用（如 `--merge` 和 `--discard`）

**解决方案：**

```python
import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # 工作空间模式（互斥）
    workspace_group = parser.add_mutually_exclusive_group()
    workspace_group.add_argument(
        "--isolated",
        action="store_true",
        help="Run in isolated worktree (default)"
    )
    workspace_group.add_argument(
        "--direct",
        action="store_true",
        help="Run directly in project (dangerous)"
    )

    # 构建管理命令（互斥）
    build_group = parser.add_mutually_exclusive_group()
    build_group.add_argument("--merge", action="store_true")
    build_group.add_argument("--review", action="store_true")
    build_group.add_argument("--discard", action="store_true")

    return parser.parse_args()
```

**效果：**
```bash
# ✅ 正确
python run.py --spec 001 --merge

# ❌ 错误：自动报错
python run.py --spec 001 --merge --discard
# error: argument --discard: not allowed with argument --merge
```

### 2.2 布尔标志 vs 值参数

**设计原则：**

| 类型 | 使用场景 | 示例 |
|------|---------|------|
| **布尔标志** | 开关功能 | `--verbose`, `--force`, `--dry-run` |
| **值参数** | 需要输入 | `--spec 001`, `--model opus`, `--branch main` |

**实现：**

```python
# 布尔标志
parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    help="Enable verbose output"
)

# 值参数
parser.add_argument(
    "--spec",
    type=str,
    required=True,
    help="Spec ID or name (e.g., 001 or 001-feature)"
)

# 可选值参数（带默认值）
parser.add_argument(
    "--model",
    type=str,
    default="claude-sonnet-4",
    help="Claude model to use (default: claude-sonnet-4)"
)
```

### 2.3 参数验证

**Pattern: Early Validation**

```python
def validate_args(args: argparse.Namespace) -> None:
    """在执行命令前验证参数"""

    # 验证 spec 格式
    if args.spec and not is_valid_spec_format(args.spec):
        raise ValueError(
            f"Invalid spec format: {args.spec}\n"
            f"Expected: 001 or 001-feature-name"
        )

    # 验证文件存在
    if args.config and not Path(args.config).exists():
        raise FileNotFoundError(f"Config file not found: {args.config}")

    # 验证环境变量
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        raise EnvironmentError(
            "CLAUDE_CODE_OAUTH_TOKEN not set.\n"
            "Run: claude setup-token"
        )
```

---

## 3. 子命令组织模式

### 3.1 模块化命令处理器

**目录结构：**

```
cli/
├── __init__.py
├── main.py                 # 入口和路由
├── build_commands.py       # 构建相关命令
├── spec_commands.py        # Spec 管理命令
├── qa_commands.py          # QA 验证命令
├── workspace_commands.py   # 工作空间管理
├── followup_commands.py    # 后续任务命令
└── utils.py               # 共享工具函数
```

**命令处理器模板：**

```python
# build_commands.py
from pathlib import Path
from .utils import load_spec, print_status

def handle_build_command(args) -> None:
    """处理构建命令"""

    # 1. 加载配置
    project_dir = Path.cwd()
    spec_dir = load_spec(args.spec, project_dir)

    # 2. 验证前置条件
    if not spec_dir.exists():
        print_status(f"Spec not found: {args.spec}", "error")
        return

    # 3. 执行核心逻辑
    try:
        print_status(f"Building spec: {args.spec}", "info")
        result = run_build(project_dir, spec_dir, args)

        if result.success:
            print_status("Build completed successfully", "success")
        else:
            print_status(f"Build failed: {result.error}", "error")

    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        raise
```

### 3.2 命令依赖管理

**Pattern: Command Prerequisites**

```python
def handle_merge_command(args) -> None:
    """合并命令：需要先完成构建"""

    # 检查前置条件
    prerequisites = [
        ("spec_exists", lambda: spec_dir.exists()),
        ("build_complete", lambda: is_build_complete(spec_dir)),
        ("qa_passed", lambda: has_qa_passed(spec_dir)),
    ]

    for name, check in prerequisites:
        if not check():
            print_status(f"Prerequisite failed: {name}", "error")
            print_help_for_prerequisite(name)
            return

    # 执行合并
    merge_worktree(spec_dir, args)
```

---

## 4. 配置管理策略

### 4.1 配置优先级

**推荐优先级：** 命令行参数 > 环境变量 > 配置文件 > 默认值

```python
def get_config_value(
    arg_value: str | None,
    env_var: str,
    config_key: str,
    default: str
) -> str:
    """按优先级获取配置值"""

    # 1. 命令行参数（最高优先级）
    if arg_value is not None:
        return arg_value

    # 2. 环境变量
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value

    # 3. 配置文件
    config = load_config_file()
    if config and config_key in config:
        return config[config_key]

    # 4. 默认值
    return default

# 使用示例
model = get_config_value(
    arg_value=args.model,
    env_var="AUTO_BUILD_MODEL",
    config_key="default_model",
    default="claude-sonnet-4"
)
```

### 4.2 配置文件设计

**推荐格式：** JSON（易于解析）或 YAML（易于阅读）

```json
// .auto-claude.json
{
  "default_model": "claude-sonnet-4",
  "default_branch": "main",
  "worktree_dir": ".worktrees",
  "security": {
    "sandbox_enabled": true,
    "allowed_commands": ["git", "npm", "python"]
  },
  "memory": {
    "graphiti_enabled": false,
    "file_based_enabled": true
  }
}
```

**加载配置：**

```python
import json
from pathlib import Path

def load_config(project_dir: Path) -> dict:
    """加载项目配置文件"""
    config_file = project_dir / ".auto-claude.json"

    if not config_file.exists():
        return get_default_config()

    try:
        with open(config_file) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print_warning(f"Invalid config file: {e}")
        return get_default_config()
```

### 4.3 环境变量管理

**Pattern: .env File Support**

```python
from pathlib import Path

def load_env_file(project_dir: Path) -> None:
    """加载 .env 文件"""
    env_file = project_dir / ".env"

    if not env_file.exists():
        return

    with open(env_file) as f:
        for line in f:
            line = line.strip()

            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue

            # 解析 KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
```

---

## 5. 错误处理和用户反馈

### 5.1 分层日志系统

**三层日志架构：**

```python
# 1. 任务日志（持久化，供 AI 读取）
class TaskLogger:
    def log(self, message: str, level: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self._append_to_file(entry)

# 2. 调试日志（开发时使用）
def debug(module: str, message: str):
    if os.environ.get("DEBUG"):
        print(f"[DEBUG:{module}] {message}", file=sys.stderr)

# 3. 用户状态（友好的进度显示）
def print_status(message: str, status: str):
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "progress": "⏳"
    }
    icon = icons.get(status, "•")
    print(f"{icon} {message}")
```

### 5.2 进度显示

**Pattern: Progress Indicator**

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def run_with_progress(task_name: str, func, *args, **kwargs):
    """显示进度的任务执行"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task(task_name, total=None)

        try:
            result = func(*args, **kwargs)
            progress.update(task, description=f"✅ {task_name}")
            return result
        except Exception as e:
            progress.update(task, description=f"❌ {task_name}")
            raise

# 使用示例
result = run_with_progress(
    "Building spec 001",
    run_build,
    project_dir,
    spec_dir
)
```

### 5.3 错误消息设计

**原则：** 可操作的错误消息

```python
def handle_error(error: Exception, context: dict) -> None:
    """处理错误并提供可操作的建议"""

    if isinstance(error, FileNotFoundError):
        print_status(
            f"File not found: {error.filename}\n"
            f"💡 Tip: Check if the spec exists with: python run.py --list",
            "error"
        )

    elif isinstance(error, EnvironmentError):
        print_status(
            f"Environment error: {error}\n"
            f"💡 Tip: Run 'claude setup-token' to configure authentication",
            "error"
        )

    elif isinstance(error, SecurityError):
        print_status(
            f"Security error: {error}\n"
            f"💡 Tip: Review allowed commands in .auto-claude-security.json",
            "error"
        )

    else:
        print_status(f"Unexpected error: {error}", "error")
        if context.get("verbose"):
            import traceback
            traceback.print_exc()
```

---

## 6. 安全性设计

### 6.1 命令白名单

**Pattern: Dynamic Allowlist**

```python
class SecurityManager:
    """管理命令白名单"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.profile = self._load_or_create_profile()

    def _load_or_create_profile(self) -> SecurityProfile:
        """加载或创建安全配置"""
        cache_file = self.project_dir / ".auto-claude-security.json"

        if cache_file.exists():
            return self._load_cached_profile(cache_file)

        # 分析项目并生成配置
        profile = self._analyze_project()
        self._save_profile(cache_file, profile)
        return profile

    def _analyze_project(self) -> SecurityProfile:
        """分析项目技术栈并生成白名单"""
        allowed_commands = set(BASE_COMMANDS)

        # 检测语言
        if (self.project_dir / "package.json").exists():
            allowed_commands.update(NODE_COMMANDS)

        if (self.project_dir / "requirements.txt").exists():
            allowed_commands.update(PYTHON_COMMANDS)

        # 解析自定义脚本
        custom_scripts = self._parse_custom_scripts()
        allowed_commands.update(custom_scripts)

        return SecurityProfile(allowed_commands=allowed_commands)

    def is_command_allowed(self, command: str) -> bool:
        """检查命令是否在白名单中"""
        cmd_name = command.split()[0]
        return cmd_name in self.profile.allowed_commands
```

### 6.2 沙箱执行

**Pattern: Sandboxed Execution**

```python
def execute_command_safely(
    command: str,
    cwd: Path,
    security_manager: SecurityManager
) -> subprocess.CompletedProcess:
    """在沙箱中安全执行命令"""

    # 1. 验证命令白名单
    if not security_manager.is_command_allowed(command):
        raise SecurityError(
            f"Command not allowed: {command}\n"
            f"Allowed commands: {security_manager.get_allowed_commands()}"
        )

    # 2. 限制工作目录
    if not cwd.is_relative_to(security_manager.project_dir):
        raise SecurityError(f"Cannot execute outside project: {cwd}")

    # 3. 执行命令
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        return result

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out: {command}")
```

---

## 7. 可扩展性设计

### 7.1 插件系统

**Pattern: Hook System**

```python
from typing import Callable, Dict, List

class HookManager:
    """管理命令钩子"""

    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}

    def register(self, event: str, callback: Callable):
        """注册钩子"""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)

    def trigger(self, event: str, *args, **kwargs):
        """触发钩子"""
        if event in self.hooks:
            for callback in self.hooks[event]:
                callback(*args, **kwargs)

# 使用示例
hooks = HookManager()

# 注册钩子
hooks.register("pre_build", lambda spec: print(f"Building {spec}"))
hooks.register("post_build", lambda spec: print(f"Completed {spec}"))

# 触发钩子
hooks.trigger("pre_build", spec_name)
run_build(...)
hooks.trigger("post_build", spec_name)
```

### 7.2 命令扩展

**Pattern: Command Registry**

```python
class CommandRegistry:
    """命令注册表"""

    def __init__(self):
        self.commands: Dict[str, Callable] = {}

    def register(self, name: str, handler: Callable):
        """注册命令"""
        self.commands[name] = handler

    def execute(self, name: str, args):
        """执行命令"""
        if name not in self.commands:
            raise ValueError(f"Unknown command: {name}")

        return self.commands[name](args)

# 使用示例
registry = CommandRegistry()

# 注册内置命令
registry.register("build", handle_build_command)
registry.register("merge", handle_merge_command)

# 注册自定义命令
registry.register("deploy", handle_deploy_command)

# 执行命令
registry.execute(args.command, args)
```

---

## 8. 实战案例

### 8.1 完整的 CLI 入口示例

```python
#!/usr/bin/env python3
"""
Auto Claude CLI
===============

Usage:
    python run.py --spec 001
    python run.py --spec 001 --merge
    python run.py --list
"""

import sys
import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auto Claude - Autonomous coding framework"
    )

    # 核心参数
    parser.add_argument("--spec", type=str, help="Spec ID or name")
    parser.add_argument("--list", action="store_true", help="List all specs")

    # 工作空间模式
    workspace_group = parser.add_mutually_exclusive_group()
    workspace_group.add_argument("--isolated", action="store_true")
    workspace_group.add_argument("--direct", action="store_true")

    # 构建管理
    build_group = parser.add_mutually_exclusive_group()
    build_group.add_argument("--merge", action="store_true")
    build_group.add_argument("--review", action="store_true")
    build_group.add_argument("--discard", action="store_true")

    # QA 选项
    parser.add_argument("--qa", action="store_true")
    parser.add_argument("--qa-status", action="store_true")

    # 通用选项
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--model", type=str, default="claude-sonnet-4")

    return parser.parse_args()

def main() -> None:
    """主入口"""
    try:
        args = parse_args()

        # 加载配置
        project_dir = Path.cwd()
        load_env_file(project_dir)

        # 验证参数
        validate_args(args)

        # 路由命令
        if args.list:
            handle_list_command(args)
        elif args.merge:
            handle_merge_command(args)
        elif args.review:
            handle_review_command(args)
        elif args.discard:
            handle_discard_command(args)
        elif args.qa:
            handle_qa_command(args)
        elif args.qa_status:
            handle_qa_status_command(args)
        else:
            handle_build_command(args)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)

    except Exception as e:
        handle_error(e, {"verbose": args.verbose if 'args' in locals() else False})
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 8.2 命令处理器示例

```python
# build_commands.py
from pathlib import Path
from .utils import print_status, load_spec

def handle_build_command(args) -> None:
    """处理构建命令"""

    # 1. 验证前置条件
    if not args.spec:
        print_status("Error: --spec is required", "error")
        print("Usage: python run.py --spec 001")
        return

    # 2. 加载配置
    project_dir = Path.cwd()
    spec_dir = load_spec(args.spec, project_dir)

    if not spec_dir.exists():
        print_status(f"Spec not found: {args.spec}", "error")
        print("💡 Tip: List available specs with: python run.py --list")
        return

    # 3. 创建工作空间
    if not args.direct:
        print_status("Creating isolated worktree...", "info")
        worktree = create_worktree(project_dir, args.spec)
        working_dir = worktree.path
    else:
        working_dir = project_dir

    # 4. 执行构建
    try:
        print_status(f"Building spec: {args.spec}", "info")

        result = run_build(
            project_dir=working_dir,
            spec_dir=spec_dir,
            model=args.model,
            verbose=args.verbose
        )

        if result.success:
            print_status("✅ Build completed successfully", "success")
            print(f"\n📁 Review changes: cd {working_dir}")
            print(f"🔀 Merge to main: python run.py --spec {args.spec} --merge")
        else:
            print_status(f"❌ Build failed: {result.error}", "error")

    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        raise
```

---

## 9. 总结

### 9.1 核心设计原则

1. **用户友好**：清晰的命令结构、友好的错误消息
2. **安全优先**：命令白名单、沙箱执行、权限控制
3. **模块化**：命令处理器分离、服务层抽象
4. **可扩展**：插件系统、命令注册表、钩子机制
5. **配置灵活**：多层配置优先级、环境变量支持

### 9.2 关键模式

| 模式 | 用途 | 优势 |
|------|------|------|
| **Command Pattern** | 命令封装 | 易于扩展、撤销/重做 |
| **Strategy Pattern** | 行为选择 | 运行时切换策略 |
| **Facade Pattern** | 接口简化 | 隐藏复杂性 |
| **Hook System** | 扩展点 | 插件化架构 |
| **Registry Pattern** | 命令注册 | 动态添加命令 |

### 9.3 最佳实践清单

- ✅ 使用互斥组防止冲突选项
- ✅ 提供清晰的帮助信息和示例
- ✅ 实现配置优先级（CLI > ENV > Config > Default）
- ✅ 分层日志系统（任务、调试、用户）
- ✅ 可操作的错误消息
- ✅ 进度显示和状态反馈
- ✅ 命令白名单和安全验证
- ✅ 模块化命令处理器
- ✅ 钩子系统支持扩展
- ✅ 优雅的错误处理和恢复

---

**文档版本：** 1.0
**最后更新：** 2025-12-22
**参考项目：** Auto-Claude v2.7.1
