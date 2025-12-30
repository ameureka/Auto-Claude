# 方案 1：CLI 增强（优化版）

> 基于 FPF 第一性原理推理框架优化
>
> 版本: 2.0 | 日期: 2025-01-30

---

## 一、原方案问题诊断

### 1.1 核心缺陷

原方案1 存在与主方案相同的 **SDK 兼容性问题**：

```
原方案假设: apply_auth_env() 按类型写入不同 env 变量
实际行为:   claude-agent-sdk 只读取 CLAUDE_CODE_OAUTH_TOKEN
结论:       API Key 写入 ANTHROPIC_API_KEY 后 SDK 无法读取
```

### 1.2 原方案第37行设计缺陷

```
原文: "调整 ensure_claude_code_oauth_token()：仅 OAuth 模式写入 CLAUDE_CODE_OAUTH_TOKEN"
问题: 这会导致 API Key 和 Proxy 模式下 SDK 无法获取认证
```

---

## 二、修正后的方案设计

### 2.1 核心原则

**统一入口原则**（与主方案一致）：
- 所有 Token 类型最终都必须写入 `CLAUDE_CODE_OAUTH_TOKEN`
- 这是 SDK 的唯一读取点

### 2.2 范围限定（保持不变）

| 组件 | 是否修改 | 说明 |
|------|----------|------|
| `apps/backend/` | ✅ 修改 | CLI 核心逻辑 |
| `apps/frontend/` | ❌ 不改 | 保持 OAuth only，方案2 再补 |

---

## 三、修正后的实现清单

### 3.1 apps/backend/core/auth.py

#### 扩展变量（与原方案一致）

```python
AUTH_TOKEN_ENV_VARS = [
    "CLAUDE_CODE_OAUTH_TOKEN",  # OAuth (最高优先级)
    "ANTHROPIC_AUTH_TOKEN",     # Proxy/Enterprise
    "ANTHROPIC_API_KEY",        # 直接 API (最低优先级)
]

SDK_ENV_VARS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",        # 新增
    "NO_PROXY",
    "DISABLE_TELEMETRY",
    "DISABLE_COST_WARNINGS",
    "API_TIMEOUT_MS",
]
```

#### 新增 get_token_type()（与原方案一致）

```python
def get_token_type(token: str | None) -> str:
    """检测 Token 类型"""
    if not token:
        return "unknown"
    if token.startswith("sk-ant-oat01-") or token.startswith("sk-ant-oat"):
        return "oauth"
    elif token.startswith("sk-ant-api") or (token.startswith("sk-") and "oat" not in token):
        return "api_key"
    elif token.startswith("pc_") or token.startswith("ccr-"):
        return "proxy"
    return "unknown"
```

#### 修正 apply_auth_env()（关键修正）

```python
# ============== 原方案设计（有缺陷）==============
def apply_auth_env(token):
    token_type = get_token_type(token)
    if token_type == "oauth":
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token
    elif token_type == "api_key":
        os.environ["ANTHROPIC_API_KEY"] = token      # ❌ SDK 不读
    elif token_type == "proxy":
        os.environ["ANTHROPIC_AUTH_TOKEN"] = token   # ❌ SDK 不读

# ============== 修正后设计 ==============
def apply_auth_env(token: str) -> str:
    """
    统一设置认证环境变量。

    关键修正：SDK 只读取 CLAUDE_CODE_OAUTH_TOKEN，
    因此所有 token 类型都必须写入此变量。
    """
    token_type = get_token_type(token)

    # 清理冲突变量
    for key in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        os.environ.pop(key, None)

    # 核心：统一写入 SDK 读取点
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token

    # 同时设置原生变量（用于日志/调试）
    if token_type == "api_key":
        os.environ["ANTHROPIC_API_KEY"] = token
    elif token_type == "proxy":
        os.environ["ANTHROPIC_AUTH_TOKEN"] = token

    return token_type
```

#### 修正 ensure_claude_code_oauth_token()（关键修正）

```python
# ============== 原方案设计（有缺陷）==============
# "仅 OAuth 模式写入 CLAUDE_CODE_OAUTH_TOKEN"  ❌ 错误

# ============== 修正后设计 ==============
def ensure_claude_code_oauth_token() -> None:
    """
    确保 CLAUDE_CODE_OAUTH_TOKEN 已设置。

    修正：所有模式都需要写入此变量，因为 SDK 只读这个。
    """
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return

    token = get_auth_token()
    if token:
        # 所有类型都写入（不仅是 OAuth）
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token
```

#### 新增 validate_proxy_config()

```python
def validate_proxy_config() -> tuple[bool, str]:
    """验证 Proxy 配置完整性"""
    token = get_auth_token()
    if get_token_type(token) != "proxy":
        return True, ""

    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if not base_url:
        return False, "Proxy token detected but ANTHROPIC_BASE_URL is not set"
    return True, ""
```

### 3.2 apps/backend/core/client.py

