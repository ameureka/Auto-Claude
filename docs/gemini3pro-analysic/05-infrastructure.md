# 05. 基础设施层 (Infrastructure)

## 1. Git Worktree 隔离系统

Auto-Claude 最核心的安全机制是基于 Git Worktree 的环境隔离，由 `core/worktree.py` 中的 `WorktreeManager` 实现。

### 1.1 Per-Spec 架构
与传统的 "单一大模型上下文" 不同，Auto-Claude 为每个任务创建一个独立的物理工作区：

- **Path**: `.worktrees/{spec-name}/`
- **Branch**: `auto-claude/{spec-name}`

### 1.2 隔离优势
1.  **并行开发**: 用户可以在主分支继续工作，而 AI 在隔离的目录中编码，互不干扰（避免了文件锁冲突和 HMR 刷新问题）。
2.  **安全沙箱**: AI 的所有破坏性操作（如误删文件）仅限于 Worktree，不会影响主项目。
3.  **清晰回滚**: 丢弃一个糟糕的 Build 只需删除对应的 Worktree 和 Branch。

### 1.3 智能合并保护
在 `merge_worktree` 时，系统有一个关键保护机制：**自动 Unstage 项目元数据**。

```python
# core/worktree.py
def _unstage_gitignored_files(self):
    # 防止将 .auto-claude/ 目录下的 Spec/Plan 文件合并到主分支
    # 因为这些是 Auto-Claude 的运行时数据，不是用户代码
    for pattern in [".auto-claude/", "auto-claude/specs/"]:
        # ... git reset HEAD ...
```

## 2. 安全验证系统 (Security Validators)

位于 `auto-claude/security/`，实现了一套多层防御体系。

### 2.1 验证器类型
- **FileSystem Validators**: 限制文件操作范围（禁止访问项目目录之外的文件，禁止修改 `.git` 目录）。
- **Process Validators**: 限制 shell 命令执行。通常维护一个 Allowlist（白名单），仅允许常见的构建和测试命令（如 `npm`, `pip`, `python`, `go`）。
- **Git Validators**: 限制 Git 操作（禁止 `git push`, `git rebase` 等可能破坏远程仓库的操作）。

### 2.2 密钥扫描
`scan_secrets.py` 在提交代码前运行，扫描代码中是否硬编码了 API Key 或 Token，防止意外泄露。

## 3. 工具集基础设施

`agents/auto_claude_tools.py` 封装了提供给 LLM 的标准工具箱：

- `Read/Write/Edit`: 文件操作。
- `Bash`: 执行命令（受 Security Validator 监控）。
- `Search`: 基于 `ripgrep` 的代码搜索。
- `Git`: 基本的 Git 操作。

这些工具是 LLM 与隔离环境交互的唯一桥梁。
