# Auto-Claude 代理服务支持魔改方案

**日期**: 2025-12-23
**分析对象**: Auto-Claude 认证与代理配置机制
**目标**: 让 Auto-Claude 支持通过本地代理服务 (如 `127.0.0.1:8999`) 访问 Claude API

---

## 1. 背景与问题

### 1.1 当前 Claude Code CLI 配置

用户的 Claude Code CLI 使用代理服务：

```json
// ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "proxy_cast",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8999"
  }
}
```

同时，OAuth Token 存储在 macOS Keychain 中：
- **服务名**: `Claude Code-credentials`
- **Token 格式**: `sk-ant-oat01-...`

### 1.2 核心问题

Auto-Claude **不会读取** `~/.claude/settings.json`，导致：
1. 不知道要使用 `ANTHROPIC_BASE_URL=http://127.0.0.1:8999`
2. 不知道要使用 `ANTHROPIC_AUTH_TOKEN=proxy_cast`
3. 直接使用 Keychain 中的 OAuth Token 访问官方 API

---

## 2. 数据流分析

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        当前 Auto-Claude 认证流程                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. core/auth.py::get_auth_token()                                     │
│     ├── 检查 CLAUDE_CODE_OAUTH_TOKEN 环境变量                            │
│     ├── 检查 ANTHROPIC_AUTH_TOKEN 环境变量                               │
│     └── 回退到 macOS Keychain (读取 OAuth Token)                        │
│                                                                         │
│  2. core/auth.py::get_sdk_env_vars()                                   │
│     └── 收集 ANTHROPIC_BASE_URL 等环境变量 (仅从 os.environ)            │
│                                                                         │
│  3. core/client.py::create_client()                                    │
│     ├── oauth_token = require_auth_token()                             │
│     ├── os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token            │
│     ├── sdk_env = get_sdk_env_vars()  ← 这里获取 BASE_URL              │
│     └── ClaudeSDKClient(env=sdk_env)  ← 传递给 SDK                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

问题：ANTHROPIC_BASE_URL 只从 os.environ 读取，不会读取 ~/.claude/settings.json
```

---

## 3. 需要修改的文件清单

| 层级 | 文件 | 修改内容 |
|------|------|----------|
| **后端核心** | `apps/backend/core/auth.py` | 添加读取 `~/.claude/settings.json` 的功能 |
| **后端核心** | `apps/backend/core/client.py` | 确保代理配置传递给 SDK |
| **CLI 工具** | `apps/backend/cli/utils.py` | 显示代理配置状态 |
| **前端 UI** | `apps/frontend/src/main/ipc-handlers/env-handlers.ts` | 支持代理配置的读写 |
| **前端 UI** | `apps/frontend/src/shared/types/ipc.ts` | 添加代理配置类型定义 |
| **前端组件** | `apps/frontend/src/renderer/components/project-settings/` | 添加代理配置 UI |

---

## 4. 详细魔改方案

### 4.1 步骤 1: 修改 `apps/backend/core/auth.py` - 读取 Claude Code 配置

```python
# 在文件顶部添加
from pathlib import Path

def get_claude_code_settings() -> dict:
    """
    读取 Claude Code CLI 的 settings.json 配置

    Returns:
        包含 env 配置的字典，如果文件不存在则返回空字典
    """
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        return {}

    try:
        import json
        data = json.loads(settings_path.read_text())
        return data.get("env", {})
    except (json.JSONDecodeError, Exception):
        return {}


def get_auth_token() -> str | None:
    """
    Get authentication token from environment variables, Claude Code settings, or macOS Keychain.

    优先级:
    1. CLAUDE_CODE_OAUTH_TOKEN (环境变量)
    2. ANTHROPIC_AUTH_TOKEN (环境变量)
    3. ~/.claude/settings.json 中的 env 配置
    4. macOS Keychain
    """
    # 1. 检查环境变量
    for var in AUTH_TOKEN_ENV_VARS:
        token = os.environ.get(var)
        if token:
            return token

    # 2. 检查 Claude Code settings.json
    claude_settings = get_claude_code_settings()
    for var in AUTH_TOKEN_ENV_VARS:
        token = claude_settings.get(var)
        if token:
            return token

    # 3. 回退到 macOS Keychain
    return get_token_from_keychain()


