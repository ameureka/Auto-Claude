# Requirements Document: CLI Multi-Auth Support

## Introduction

为 Auto-Claude CLI 添加多认证支持，允许用户使用 OAuth Token、API Key 或 Proxy Token 进行认证，同时保持向后兼容性和安全性。

## Glossary

- **AuthModule**: `apps/backend/core/auth.py` 认证模块，负责 Token 获取、类型识别和环境变量注入
- **ClientFactory**: `apps/backend/core/client.py` SDK 客户端工厂，负责创建配置好的 ClaudeSDKClient
- **SimpleClientFactory**: `apps/backend/core/simple_client.py` 简化客户端工厂，用于单轮工具操作
- **CLIValidator**: `apps/backend/cli/utils.py` CLI 环境验证模块
- **SDK**: `claude-agent-sdk` 包，Auto-Claude 的唯一 AI 交互层
- **CLI**: Claude Code CLI，SDK 底层调用的命令行工具，实际处理认证
- **OAuth_Token**: Claude Code CLI 颁发的订阅凭证，前缀 `sk-ant-oat01-` 或 `sk-ant-oat`
- **API_Key**: Anthropic Console 直接计费密钥，前缀 `sk-ant-api` 或通用 `sk-`（排除 oat）
- **Proxy_Token**: 企业代理/ProxyCast 凭证，前缀 `pc_` 或 `ccr-`

## Requirements

### Requirement 1: Token Type Detection

**User Story:** As a developer, I want the system to automatically detect my token type, so that I don't need to manually configure the authentication mode.

#### Acceptance Criteria

1. WHEN the AuthModule receives a token starting with `sk-ant-oat01-` or `sk-ant-oat`, THE AuthModule SHALL classify the token as `oauth` type.

2. WHEN the AuthModule receives a token starting with `sk-ant-api`, THE AuthModule SHALL classify the token as `api_key` type. WHEN the AuthModule receives a token starting with `sk-` but NOT starting with `sk-ant-oat` and NOT starting with `sk-ant-api`, THE AuthModule SHALL also classify the token as `api_key` type (fallback for generic Anthropic keys).

**Note**: Classification order is critical: OAuth prefixes (`sk-ant-oat`) MUST be checked before API Key prefixes (`sk-ant-api`, then generic `sk-`).

3. WHEN the AuthModule receives a token starting with `pc_` or `ccr-`, THE AuthModule SHALL classify the token as `proxy` type.

4. WHEN the AuthModule receives a token not matching any known pattern, THE AuthModule SHALL classify the token as `unknown` type.

### Requirement 2: Type-Specific Environment Injection

**User Story:** As a developer, I want all token types to work with the SDK/CLI, so that I can use any authentication method seamlessly.

#### Acceptance Criteria

1. WHEN the token type is `oauth`, THE AuthModule SHALL write the token to `CLAUDE_CODE_OAUTH_TOKEN` environment variable.

2. WHEN the token type is `api_key`, THE AuthModule SHALL write the token to `ANTHROPIC_API_KEY` environment variable.

3. WHEN the token type is `proxy`, THE AuthModule SHALL write the token to `ANTHROPIC_AUTH_TOKEN` environment variable.

4. WHEN applying authentication environment, THE AuthModule SHALL clear conflicting variables (`CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`) before injection to prevent ambiguity.

**Note - CLI Authentication Behavior**: The Claude Code CLI reads authentication from type-specific environment variables:
- `CLAUDE_CODE_OAUTH_TOKEN` for OAuth subscription tokens
- `ANTHROPIC_API_KEY` for direct API access
- `ANTHROPIC_AUTH_TOKEN` for proxy/enterprise setups (with `ANTHROPIC_BASE_URL`)

### Requirement 3: Token Resolution Priority

**User Story:** As a developer, I want a clear priority order when multiple tokens exist, so that the system behaves predictably.

#### Acceptance Criteria

1. THE AuthModule SHALL resolve tokens in priority order: `CLAUDE_CODE_OAUTH_TOKEN` → `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY`.

2. WHEN multiple token environment variables exist, THE AuthModule SHALL use the highest priority token and ignore others.

3. WHEN no token is found in environment variables on macOS, THE AuthModule SHALL attempt to retrieve token from macOS Keychain.

### Requirement 4: Proxy Configuration Validation

**User Story:** As a developer using a proxy, I want the system to validate my configuration early, so that I don't waste time with misconfigured setups.

#### Acceptance Criteria

1. WHEN the token type is `proxy`, THE CLIValidator SHALL check for `ANTHROPIC_BASE_URL` environment variable during environment validation.

2. IF the token type is `proxy` and `ANTHROPIC_BASE_URL` is not set, THEN THE CLIValidator SHALL display an error and return `False` to block execution early.

3. WHEN the token type is `proxy` and `ANTHROPIC_BASE_URL` is set, THE CLIValidator SHALL display the configured endpoint URL for confirmation.

4. THE ClientFactory SHALL also validate proxy configuration and raise `ValueError` if misconfigured, as a secondary safeguard.

### Requirement 5: API Key Billing Warning

**User Story:** As a developer using an API key, I want to be warned about billing implications, so that I can make informed decisions.

#### Acceptance Criteria

1. WHEN the token type is `api_key`, THE ClientFactory SHALL print a warning message containing "API Key mode" and "costs charged".

2. WHEN the token type is `api_key`, THE CLIValidator SHALL display a prominent warning box about direct billing.

### Requirement 6: Authentication Error Messages

**User Story:** As a developer without valid credentials, I want clear guidance on how to authenticate, so that I can quickly resolve the issue.

#### Acceptance Criteria

1. IF no authentication token is found, THEN THE AuthModule SHALL raise a ValueError listing all three supported authentication methods.

2. WHEN raising authentication error, THE AuthModule SHALL include OAuth Token setup instructions (`claude setup-token`) in the error message.

3. WHEN raising authentication error, THE AuthModule SHALL include API Key setup instructions (`ANTHROPIC_API_KEY` in .env) in the error message.

4. WHEN raising authentication error, THE AuthModule SHALL include Proxy setup instructions (`ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`) in the error message.

### Requirement 7: SDK Environment Variable Passthrough

**User Story:** As a developer, I want relevant environment variables passed to the SDK subprocess, so that custom configurations work correctly.

#### Acceptance Criteria

1. THE AuthModule SHALL include `ANTHROPIC_API_KEY` in the SDK environment variable passthrough list.

2. THE AuthModule SHALL pass through `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `NO_PROXY`, `DISABLE_TELEMETRY`, `DISABLE_COST_WARNINGS`, and `API_TIMEOUT_MS` to the SDK subprocess.

### Requirement 8: Backward Compatibility

**User Story:** As an existing OAuth user, I want my current setup to continue working, so that I don't need to change anything.

#### Acceptance Criteria

1. WHEN only `CLAUDE_CODE_OAUTH_TOKEN` is set, THE AuthModule SHALL behave identically to the previous implementation.

2. WHEN token is retrieved from macOS Keychain, THE AuthModule SHALL continue to validate the `sk-ant-oat01-` prefix (Note: Keychain validation is stricter than general OAuth detection for security reasons).

3. THE SimpleClientFactory SHALL use the same type-specific injection logic as the ClientFactory.
