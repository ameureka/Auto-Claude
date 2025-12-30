# Requirements Document: Full-Stack Multi-Auth Support (CLI + UI)

## Introduction

为 Auto-Claude 实现全栈多认证支持，包括 CLI 和 Electron UI，允许用户使用 OAuth Token、API Key 或 Proxy Token 进行认证，同时保持向后兼容性、数据迁移和安全性。

## Glossary

### Backend Components
- **AuthModule**: `apps/backend/core/auth.py` 认证模块，负责 Token 获取、类型识别和环境变量注入
- **ClientFactory**: `apps/backend/core/client.py` SDK 客户端工厂
- **SimpleClientFactory**: `apps/backend/core/simple_client.py` 简化客户端工厂
- **CLIValidator**: `apps/backend/cli/utils.py` CLI 环境验证模块

### Frontend Components
- **ProfileManager**: `apps/frontend/src/main/claude-profile-manager.ts` Profile 管理和环境注入
- **TerminalHandler**: `apps/frontend/src/main/terminal/claude-integration-handler.ts` 终端环境注入
- **RateLimitDetector**: `apps/frontend/src/main/rate-limit-detector.ts` 速率限制检测
- **AgentQueue**: `apps/frontend/src/main/agent/agent-queue.ts` Agent 队列和环境合并
- **EnvHandlers**: `apps/frontend/src/main/ipc-handlers/env-handlers.ts` .env 文件读写
- **AuthSection**: `apps/frontend/src/renderer/components/project-settings/ClaudeAuthSection.tsx` 认证 UI 组件

### Data Types
- **ProjectEnvConfig**: 项目环境配置接口，包含 `claudeAuthType`, `claudeAuthToken`, `claudeBaseUrl`
- **ClaudeProfile**: Profile 配置接口，包含 `tokenType`, `tokenValue`

### Token Types
- **OAuth_Token**: Claude Code CLI 颁发的订阅凭证，前缀 `sk-ant-oat01-` 或 `sk-ant-oat`
- **API_Key**: Anthropic Console 直接计费密钥，前缀 `sk-ant-api` 或 `sk-`（排除 oat 前缀）
- **Proxy_Token**: 企业代理/ProxyCast 凭证，前缀 `pc_` 或 `ccr-`
- **CLI**: Claude Code CLI，SDK 底层调用的命令行工具，实际处理认证

### Existing Fields (需保留兼容)
- **claudeAuthStatus**: 现有认证状态字段，需保留
- **claudeTokenIsGlobal**: 现有全局 token 标识，需保留
- **hasValidToken**: Profile 有效性检查函数，需扩展支持非 OAuth 类型

## Requirements

### Requirement 1: Backend Token Type Detection (继承自方案1)

**User Story:** As a developer, I want the system to automatically detect my token type, so that I don't need to manually configure the authentication mode.

#### Acceptance Criteria

1. WHEN the AuthModule receives a token starting with `sk-ant-oat01-` or `sk-ant-oat`, THE AuthModule SHALL classify the token as `oauth` type.

2. WHEN the AuthModule receives a token starting with `sk-ant-api`, THE AuthModule SHALL classify the token as `api_key` type. WHEN the AuthModule receives a token starting with `sk-` but NOT starting with `sk-ant-oat` and NOT starting with `sk-ant-api`, THE AuthModule SHALL also classify the token as `api_key` type (fallback for generic Anthropic keys).

**Note**: Classification order is critical: OAuth prefixes (`sk-ant-oat`) MUST be checked before API Key prefixes (`sk-ant-api`, then generic `sk-`).

3. WHEN the AuthModule receives a token starting with `pc_` or `ccr-`, THE AuthModule SHALL classify the token as `proxy` type.

4. WHEN the AuthModule receives a token not matching any known pattern, THE AuthModule SHALL classify the token as `unknown` type.

### Requirement 2: Backend Type-Specific Environment Injection (继承自方案1)

**User Story:** As a developer, I want all token types to work with the SDK/CLI, so that I can use any authentication method seamlessly.

#### Acceptance Criteria

1. WHEN the token type is `oauth`, THE AuthModule SHALL write the token to `CLAUDE_CODE_OAUTH_TOKEN` environment variable.

2. WHEN the token type is `api_key`, THE AuthModule SHALL write the token to `ANTHROPIC_API_KEY` environment variable.