```python
def create_client(...) -> ClaudeSDKClient:
    from core.auth import apply_auth_env, validate_proxy_config

    token = require_auth_token()
    token_type = apply_auth_env(token)  # 统一注入

    # Proxy 配置校验（阻断）
    is_valid, error_msg = validate_proxy_config()
    if not is_valid:
        raise ValueError(f"Proxy configuration error: {error_msg}")

    sdk_env = get_sdk_env_vars()

    # 警告提示
    if token_type == "api_key":
        print("⚠️  WARNING: API Key mode - costs charged to your account")
    elif token_type == "proxy":
        print(f"ℹ️  Proxy mode: {os.environ.get('ANTHROPIC_BASE_URL')}")

    # ... 其余不变 ...
```

### 3.3 apps/backend/core/simple_client.py

```python
def create_simple_client(...) -> ClaudeSDKClient:
    from core.auth import apply_auth_env

    token = require_auth_token()
    apply_auth_env(token)  # 统一注入（替换原来的直接写入）

    sdk_env = get_sdk_env_vars()
    # ... 其余不变 ...
```

### 3.4 apps/backend/cli/utils.py

```python
def validate_environment(spec_dir: Path) -> bool:
    from core.auth import get_token_type, validate_proxy_config

    valid = True
    token = get_auth_token()

    if not token:
        print("Error: No authentication token found")
        print("\nSupported methods:")
        print("  1. claude setup-token (OAuth)")
        print("  2. ANTHROPIC_API_KEY (API Key)")
        print("  3. ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL (Proxy)")
        return False

    source = get_auth_token_source()
    token_type = get_token_type(token)

    print(f"Auth: {source}")
    print(f"Mode: {token_type.upper()}")

    # 模式特定处理
    if token_type == "api_key":
        print("┌────────────────────────────────────────────┐")
        print("│ ⚠️  API Key mode: costs charged directly   │")
        print("│ Set budget at: console.anthropic.com      │")
        print("└────────────────────────────────────────────┘")
    elif token_type == "proxy":
        is_valid, error_msg = validate_proxy_config()
        if not is_valid:
            print(f"Error: {error_msg}")
            return False
        print(f"Endpoint: {os.environ.get('ANTHROPIC_BASE_URL')}")

    # ... 其余校验不变 ...
    return valid
```

### 3.5 apps/backend/.env.example

```bash
# ===========================================
# Authentication (choose ONE method)
# ===========================================

# Method 1: OAuth Token (recommended)
# Run: claude setup-token
# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxxxx

# Method 2: API Key (direct billing - use with caution)
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Method 3: Proxy/Enterprise
# ANTHROPIC_AUTH_TOKEN=pc_xxxxx
# ANTHROPIC_BASE_URL=http://127.0.0.1:8999
```

---

## 四、使用方法（与原方案一致）

### API Key 模式
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

python apps/backend/run.py --list
# 输出: ⚠️ WARNING: API Key mode - costs charged to your account
```

### Proxy 模式
```bash
# .env
ANTHROPIC_AUTH_TOKEN=pc_xxxxx
ANTHROPIC_BASE_URL=http://127.0.0.1:8999

python apps/backend/run.py --list
# 输出: ℹ️ Proxy mode: http://127.0.0.1:8999
```

### OAuth 模式（保持不变）
```bash
claude setup-token
python apps/backend/run.py --list
```

---

## 五、风险评估

### 5.1 R_eff 对比

| 版本 | R_eff | 状态 |
|------|-------|------|
| 方案1 原版 | 0.30 | ❌ SDK 不兼容 |
| **方案1 修正版** | **0.82** | ✅ 推荐 |

### 5.2 风险缓解（与原方案一致）

| 风险 | 缓解措施 |
|------|----------|
| API Key 计费 | 启动警告 + 建议预算 |
| Proxy 误直连 | 强制校验 Base URL，缺失则阻断 |
| 多 Token 冲突 | apply_auth_env() 清理冲突变量 |

### 5.3 方案1 特有风险

| 风险 | 说明 | 缓解 |
|------|------|------|
| CLI/UI 不一致 | UI 仍只支持 OAuth | 文档明确说明；方案2 补齐 |
| 用户混淆 | CLI 支持多认证，UI 不支持 | 错误提示引导使用 CLI |

---

## 六、验收标准

- [ ] OAuth 模式：现有流程不受影响
- [ ] API Key 模式：正常运行 + 显示计费警告
- [ ] Proxy 模式：缺少 Base URL 时阻断；配置完整时正常运行
- [ ] simple_client：不再强制写入 OAuth env
- [ ] UI：保持 OAuth only（不改动）

---

## 七、与原方案差异总结

| 项目 | 原方案1 | 修正版 |
|------|---------|--------|
| apply_auth_env | 分离写入不同 env | 统一写入 CLAUDE_CODE_OAUTH_TOKEN |
| ensure_oauth_token | 仅 OAuth 写入 | 所有类型都写入 |
| SDK 兼容性 | ❌ API Key 无法生效 | ✅ 所有类型正常工作 |
| R_eff | 0.30 | 0.82 |

---

## 八、后续路径

方案1 完成后，可平滑过渡到方案2（全功能 UI 改造）：
1. 方案1 的 auth.py 修改可完全复用
2. 方案2 仅需补充前端 UI 组件和 env 注入逻辑
3. 渐进式改造降低风险