def get_sdk_env_vars() -> dict[str, str]:
    """
    Get environment variables to pass to SDK.

    合并来源:
    1. os.environ (环境变量)
    2. ~/.claude/settings.json 中的 env 配置
    """
    env = {}

    # 先从 Claude Code settings.json 读取
    claude_settings = get_claude_code_settings()
    for var in SDK_ENV_VARS:
        value = claude_settings.get(var)
        if value:
            env[var] = value

    # 环境变量优先级更高，覆盖 settings.json
    for var in SDK_ENV_VARS:
        value = os.environ.get(var)
        if value:
            env[var] = value

    return env


def get_auth_token_source() -> str | None:
    """Get the name of the source that provided the auth token."""
    # 检查环境变量
    for var in AUTH_TOKEN_ENV_VARS:
        if os.environ.get(var):
            return f"env:{var}"

    # 检查 Claude Code settings.json
    claude_settings = get_claude_code_settings()
    for var in AUTH_TOKEN_ENV_VARS:
        if claude_settings.get(var):
            return f"~/.claude/settings.json:{var}"

    # 检查 macOS Keychain
    if get_token_from_keychain():
        return "macOS Keychain"

    return None
```

### 4.2 步骤 2: 修改 `apps/backend/core/client.py` - 支持代理认证

```python
# 在 create_client() 函数中，修改 token 处理逻辑

def create_client(...) -> ClaudeSDKClient:
    # 获取 SDK 环境变量（包含 ANTHROPIC_BASE_URL）
    sdk_env = get_sdk_env_vars()

    # 获取认证 token
    auth_token = require_auth_token()

    # 智能检测 token 类型并设置正确的环境变量
    if auth_token.startswith("sk-ant-api"):
        # API Key
        sdk_env["ANTHROPIC_API_KEY"] = auth_token
    elif auth_token.startswith("sk-ant-oat"):
        # OAuth Token
        sdk_env["CLAUDE_CODE_OAUTH_TOKEN"] = auth_token
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = auth_token
    else:
        # 代理 token (如 "proxy_cast") 或其他格式
        # 使用 ANTHROPIC_AUTH_TOKEN
        sdk_env["ANTHROPIC_AUTH_TOKEN"] = auth_token

    # 打印代理配置信息
    if sdk_env.get("ANTHROPIC_BASE_URL"):
        print(f"   - API Proxy: {sdk_env['ANTHROPIC_BASE_URL']}")

    # ... 后续代码不变，确保 env=sdk_env 传递给 ClaudeSDKClient
```

### 4.3 步骤 3: 修改 `apps/backend/cli/utils.py` - 显示代理状态

```python
def validate_environment(spec_dir: Path) -> bool:
    valid = True

    if not get_auth_token():
        print("Error: No authentication token found")
        # ... 错误处理
        valid = False
    else:
        source = get_auth_token_source()
        if source:
            print(f"Auth: {source}")

        # 显示代理配置
        sdk_env = get_sdk_env_vars()
        base_url = sdk_env.get("ANTHROPIC_BASE_URL")
        if base_url:
            print(f"API Proxy: {base_url}")
            # 检查代理是否可达
            try:
                import urllib.request
                urllib.request.urlopen(base_url, timeout=2)
                print(f"  Status: ✓ Reachable")
            except:
                print(f"  Status: ⚠ Not reachable (check if proxy is running)")

    # ... 后续代码不变
```

### 4.4 步骤 4: 前端 - 添加代理配置类型

**`apps/frontend/src/shared/types/ipc.ts`** (添加字段)

```typescript
export interface ProjectEnvConfig {
  // ... 现有字段