3. WHEN the token type is `proxy`, THE AuthModule SHALL write the token to `ANTHROPIC_AUTH_TOKEN` environment variable.

4. WHEN applying authentication environment, THE AuthModule SHALL clear conflicting variables (`CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_AUTH_TOKEN`) before injection, BUT SHALL NOT clear `ANTHROPIC_API_KEY` to preserve Graphiti Anthropic provider compatibility.

**Note - CLI Authentication Behavior**: The Claude Code CLI reads authentication from type-specific environment variables:
- `CLAUDE_CODE_OAUTH_TOKEN` for OAuth subscription tokens
- `ANTHROPIC_API_KEY` for direct API access
- `ANTHROPIC_AUTH_TOKEN` for proxy/enterprise setups (with `ANTHROPIC_BASE_URL`)

**Note - Graphiti Compatibility**: `ANTHROPIC_API_KEY` is also used by Graphiti's Anthropic LLM provider. To avoid cross-feature conflicts, this variable is NOT cleared during auth injection. If user sets API Key mode, the same key will be used for both Claude CLI and Graphiti.

### Requirement 3: Frontend Data Structure Extension

**User Story:** As a UI user, I want to configure different authentication types in the settings, so that I can use my preferred authentication method.

#### Acceptance Criteria

1. THE ProjectEnvConfig interface SHALL include `claudeAuthType` field with type `'oauth' | 'api_key' | 'proxy'`.

2. THE ProjectEnvConfig interface SHALL include `claudeAuthToken` field for storing the token value.

3. THE ProjectEnvConfig interface SHALL include `claudeBaseUrl` field for Proxy mode configuration.

4. THE ClaudeProfile interface SHALL include `tokenType` field with type `'oauth' | 'api_key' | 'proxy'`.

5. THE ClaudeProfile interface SHALL include `tokenValue` field for storing the token value.

6. THE ClaudeProfile interface SHALL include `baseUrl` field for Proxy mode configuration, required when `tokenType` is `proxy`.

7. THE ProjectEnvConfig interface SHALL preserve existing fields `claudeAuthStatus` and `claudeTokenIsGlobal` for backward compatibility.

8. THE IPC types (`SourceEnvConfig`, etc.) SHALL be updated to include the new auth fields to prevent type断裂.

**Note - Existing Type Dependencies**: The following existing types/fields must be preserved:
- `ProjectEnvConfig.claudeAuthStatus` - used by UI for status display
- `ProjectEnvConfig.claudeTokenIsGlobal` - used for global token detection
- `SettingsState.globalClaudeToken` - global token storage
- `ISourceEnvConfig` in `ipc.ts` - IPC communication types

### Requirement 4: Frontend Profile Environment Injection

**User Story:** As a UI user, I want my profile authentication to work correctly with the SDK, so that I can run agents from the UI.

#### Acceptance Criteria

1. WHEN the ProfileManager generates environment variables for `oauth` type, THE ProfileManager SHALL write the token to `CLAUDE_CODE_OAUTH_TOKEN`.

2. WHEN the ProfileManager generates environment variables for `api_key` type, THE ProfileManager SHALL write the token to `ANTHROPIC_API_KEY`.

3. WHEN the ProfileManager generates environment variables for `proxy` type, THE ProfileManager SHALL write the token to `ANTHROPIC_AUTH_TOKEN` and set `ANTHROPIC_BASE_URL`.

4. IF the token value is empty or undefined AND no fallback is available, THEN THE ProfileManager SHALL return an empty environment object.

5. WHEN the token value is empty but `CLAUDE_CONFIG_DIR` is set (non-default profile), THE ProfileManager SHALL preserve the existing fallback behavior to maintain multi-profile compatibility.

**Note - Fallback Behavior**: The current ProfileManager falls back to `CLAUDE_CONFIG_DIR` for non-default profiles when no explicit token is set. This behavior MUST be preserved to avoid breaking existing multi-profile setups.

### Requirement 5: Frontend Terminal Environment Injection

**User Story:** As a UI user, I want terminal sessions to have correct authentication, so that I can use Claude CLI from the integrated terminal.

#### Acceptance Criteria

1. WHEN the TerminalHandler generates environment exports for `oauth` type, THE TerminalHandler SHALL export `CLAUDE_CODE_OAUTH_TOKEN`.

