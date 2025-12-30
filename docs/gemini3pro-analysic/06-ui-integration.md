# 06. UI 集成与通信 (UI Integration)

## 1. 架构概览

Auto-Claude 的桌面应用 (`apps/frontend`) 是一个 Electron 应用，它并不直接包含 AI 逻辑，而是作为 Python CLI 的图形化前端。

```mermaid
graph TD
    Electron[Electron Main Process] <-->|Stdio (JSON)| Python[Python CLI Process]
    Python <-->|Functions| Agents[AI Agents]
```

## 2. 通信协议 (JSON over Stdio)

UI 与后端通过标准输入输出流（Stdio）进行通信。为了支持结构化数据传输，CLI 在特定模式下（如 `--merge-preview`）会输出 JSON。

### 2.1 关键交互点
1.  **状态同步**: Python 进程通过更新 `.auto-claude/status` 文件（或类似机制）通知 UI 当前进度，UI 监听文件变化更新进度条。
2.  **命令触发**: UI 调用 `spawn('python', ['run.py', ...])` 启动任务。
3.  **预览数据**: UI 调用 `python run.py --merge-preview --spec 001`，后端计算冲突并返回 JSON，UI 渲染 Diff 视图。

## 3. 进程管理

位于 `apps/frontend/src/main/agent-manager.ts`：

- **生命周期管理**: 负责启动、停止 Python 进程。
- **环境检测**: 自动检测用户的 Python 环境（Conda, venv, System Python）。
- **优雅退出**: 在 Electron 关闭时确保杀死所有子进程（包括可能挂起的 Worktree 操作）。

## 4. 前端实现

基于 React，主要负责：
- **Spec 编辑器**: 提供富文本编辑器编写 Spec。
- **Kanban Board**: 可视化展示 Subtask 的状态 (`Pending` -> `In Progress` -> `Done`)。
- **Terminal View**: 将 Python 的 stdout/stderr 实时流式传输到前端组件，让用户看到“AI 在思考”。

## 5. 总结

这种 **"Thick Client, Thin Wrapper"** 的架构非常巧妙：
- **解耦**: 核心逻辑完全在 Python 中，CLI 可以独立运行（方便 CI/CD）。
- **稳定性**: UI 崩溃不会影响后台正在运行的 AI 任务（只要 Python 进程没死）。
- **灵活性**: 所有的复杂逻辑（如 Git 操作、LLM 调用）都由 Python 处理，Electron 只负责展示，规避了 Node.js 处理 CPU 密集型任务的弱点。