  // 代理配置 (新增)
  anthropicBaseUrl?: string;
  anthropicAuthToken?: string;
  proxyEnabled?: boolean;
}
```

### 4.5 步骤 5: 前端 - 修改环境配置处理

**`apps/frontend/src/main/ipc-handlers/env-handlers.ts`**

```typescript
// 在 generateEnvContent 函数中添加代理配置
const generateEnvContent = (config: Partial<ProjectEnvConfig>, existingContent?: string): string => {
  // ... 现有代码

  // 代理配置 (新增)
  if (config.anthropicBaseUrl !== undefined) {
    existingVars['ANTHROPIC_BASE_URL'] = config.anthropicBaseUrl;
  }
  if (config.anthropicAuthToken !== undefined) {
    existingVars['ANTHROPIC_AUTH_TOKEN'] = config.anthropicAuthToken;
  }

  // 在生成的内容中添加代理配置部分
  const content = `# Auto Claude Framework Environment Variables
# ...

# =============================================================================
# PROXY CONFIGURATION (OPTIONAL)
# =============================================================================
${existingVars['ANTHROPIC_BASE_URL'] ? `ANTHROPIC_BASE_URL=${existingVars['ANTHROPIC_BASE_URL']}` : '# ANTHROPIC_BASE_URL=http://127.0.0.1:8999'}
${existingVars['ANTHROPIC_AUTH_TOKEN'] ? `ANTHROPIC_AUTH_TOKEN=${existingVars['ANTHROPIC_AUTH_TOKEN']}` : '# ANTHROPIC_AUTH_TOKEN=proxy_cast'}

# ... 其他配置
`;
  return content;
};

// 在 ENV_GET handler 中读取代理配置
if (vars['ANTHROPIC_BASE_URL']) {
  config.anthropicBaseUrl = vars['ANTHROPIC_BASE_URL'];
  config.proxyEnabled = true;
}
if (vars['ANTHROPIC_AUTH_TOKEN']) {
  config.anthropicAuthToken = vars['ANTHROPIC_AUTH_TOKEN'];
}
```

### 4.6 步骤 6: 前端 - 添加代理配置 UI 组件

**新建 `apps/frontend/src/renderer/components/project-settings/ProxyConfigSection.tsx`**

```tsx
import { Globe, Server, CheckCircle2, AlertCircle } from 'lucide-react';
import { CollapsibleSection } from './CollapsibleSection';
import { StatusBadge } from './StatusBadge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import type { ProjectEnvConfig } from '../../../shared/types';

interface ProxyConfigSectionProps {
  isExpanded: boolean;
  onToggle: () => void;
  envConfig: ProjectEnvConfig | null;
  onUpdateConfig: (updates: Partial<ProjectEnvConfig>) => void;
}

