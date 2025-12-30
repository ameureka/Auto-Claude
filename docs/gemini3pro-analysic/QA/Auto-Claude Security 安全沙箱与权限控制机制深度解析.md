# Auto-Claude Security 安全沙箱与权限控制机制深度解析

**日期**: 2025-12-22
**分析对象**: Security Suite (`apps/backend/security/`)

---

## 1. 核心理念：最小权限原则 (Principle of Least Privilege)

Auto-Claude 的安全设计目标是：允许 Agent 自主执行开发任务，但绝对禁止其触碰系统核心、修改敏感配置或执行破坏性操作。系统采用 **“默认阻断，按需授权”** 的白名单模式。

---

## 2. 三层防御架构 (Three-Layer Defense)

### 2.1 目录级隔离 (Directory Scoping)
- **实现**: 在 `core/client.py` 中，通过设置 `cwd` 和权限规则，强制要求所有文件读写必须使用相对路径（以 `./` 开头）。
- **效果**: 防止 Agent 访问或修改项目目录之外的任何文件（如 `/etc/passwd`）。

### 2.2 动态命令白名单 (`SecurityProfile`)
- **实现**: `project_analyzer.py` 会扫描项目依赖。
- **策略**: 
    - 如果是 Node 项目，只允许 `npm`, `npx`, `vite` 等。
    - 如果是 Python 项目，只允许 `pip`, `python`, `pytest` 等。
- **效果**: 缩小了 Agent 的攻击面，禁止其运行非必要的系统工具。

### 2.3 实时指令校验器 (`Validators`)
这是最核心的逻辑，位于 `apps/backend/security/` 目录下：

| 验证器 | 校验逻辑 | 拦截示例 |
| :--- | :--- | :--- |
| **Filesystem** | 限制 `rm` 和 `chmod` 的参数。 | 禁止 `rm -rf /` 或 `rm -rf ..` |
| **Process** | 限制 `kill` 类命令的目标。 | 禁止 `kill -9 -1`（杀掉全系统进程）。 |
| **Database** | 拦截高危数据库管理指令。 | 禁止 `dropdb`, `dropuser`。 |
| **Secret Scan** | 在提交前扫描敏感信息。 | 拦截硬编码的 `sk-ant-...` 等 Token。 |

---

## 3. 安全钩子：`bash_security_hook`

这是与 Claude SDK 交互的“安检口”：
1.  **解析**: 使用 `shlex` 将 Agent 生成的复杂 shell 字符串解析为独立的命令序列。
2.  **拆解**: 处理管道（`|`）和连接符（`&&`, `;`）。
3.  **匹配**: 每一个子命令都会在 `VALIDATORS` 注册表中查找对应的验证函数。
4.  **决策**: 只要序列中有一个命令违规，整条语句将被 `block`，并返回友好的错误信息，要求 Agent 重新思考。

---

## 4. 特色功能：密钥扫描 (Secret Scanning)

位于 `git_validators.py` 内部。在 Agent 尝试执行 `git commit` 前，系统会自动对 Staged 变更进行正则扫描。如果发现疑似 API Key，会强制拦截 commit 动作，保护用户的凭据安全。

---

## 5. 对 AMEUREKA 协作的启示

1.  **自定义白名单**: 在 AMEUREKA 框架下，您可能使用了特定的 CLI 工具（如 `kiro` 或内部脚本）。建议在 `process_validators.py` 中新增对应的 `ALLOWED_PROCESS_NAMES`。
2.  **规范强制化**: 可以编写自定义验证器，检查 `git commit` 的 message 是否符合 AMEUREKA 的约定格式，实现真正的“规范即防御”。

---

## 6. 总结

Auto-Claude 的安全系统是一个**上下文感知**的动态防护网。它不仅能防止低级的“自杀式”命令（如 `rm -rf /`），还能理解当前的工程语境，确保 Agent 始终在一个安全的、被授权的“工程围栏”内活动。