2. WHEN the TerminalHandler generates environment exports for `api_key` type, THE TerminalHandler SHALL export `ANTHROPIC_API_KEY`.

3. WHEN the TerminalHandler generates environment exports for `proxy` type, THE TerminalHandler SHALL export `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL`.

4. IF the token type is `proxy` and `baseUrl` is not provided, THEN THE TerminalHandler SHALL display an error and prevent terminal injection.

**Note - Implementation Context**: The current terminal injection uses `invokeClaude` with inline temporary file writing. The new implementation should either:
- Extend the existing `invokeClaude` to support type-specific exports, OR
- Create a new `generateEnvExports` helper that `invokeClaude` calls internally
The existing history protection logic in `invokeClaude` MUST be preserved.

### Requirement 6: Frontend Rate Limit Detection Adaptation

**User Story:** As a UI user using API Key or Proxy, I don't want to see OAuth expiration warnings, so that I'm not confused by irrelevant messages.

#### Acceptance Criteria

1. WHEN the RateLimitDetector needs environment variables, THE RateLimitDetector SHALL delegate to ProfileManager.getActiveProfileEnv() to ensure consistent type-specific injection.

2. WHEN determining whether to show OAuth expiration warning, THE RateLimitDetector SHALL only show the warning if token type is `oauth`.

3. WHEN the token type is `api_key` or `proxy`, THE RateLimitDetector SHALL suppress OAuth expiration warnings.

4. THE RateLimitDetector SHALL implement a new `shouldShowOAuthExpiredWarning(tokenType: AuthType): boolean` method to centralize warning logic.

**Note - Current Implementation Gap**: The current RateLimitDetector has `getProfileEnv` but lacks OAuth expiration warning logic. This requirement adds:
- Token type awareness to the detector
- A new method for warning suppression based on token type
- UI integration point for displaying warnings (to be defined in UI component requirements)

### Requirement 7: Frontend Agent Queue Environment Merge

**User Story:** As a UI user, I want agent execution to use the correct authentication from my profile, so that agents run with my credentials.

#### Acceptance Criteria

1. WHEN the AgentQueue builds agent environment, THE AgentQueue SHALL merge environments in the following precedence order (highest to lowest):
   - Profile environment (from ProfileManager)
   - Project .env settings (from autoBuildSource/.env)
   - Project settings (from project configuration)
   - Process environment (process.env)

2. WHEN logging environment variables for debugging, THE AgentQueue SHALL mask sensitive token values showing only the first 6 characters.