export function ProxyConfigSection({
  isExpanded,
  onToggle,
  envConfig,
  onUpdateConfig,
}: ProxyConfigSectionProps) {
  const badge = envConfig?.proxyEnabled ? (
    <StatusBadge status="success" label="Enabled" />
  ) : (
    <StatusBadge status="default" label="Direct" />
  );

  return (
    <CollapsibleSection
      title="API Proxy Configuration"
      icon={<Server className="h-4 w-4" />}
      isExpanded={isExpanded}
      onToggle={onToggle}
      badge={badge}
    >
      <div className="space-y-4">
        {/* 启用代理开关 */}
        <div className="flex items-center justify-between">
          <div>
            <Label>Enable API Proxy</Label>
            <p className="text-xs text-muted-foreground">
              Route API requests through a local proxy server
            </p>
          </div>
          <Switch
            checked={envConfig?.proxyEnabled || false}
            onCheckedChange={(checked) => {
              if (checked) {
                onUpdateConfig({
                  proxyEnabled: true,
                  anthropicBaseUrl: envConfig?.anthropicBaseUrl || 'http://127.0.0.1:8999',
                  anthropicAuthToken: envConfig?.anthropicAuthToken || 'proxy_cast',
                });
              } else {
                onUpdateConfig({
                  proxyEnabled: false,
                  anthropicBaseUrl: undefined,
                  anthropicAuthToken: undefined,
                });
              }
            }}
          />
        </div>

        {envConfig?.proxyEnabled && (
          <>
            {/* 代理 URL */}
            <div className="space-y-2">
              <Label>Proxy URL</Label>
              <Input
                value={envConfig?.anthropicBaseUrl || ''}
                onChange={(e) => onUpdateConfig({ anthropicBaseUrl: e.target.value })}
                placeholder="http://127.0.0.1:8999"
              />
            </div>

            {/* 代理 Token */}
            <div className="space-y-2">
              <Label>Proxy Auth Token</Label>
              <Input
                value={envConfig?.anthropicAuthToken || ''}
                onChange={(e) => onUpdateConfig({ anthropicAuthToken: e.target.value })}
                placeholder="proxy_cast"
              />
              <p className="text-xs text-muted-foreground">
                Authentication token for the proxy server
              </p>
            </div>
          </>
        )}
      </div>
    </CollapsibleSection>
  );
}
```

---

## 5. 快速方案（最小修改）

如果不想修改太多代码，可以使用以下快速方案：

### 方案 A: 在 `.env` 文件中配置

在 `apps/backend/.env` 中添加：

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8999
ANTHROPIC_AUTH_TOKEN=proxy_cast
```

### 方案 B: 在启动脚本中设置

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8999
export ANTHROPIC_AUTH_TOKEN=proxy_cast
python apps/backend/run.py --spec 001
```

### 方案 C: 只修改 `core/auth.py` 自动读取配置

只需修改 `core/auth.py` 中的 `get_sdk_env_vars()` 函数（步骤 1），让它自动读取 `~/.claude/settings.json`。这是最小的代码改动，但能实现自动同步。

---

## 6. 方案对比

| 方案 | 修改量 | 效果 | 推荐场景 |
|------|--------|------|----------|
| **快速方案 A/B** | 0 行代码 | 手动配置 `.env` 或环境变量 | 临时测试 |
| **快速方案 C** | ~30 行 Python | 自动读取 Claude Code 配置 | 个人使用 |
| **完整方案** | ~200 行 | 后端自动读取 + 前端 UI 配置 | 团队/产品化 |

---

## 7. 验证步骤

修改完成后，验证代理是否工作：

```bash
# 1. 确保代理服务运行
curl http://127.0.0.1:8999/health

# 2. 运行 Auto-Claude
cd your-project
python apps/backend/run.py --list

# 3. 检查输出是否显示代理配置
# 应该看到类似：
# Auth: ~/.claude/settings.json:ANTHROPIC_AUTH_TOKEN
# API Proxy: http://127.0.0.1:8999
```

---

## 8. 风险提示

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| **代理不可用** | 代理服务未启动时 Auto-Claude 无法工作 | 添加代理可达性检查 |
| **配置冲突** | 环境变量与 settings.json 配置不一致 | 明确优先级：环境变量 > settings.json |
| **安全性** | 代理 token 可能泄露 | 确保 settings.json 权限为 600 |

---

## 9. 相关文件位置

```
Claude Code 配置:
├── ~/.claude/settings.json          # 主配置文件 (包含 env)
├── ~/.claude/settings.local.json    # 本地配置 (hooks, permissions)
└── macOS Keychain                   # OAuth Token 存储
    └── "Claude Code-credentials"

Auto-Claude 配置:
├── apps/backend/.env                 # 环境变量配置
├── apps/backend/core/auth.py         # 认证逻辑
├── apps/backend/core/client.py       # SDK 客户端创建
└── apps/backend/cli/utils.py         # CLI 工具函数
```

---

## 10. 参考资料

- [Auto-Claude 官方文档](https://github.com/anthropics/auto-claude)
- [Claude Code CLI 配置](https://docs.anthropic.com/claude-code)
- [Anthropic API 代理设置](https://docs.anthropic.com/api/proxy)
