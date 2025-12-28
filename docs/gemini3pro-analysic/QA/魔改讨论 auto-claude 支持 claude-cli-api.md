# 魔改讨论: Auto-Claude 支持 Claude CLI API Key

**日期**: 2025-12-22
**分析对象**: Auto-Claude 认证机制
**目标**: 解除对 `Claude Pro/Max` 订阅的强制依赖，启用标准 `ANTHROPIC_API_KEY` 支持。

---

## 1. 背景与疑问 (Background & Question)

**核心问题**: 
Auto-Claude 官方文档明确指出，使用该工具必须拥有 `Claude Pro` 或 `Max` 订阅，并配合 `Claude Code CLI` 的 OAuth 认证使用。然而，底层的 Anthropic API 和大多数 SDK 通常都支持标准的 API Key (`sk-ant-api...`)。

**疑问**: 
1. 这种限制是技术上的硬性约束，还是人为的设计选择？
2. 既然底层的 `claude_agent_sdk` 支持 API Key，为什么 Auto-Claude 屏蔽了它？
3. 如果我的 `Claude Code CLI` 本身是使用 API Key 配置的，能否通过修改代码让 Auto-Claude 兼容？

---

## 2. 分析思路与过程 (Analysis Process)

### 2.1 初始排查
通过阅读 `README.md` 和 `cli/utils.py`，我们发现了明确的阻断逻辑：
> "Auto Claude requires Claude Code OAuth authentication. Direct API keys (ANTHROPIC_API_KEY) are not supported."

### 2.2 深度代码审计
深入核心模块，我们锁定了三个关键拦截点：

1.  **认证层 (`core/auth.py`)**: 
    - 代码中定义了 `AUTH_TOKEN_ENV_VARS` 列表，**故意**移除了 `ANTHROPIC_API_KEY`。
    - 注释明确说明了理由："We intentionally do NOT fall back to ANTHROPIC_API_KEY... to prevent silent billing".
    - 这是一个为了防止用户无意中消耗 API 额度而设计的安全网，而非技术限制。

2.  **客户端构建层 (`core/client.py`)**: 
    - 在创建 `ClaudeSDKClient` 时，代码强制将获取到的 Token 赋值给 `CLAUDE_CODE_OAUTH_TOKEN` 环境变量。
    - 这会导致即使我们强行传入 API Key，SDK 也会错误地将其作为 OAuth Token 处理，从而导致认证失败。

3.  **CLI 检查层 (`cli/utils.py`)**: 
    - `validate_environment` 函数在启动时会主动检查 OAuth Token，如果不存在直接抛出错误并退出。

### 2.3 底层 SDK 验证
通过对 `claude_agent_sdk` 的调研（官方文档及搜索结果），确认该 SDK 支持标准的 `ANTHROPIC_API_KEY` 环境变量。这意味着只要我们打通 Auto-Claude 的应用层封锁，底层完全能够正常工作。

---

## 3. 最终结论 (Conclusion)

**Auto-Claude 对 API Key 的不支持完全是应用层的人为限制。**

作者为了保护用户免受意外 API 计费的影响，在代码中硬编码了 "OAuth Only" 的策略。通过修改几处关键的 Python 代码，我们可以轻松移除这个限制，使其支持标准的 API Key 认证。

---

## 4. 可执行的修改步骤 (Implementation Plan)

以下是详细的 "魔改" 指南。请按顺序修改文件。

### 步骤 1: 解锁环境变量 (`auto-claude/core/auth.py`)

**目标**: 让系统允许读取 `ANTHROPIC_API_KEY`。

打开 `auto-claude/core/auth.py`，找到 `AUTH_TOKEN_ENV_VARS` 和 `SDK_ENV_VARS` 的定义，添加 API Key 支持。

```python
# 修改前
AUTH_TOKEN_ENV_VARS = ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN"]
SDK_ENV_VARS = ["ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "NO_PROXY", ...]

# 修改后
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN", 
    "ANTHROPIC_AUTH_TOKEN", 
    "ANTHROPIC_API_KEY"  # <--- 新增
]
SDK_ENV_VARS = [
    "ANTHROPIC_BASE_URL", 
    "ANTHROPIC_AUTH_TOKEN", 
    "ANTHROPIC_API_KEY", # <--- 新增
    "NO_PROXY", 
    ...
]
```

### 步骤 2: 智能 Token 注入 (`auto-claude/core/client.py`)

**目标**: 根据 Token 类型（API Key vs OAuth），将其注入到正确的环境变量中。

打开 `auto-claude/core/client.py`，找到 `create_client` 函数（约 135 行），修改 Token 处理逻辑：

```python
def create_client(...):
    # --- 修改开始 ---
    token = require_auth_token()
    
    # 简单的特征检测：API Key 通常以 sk-ant-api 开头，而 OAuth Token 以 sk-ant-oat 开头
    # 包含 sk- 是为了兼容可能的旧格式
    if token.startswith("sk-ant-api") or token.startswith("sk-"):
        os.environ["ANTHROPIC_API_KEY"] = token
        # 清除 OAuth 变量，防止干扰
        if "CLAUDE_CODE_OAUTH_TOKEN" in os.environ:
            del os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
    else:
        # 默认回退到 OAuth 逻辑
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token
    # --- 修改结束 ---

    # Collect env vars to pass to SDK...
    sdk_env = get_sdk_env_vars()
    
    # ...后续代码保持不变
```

### 步骤 3: 移除 CLI 报错 (`auto-claude/cli/utils.py`)

**目标**: 防止启动时因检测不到 OAuth Token 而报错退出。

打开 `auto-claude/cli/utils.py`，找到 `validate_environment` 函数：

```python
def validate_environment(spec_dir: Path) -> bool:
    valid = True

    # --- 修改开始 ---
    # 原代码会检查 get_auth_token() 并报错说不支持 API Key
    # 修改为仅检查 Token 是否存在
    if not get_auth_token():
        print("Error: No Auth token found")
        print("\nPlease set ANTHROPIC_API_KEY in .env or run 'claude setup-token'.")
        valid = False
    else:
        # 可选：打印当前使用的认证方式
        source = get_auth_token_source()
        if source:
            print(f"Auth Source: {source}")
    # --- 修改结束 ---
    
    # ...后续代码保持不变
```

### 步骤 4: 配置与运行

1.  在项目根目录创建 `.env` 文件（如果不存在）。
2.  添加你的 API Key：
    ```bash
    ANTHROPIC_API_KEY=sk-ant-api03-......
    ```
3.  运行 Auto-Claude：
    ```bash
    python auto-claude/run.py --list
    ```

---

## 5. 风险提示

1.  **计费风险**: 使用 API Key 后，每一次 Agent 思考和工具调用都会直接从你的 API 余额中扣费。Auto-Claude 的 Token 消耗量可能很大，请务必在 Anthropic Console 设置预算上限。
2.  **SDK 兼容性**: 本方案基于 "SDK 支持 API Key" 的通用假设。如果 Anthropic 在未来的 SDK 版本中移除了 API Key 支持（极不可能），此方案将失效。