3. THE AgentQueue SHALL mask `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, and `ANTHROPIC_AUTH_TOKEN` in debug logs.

**Note - Actual Merge Order**: The current implementation in `agent-queue.ts` and `agent-process.ts` has a complex merge order involving `process.env`, `autoBuildSource/.env`, and project settings. This requirement documents the intended precedence to ensure profile auth takes priority.

### Requirement 8: Frontend .env File Read/Write and CLI Integration

**User Story:** As a UI user, I want my authentication settings saved to .env file, so that CLI can also use them.

#### Acceptance Criteria

1. WHEN writing .env file with `oauth` auth type, THE EnvHandlers SHALL write `CLAUDE_CODE_OAUTH_TOKEN` variable.

2. WHEN writing .env file with `api_key` auth type, THE EnvHandlers SHALL write `ANTHROPIC_API_KEY` variable.

3. WHEN writing .env file with `proxy` auth type, THE EnvHandlers SHALL write `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` variables.

4. WHEN reading .env file, THE EnvHandlers SHALL detect auth type based on token prefix (using `get_token_type` logic), NOT based on which variable name is present.

5. THE CLI/runner (`spec_runner.py`, `run.py`) SHALL be modified to load project `.auto-claude/.env` in addition to `apps/backend/.env`, with project .env taking precedence.

**Note - Storage vs Runtime Format**:
- **Storage Format (.env file)**: Type-specific variables (`CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`) for human readability and CLI compatibility.
- **Runtime Format (environment injection)**: Type-specific variables passed to SDK/CLI.
- **CLI Integration**: Currently CLI only loads `apps/backend/.env`. To fulfill "UI writes .env for CLI use", the CLI must also read project-level `.auto-claude/.env`.

**Note - .env File Locations**:
- Global CLI config: `apps/backend/.env`
- Project-specific: `{project_root}/.auto-claude/.env`
- Priority: Project .env > Global .env

### Requirement 9: Frontend Authentication UI Component

**User Story:** As a UI user, I want a clear interface to select and configure authentication, so that I can easily set up my credentials.

#### Acceptance Criteria

1. THE AuthSection component SHALL display a selector with three options: OAuth (Recommended), API Key (Direct Billing), Proxy/Enterprise.

2. WHEN `api_key` is selected, THE AuthSection component SHALL display a warning about direct billing costs.

3. WHEN `oauth` is selected, THE AuthSection component SHALL display a hint about running `claude setup-token`.

4. WHEN `proxy` is selected, THE AuthSection component SHALL display an additional Base URL input field marked as required.

5. THE AuthSection component SHALL use password input type for token fields to hide sensitive values.

### Requirement 10: Frontend Proxy Validation

**User Story:** As a UI user configuring Proxy mode, I want validation to prevent misconfiguration, so that I don't accidentally connect to the wrong endpoint.

#### Acceptance Criteria

1. WHEN the user selects `proxy` auth type, THE AuthSection component SHALL require Base URL input.

2. IF the user attempts to save Proxy configuration without Base URL, THEN THE AuthSection component SHALL display an error and prevent saving.

3. WHEN Proxy configuration is complete, THE UI SHALL display the configured Base URL for confirmation.

### Requirement 11: Data Migration and Backward Compatibility

**User Story:** As an existing OAuth user, I want my current setup to continue working without any changes.

#### Acceptance Criteria

1. WHEN reading ProjectEnvConfig with `claudeOAuthToken` but without `claudeAuthType`, THE system SHALL treat it as OAuth type for backward compatibility.

2. WHEN reading ClaudeProfile with `oauthToken` but without `tokenType`, THE system SHALL migrate it to `tokenType: 'oauth'` and `tokenValue: oauthToken`.

3. WHEN new fields are present, THE system SHALL prioritize new fields (`claudeAuthType`, `tokenType`) over legacy fields.

4. THE SimpleClientFactory SHALL use the same type-specific injection logic as the ClientFactory.

5. THE Profile storage version SHALL be upgraded to support new fields while preserving backward compatibility with existing profiles.

6. THE `hasValidToken` function in `profile-utils.ts` SHALL be extended to validate non-OAuth token types (API Key and Proxy).

**Note - Storage Version Migration**: The current profile storage (`profile-storage.ts`) needs version upgrade logic to:
- Detect old format profiles (oauthToken only)
- Migrate to new format (tokenType + tokenValue)
- Preserve existing data during migration

**Note - Token Validity**: Current `hasValidToken` only checks OAuth token format. For multi-auth support:
- OAuth: Check `sk-ant-oat` prefix
- API Key: Check `sk-ant-api` or `sk-` prefix (excluding oat)
- Proxy: Check `pc_` or `ccr-` prefix + baseUrl presence

### Requirement 12: Token Security

**User Story:** As a user, I want my tokens stored securely, so that they are not exposed.

#### Acceptance Criteria

1. THE ProfileManager SHALL encrypt token values using the existing `encryptToken` function before storage.

2. WHEN displaying tokens in UI, THE system SHALL mask the token showing only partial characters.

3. WHEN logging tokens for debugging, THE system SHALL show only the first 6 characters followed by ellipsis.

### Requirement 13: CLI Documentation and Examples Update

**User Story:** As a CLI user, I want accurate documentation about supported authentication methods, so that I'm not confused by outdated information.

#### Acceptance Criteria

1. THE CLI help text in `cli/main.py` SHALL be updated to list all three supported authentication methods (OAuth, API Key, Proxy).

2. THE CLI validation messages in `cli/utils.py` SHALL be updated to remove "API Key not supported" statements and instead provide guidance for all auth types.

3. THE `.env.example` file SHALL be updated to include examples for all three authentication methods with clear comments.

4. WHEN displaying authentication errors, THE CLI SHALL provide setup instructions for all three methods.

**Note - Current State**: The CLI currently states "API Key is not supported" in help text and examples. This conflicts with the multi-auth support goal and must be updated to reflect the new capabilities.

**Files to Update**:
- `apps/backend/cli/main.py:75` - Help text
- `apps/backend/cli/utils.py:120` - Validation messages
- `apps/backend/.env.example:7` - Example configuration

