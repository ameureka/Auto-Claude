# Feature Design: Full-Stack Multi-Auth Support (CLI + UI)

## Overview

本设计实现 Auto-Claude 的全栈多认证支持，包括后端 CLI 和前端 Electron UI，允许用户使用 OAuth Token、API Key 或 Proxy Token 进行认证。

### 核心设计决策

1. **类型特定注入**: 不同 Token 类型写入对应的环境变量，因为 CLI 从类型特定变量读取认证
2. **前后端一致性**: 前端环境注入逻辑与后端保持一致
3. **向后兼容**: 现有 OAuth 用户和数据无需任何更改
4. **渐进式迁移**: 支持旧字段到新字段的自动迁移
5. **Graphiti 兼容**: 不清理 `ANTHROPIC_API_KEY` 以保持 Graphiti Anthropic provider 兼容

### 与现有系统的关系

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   OAuth     │  │   API Key   │  │    Proxy    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   UI Storage    │  │  Profile Mgr    │  │  Terminal Hdlr  │
│   (.env file)   │  │  (env inject)   │  │  (env export)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
              ┌─────────────────────────────────┐
              │      Type-Specific Variables    │
              │  OAuth    → CLAUDE_CODE_OAUTH   │
              │  API Key  → ANTHROPIC_API_KEY   │
              │  Proxy    → ANTHROPIC_AUTH_TOKEN│
              └─────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Backend Auth   │  │  ClientFactory  │  │  SimpleClient   │
│   (auth.py)     │  │  (client.py)    │  │  (simple.py)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
              ┌─────────────────────────────────┐
              │   claude-agent-sdk → CLI        │
              │   (passes env to CLI subprocess)│
              └─────────────────────────────────┘
```

## Architecture

```mermaid
graph TD
    subgraph "Frontend - Renderer Process"
        UI_AUTH[AuthSection Component]
        UI_SETTINGS[IntegrationSettings]
        UI_ENV_MODAL[EnvConfigModal]
    end

    subgraph "Frontend - Main Process"
        PROFILE_MGR[ProfileManager]
        TERMINAL_HDL[TerminalHandler]
        RATE_LIMIT[RateLimitDetector]
        AGENT_QUEUE[AgentQueue]
        ENV_HANDLERS[EnvHandlers]
    end

    subgraph "Frontend - Shared Types"
        PROJECT_ENV[ProjectEnvConfig]
        CLAUDE_PROFILE[ClaudeProfile]
    end

    subgraph "Backend"
        AUTH_MODULE[AuthModule]
        CLIENT_FACTORY[ClientFactory]
        SIMPLE_CLIENT[SimpleClientFactory]
        CLI_VALIDATOR[CLIValidator]
    end

    subgraph "SDK"
        SDK[claude-agent-sdk]
    end

    UI_AUTH --> PROJECT_ENV
    UI_AUTH --> CLAUDE_PROFILE
    UI_SETTINGS --> PROFILE_MGR
    UI_ENV_MODAL --> ENV_HANDLERS

    PROFILE_MGR --> |"getActiveProfileEnv()"| AGENT_QUEUE
    TERMINAL_HDL --> |"generateEnvExports()"| SDK
    ENV_HANDLERS --> |"writeEnvFile()"| AUTH_MODULE

    AGENT_QUEUE --> |"buildAgentEnv()"| CLIENT_FACTORY
    RATE_LIMIT --> |"getProfileEnv()"| SDK

    AUTH_MODULE --> |"apply_auth_env()"| SDK
    CLIENT_FACTORY --> AUTH_MODULE
    SIMPLE_CLIENT --> AUTH_MODULE
    CLI_VALIDATOR --> AUTH_MODULE
```

### Call Flow

```
UI 认证配置流程:
1. 用户在 AuthSection 选择认证类型并输入 Token
2. UI 调用 EnvHandlers.writeEnvFile() 保存到 .env (类型特定变量)
3. UI 调用 ProfileManager.setProfileToken() 保存到 Profile

Agent 执行流程:
1. AgentQueue 调用 ProfileManager.getActiveProfileEnv() 获取环境
2. getActiveProfileEnv() 根据 tokenType 写入对应变量:
   - oauth → CLAUDE_CODE_OAUTH_TOKEN
   - api_key → ANTHROPIC_API_KEY
   - proxy → ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL
3. AgentQueue 合并环境 (优先级: profile > project .env > project settings > process.env)
4. ClientFactory 调用 apply_auth_env() 进行类型特定注入
5. SDK 将环境变量传递给 CLI，CLI 从类型特定变量读取认证

终端注入流程:
1. TerminalHandler 调用 invokeClaude() (现有实现使用临时文件)
2. invokeClaude() 内部根据 tokenType 导出对应变量
3. 终端 session 获得正确的认证环境
4. 保留现有的 history protection 逻辑

CLI 读取项目 .env 流程:
1. CLI/runner 启动时检查项目 .auto-claude/.env
2. 如果存在，加载并覆盖 apps/backend/.env 中的同名变量
3. 优先级: 项目 .env > 全局 .env
```

## Components and Interfaces

### Frontend - Shared Types

```typescript
// apps/frontend/src/shared/types/project.ts
interface ProjectEnvConfig {
  // Legacy field (backward compatibility)
  claudeOAuthToken?: string;

  // Existing fields (must preserve)
  claudeAuthStatus?: 'authenticated' | 'expired' | 'none';
  claudeTokenIsGlobal?: boolean;

  // New fields
  claudeAuthType?: 'oauth' | 'api_key' | 'proxy';
  claudeAuthToken?: string;
  claudeBaseUrl?: string;  // Required for proxy mode
}

// apps/frontend/src/shared/types/agent.ts
interface ClaudeProfile {
  // Legacy field (backward compatibility)
  oauthToken?: string;

  // New fields
  tokenType?: 'oauth' | 'api_key' | 'proxy';
  tokenValue?: string;
  baseUrl?: string;  // Required for proxy mode
}

// apps/frontend/src/shared/types/ipc.ts (must also update)
interface ISourceEnvConfig {
  // ... existing fields ...
  claudeAuthType?: 'oauth' | 'api_key' | 'proxy';
  claudeAuthToken?: string;
  claudeBaseUrl?: string;
}

type AuthType = 'oauth' | 'api_key' | 'proxy';
```

### Frontend - ProfileManager

```typescript
// apps/frontend/src/main/claude-profile-manager.ts

interface ProfileManager {
  /**
   * Get environment variables for the active profile.
   * Writes to type-specific variables based on tokenType.
   */
  getActiveProfileEnv(): Record<string, string>;

  /**
   * Set token for a profile with type information.
   */
  setProfileToken(profileId: string, tokenType: AuthType, tokenValue: string, baseUrl?: string): void;

  /**
   * Get active profile with migration support.
   * Falls back to CLAUDE_CONFIG_DIR for non-default profiles when no explicit token.
   */
  getActiveProfile(): { tokenType: AuthType; tokenValue: string; baseUrl?: string } | null;
}

// Implementation notes:
// - getActiveProfileEnv() must preserve existing CLAUDE_CONFIG_DIR fallback logic
// - For non-default profiles without explicit token, return CLAUDE_CONFIG_DIR env
// - This maintains compatibility with existing multi-profile setups
```

### Frontend - TerminalHandler

```typescript
// apps/frontend/src/main/terminal/claude-integration-handler.ts

// Note: Current implementation uses invokeClaude() with inline temporary file writing.
// The new implementation should extend invokeClaude() rather than create separate functions.

interface TerminalHandler {
  /**
   * Invoke Claude CLI with proper environment injection.
   * EXISTING: Uses temporary file for env injection with history protection.
   * MODIFIED: Support type-specific variable exports.
   */
  invokeClaude(options: {
    tokenType: AuthType;
    token: string;
    baseUrl?: string;
    // ... existing options
  }): Promise<void>;

  /**
   * Validate proxy configuration before injection.
   */
  validateProxyConfig(tokenType: AuthType, baseUrl?: string): { valid: boolean; error?: string };
}

// Implementation notes:
// - Extend existing invokeClaude() to accept tokenType parameter
// - Generate type-specific exports inside the existing temp file logic
// - Preserve existing history protection (HISTFILE=/dev/null etc.)
// - Do NOT create separate generateEnvExports() - keep logic inline
```

### Frontend - EnvHandlers

```typescript
// apps/frontend/src/main/ipc-handlers/env-handlers.ts

interface EnvHandlers {
  /**
   * Write authentication config to .env file.
   * Writes type-specific variables for CLI to read.
   */
  writeEnvFile(config: ProjectEnvConfig): void;

  /**
   * Read authentication config from .env file.
   * Detects auth type based on TOKEN PREFIX, not variable name.
   */
  readEnvFile(): ProjectEnvConfig;

  /**
   * Detect auth type from token value using prefix matching.
   * IMPORTANT: Use token prefix, NOT variable name presence.
   */
  detectAuthType(tokenValue: string): AuthType;
}

// Implementation notes:
// - detectAuthType() must use token prefix logic consistent with backend get_token_type()
// - Do NOT detect type based on which env var contains the token
// - This ensures frontend/backend classification consistency
```

### Frontend - AgentQueue

```typescript
// apps/frontend/src/main/agent/agent-queue.ts

interface AgentQueue {
  /**
   * Build environment for agent execution.
   * Merge order (highest to lowest priority):
   * 1. Profile environment (from ProfileManager)
   * 2. Project .env (from autoBuildSource/.env)
   * 3. Project settings
   * 4. Process environment (process.env)
   */
  buildAgentEnv(): Record<string, string>;

  /**
   * Log environment safely with masked tokens.
   */
  logEnvSafe(env: Record<string, string>): void;
}

// Implementation notes:
// - Current implementation in agent-queue.ts and agent-process.ts has complex merge logic
// - Ensure profile auth variables take precedence over all other sources
// - Mask CLAUDE_CODE_OAUTH_TOKEN, ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN in logs
```

### Backend - AuthModule (继承自方案1)

```python
# apps/backend/core/auth.py

def get_token_type(token: str | None) -> str:
    """Detect token type based on prefix."""
    ...

def apply_auth_env(token: str) -> str:
    """
    Type-specific environment injection.
    - oauth → CLAUDE_CODE_OAUTH_TOKEN
    - api_key → ANTHROPIC_API_KEY
    - proxy → ANTHROPIC_AUTH_TOKEN

    Note: Does NOT clear ANTHROPIC_API_KEY to preserve Graphiti compatibility.
    """
    ...

def validate_proxy_config() -> tuple[bool, str]:
    """Validate proxy configuration."""
    ...
```

### Backend - CLI Runner (新增)

```python
# apps/backend/runners/spec_runner.py, run.py

def load_project_env(project_dir: Path) -> None:
    """
    Load project-specific .env file.
    Priority: project .auto-claude/.env > apps/backend/.env
    """
    project_env = project_dir / '.auto-claude' / '.env'
    if project_env.exists():
        load_dotenv(project_env, override=True)
```

## Data Models

### Token Type Mapping

| Type | Prefixes | Target Variable | Additional |
|------|----------|-----------------|------------|
| oauth | `sk-ant-oat01-`, `sk-ant-oat` | `CLAUDE_CODE_OAUTH_TOKEN` | - |
| api_key | `sk-ant-api`, `sk-` (not oat) | `ANTHROPIC_API_KEY` | - |
| proxy | `pc_`, `ccr-` | `ANTHROPIC_AUTH_TOKEN` | `ANTHROPIC_BASE_URL` (required) |

**Note**: Classification order is critical - OAuth prefixes MUST be checked before generic `sk-` prefix.

### Data Migration Rules

| Scenario | Legacy Fields | Migration Action |
|----------|---------------|------------------|
| ProjectEnvConfig | `claudeOAuthToken` exists, `claudeAuthType` missing | Set `claudeAuthType: 'oauth'`, `claudeAuthToken: claudeOAuthToken` |
| ClaudeProfile | `oauthToken` exists, `tokenType` missing | Set `tokenType: 'oauth'`, `tokenValue: oauthToken` |
| Both exist | New and legacy fields present | Prioritize new fields |
| Profile Storage | Old version without tokenType | Upgrade storage version, migrate data |

### Profile Storage Version

```typescript
// apps/frontend/src/main/claude-profile/profile-storage.ts

interface ProfileStorageV1 {
  oauthToken?: string;
  // ... other fields
}

interface ProfileStorageV2 {
  tokenType?: AuthType;
  tokenValue?: string;
  baseUrl?: string;
  // ... other fields
}

// Migration: V1 → V2
function migrateProfile(v1: ProfileStorageV1): ProfileStorageV2 {
  return {
    tokenType: 'oauth',
    tokenValue: v1.oauthToken,
    // ... preserve other fields
  };
}
```

### Token Validity Check

```typescript
// apps/frontend/src/main/claude-profile/profile-utils.ts

function hasValidToken(profile: ClaudeProfile): boolean {
  const { tokenType, tokenValue, baseUrl } = profile;
  if (!tokenValue) return false;

  switch (tokenType) {
    case 'oauth':
      return tokenValue.startsWith('sk-ant-oat');
    case 'api_key':
      return tokenValue.startsWith('sk-ant-api') ||
             (tokenValue.startsWith('sk-') && !tokenValue.startsWith('sk-ant-oat'));
    case 'proxy':
      return (tokenValue.startsWith('pc_') || tokenValue.startsWith('ccr-')) && !!baseUrl;
    default:
      return false;
  }
}
```

### Authentication Priority (UI)

```
Merge order (highest to lowest priority):
1. Profile token (from ProfileManager.getActiveProfileEnv())
2. Project .env (from autoBuildSource/.env via agent-process.ts)
3. Project settings (from project configuration)
4. Process environment (process.env)
```

## Correctness Properties

### Prework: Testability Analysis

```
Frontend Properties:

4.1 Profile env injection - type-specific
  Thoughts: Each token type must write to its corresponding variable
  Testable: yes - property

4.2 Profile env injection - fallback behavior
  Thoughts: Must preserve CLAUDE_CONFIG_DIR fallback for multi-profile
  Testable: yes - property

5.1 Terminal export - type-specific
  Thoughts: Each type exports its corresponding variable
  Testable: yes - property

5.2 Terminal export - proxy validation
  Thoughts: Must block if base URL missing
  Testable: yes - property

6.1 Rate limit - OAuth warning suppression
  Thoughts: Only show for OAuth type
  Testable: yes - property

7.1 Agent queue - env merge precedence
  Thoughts: Profile must override all other sources
  Testable: yes - property

7.2 Agent queue - token masking
  Thoughts: Sensitive values must be masked
  Testable: yes - property

8.1 Env file - type detection by prefix
  Thoughts: Detect type from token prefix, not variable name
  Testable: yes - property

11.1 Data migration - legacy field handling
  Thoughts: Backward compatibility
  Testable: yes - property

11.2 Token validity - multi-type support
  Thoughts: hasValidToken must work for all types
  Testable: yes - property

12.1 Token security - masking
  Thoughts: Only show first 6 chars
  Testable: yes - property
```

### Property Reflection

- Properties 4.1-4.2 are distinct: type-specific injection vs fallback behavior
- Properties 5.1-5.2 are distinct: export generation vs validation
- Properties 7.1-7.2 are distinct: merge logic vs security
- Properties 11.1-11.2 are distinct: migration vs validity check
- Property 8.1 uses token prefix, NOT variable name

### Correctness Properties

**Property 1-6: Backend Properties (继承自方案1)**

参见方案1 design.md 的 Property 1-6（已修正为类型特定注入）。

---

**Property 7: Frontend Profile Type-Specific Injection**

*For any* token with type `oauth`, after calling `getActiveProfileEnv()`, the returned environment object SHALL contain `CLAUDE_CODE_OAUTH_TOKEN` equal to the token value.

*For any* token with type `api_key`, after calling `getActiveProfileEnv()`, the returned environment object SHALL contain `ANTHROPIC_API_KEY` equal to the token value.

*For any* token with type `proxy` and valid `baseUrl`, after calling `getActiveProfileEnv()`, the returned environment object SHALL contain `ANTHROPIC_AUTH_TOKEN` equal to the token value AND `ANTHROPIC_BASE_URL` equal to the baseUrl.

**Validates: Requirements 4.1, 4.2, 4.3**

---

**Property 8: Frontend Profile Fallback Behavior**

*For any* non-default profile without explicit token but with `CLAUDE_CONFIG_DIR` set, `getActiveProfileEnv()` SHALL return an environment containing `CLAUDE_CONFIG_DIR` to preserve multi-profile compatibility.

**Validates: Requirements 4.5**

---

**Property 9: Frontend Terminal Type-Specific Export**

*For any* token with type `oauth`, the terminal injection SHALL export `CLAUDE_CODE_OAUTH_TOKEN`.

*For any* token with type `api_key`, the terminal injection SHALL export `ANTHROPIC_API_KEY`.

*For any* token with type `proxy`, the terminal injection SHALL export `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL`.

**Validates: Requirements 5.1, 5.2, 5.3**

---

**Property 10: Frontend Terminal Proxy Validation**

*For any* token with type `proxy`, if `baseUrl` is empty or undefined, `validateProxyConfig()` SHALL return `{ valid: false, error: "..." }`.

**Validates: Requirements 5.4, 10.2**

---

**Property 11: Frontend OAuth Warning Suppression**

*For any* token with type `api_key` or `proxy`, `shouldShowOAuthExpiredWarning()` SHALL return `false`.

**Validates: Requirements 6.2, 6.3**

---

**Property 12: Frontend Agent Env Merge Precedence**

*For any* profile environment and project environment with overlapping keys, `buildAgentEnv()` SHALL return values from profile environment for overlapping keys.

**Validates: Requirements 7.1**

---

**Property 13: Frontend Token Masking**

*For any* token value with length >= 6, `logEnvSafe()` SHALL output only the first 6 characters followed by `...` for sensitive keys.

*For any* token value with length < 6, `logEnvSafe()` SHALL output `[short]` to indicate the token is too short (potential misconfiguration) without exposing the actual value.

**Validates: Requirements 7.2, 7.3, 12.3**

---

**Property 14: Frontend Env File Type Detection**

*For any* .env file content with a token value, the `detectAuthType()` function SHALL determine type based on the **token prefix** (using `get_token_type` logic):
- IF token starts with `sk-ant-oat01-` or `sk-ant-oat`, detected type SHALL be `oauth`
- IF token starts with `sk-ant-api`, OR starts with `sk-` but NOT `sk-ant-oat`, detected type SHALL be `api_key`
- IF token starts with `pc_` or `ccr-`, detected type SHALL be `proxy`
- OTHERWISE, detected type SHALL be `unknown`

**Note**: Type detection is based on token prefix, NOT on which environment variable name contains the token. This ensures consistency with backend classification.

**Validates: Requirements 8.4**

---

**Property 15: Data Migration Correctness**

*For any* ProjectEnvConfig with `claudeOAuthToken` but without `claudeAuthType`, the system SHALL treat it as `oauth` type.

*For any* ClaudeProfile with `oauthToken` but without `tokenType`, the system SHALL migrate to `tokenType: 'oauth'`.

**Validates: Requirements 11.1, 11.2, 11.3**

## Error Handling

### Error Types

| Component | Error | Condition | Message |
|-----------|-------|-----------|---------|
| Backend | `ValueError` | No token found | Multi-line guidance |
| Backend | `ValueError` | Proxy without base URL | "Proxy token detected but ANTHROPIC_BASE_URL is not set" |
| Frontend | Validation Error | Proxy without base URL | "Base URL is required for Proxy mode" |
| Frontend | UI Warning | API Key selected | "⚠️ API Key mode: costs charged directly" |

### Error Recovery

- Token not found: Display guidance in UI and CLI
- Proxy misconfiguration: Block save/injection until Base URL provided
- Migration failure: Fall back to legacy field values

## Testing Strategy

### Unit Tests (Frontend - TypeScript)

1. `test_getActiveProfileEnv_oauth`: Test OAuth profile env generation
2. `test_getActiveProfileEnv_api_key`: Test API Key profile env generation
3. `test_getActiveProfileEnv_proxy`: Test Proxy profile env generation
4. `test_generateEnvExports_all_types`: Test terminal export generation
5. `test_validateProxyConfig_missing_url`: Test proxy validation failure
6. `test_shouldShowOAuthExpiredWarning`: Test warning suppression
7. `test_buildAgentEnv_merge_precedence`: Test env merge
8. `test_logEnvSafe_masking`: Test token masking
9. `test_detectAuthType`: Test type detection from env
10. `test_migration_legacy_fields`: Test backward compatibility

### Property Tests (Frontend - Vitest)

```typescript
// Note: Repository uses Vitest, not Jest. fast-check can be integrated with Vitest.
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';

// Property 7: Frontend Profile Type-Specific Injection
describe('Profile Type-Specific Injection', () => {
  it.prop([fc.string({ minLength: 1 })])('oauth token writes to CLAUDE_CODE_OAUTH_TOKEN', (token) => {
    const env = getActiveProfileEnv({ tokenType: 'oauth', tokenValue: token });
    expect(env['CLAUDE_CODE_OAUTH_TOKEN']).toBe(token);
    expect(env['ANTHROPIC_API_KEY']).toBeUndefined();
  });

  it.prop([fc.string({ minLength: 1 })])('api_key token writes to ANTHROPIC_API_KEY', (token) => {
    const env = getActiveProfileEnv({ tokenType: 'api_key', tokenValue: token });
    expect(env['ANTHROPIC_API_KEY']).toBe(token);
    expect(env['CLAUDE_CODE_OAUTH_TOKEN']).toBeUndefined();
  });

  it.prop([fc.string({ minLength: 1 }), fc.webUrl()])('proxy token writes to ANTHROPIC_AUTH_TOKEN', (token, baseUrl) => {
    const env = getActiveProfileEnv({ tokenType: 'proxy', tokenValue: token, baseUrl });
    expect(env['ANTHROPIC_AUTH_TOKEN']).toBe(token);
    expect(env['ANTHROPIC_BASE_URL']).toBe(baseUrl);
  });
});

// Property 13: Token Masking
describe('Token Masking', () => {
  it.prop([fc.string({ minLength: 6 })])('masks tokens to first 6 chars', (token) => {
    const env = { 'CLAUDE_CODE_OAUTH_TOKEN': token };
    const logged = logEnvSafe(env);
    expect(logged['CLAUDE_CODE_OAUTH_TOKEN']).toBe(token.substring(0, 6) + '...');
  });

  it.prop([fc.string({ minLength: 1, maxLength: 5 })])('short tokens show [short]', (token) => {
    const env = { 'CLAUDE_CODE_OAUTH_TOKEN': token };
    const logged = logEnvSafe(env);
    expect(logged['CLAUDE_CODE_OAUTH_TOKEN']).toBe('[short]');
  });
});

// Property 14: Type Detection by Prefix
describe('Type Detection by Prefix', () => {
  it('detects oauth from sk-ant-oat prefix', () => {
    expect(detectAuthType('sk-ant-oat01-abc123')).toBe('oauth');
    expect(detectAuthType('sk-ant-oat-xyz')).toBe('oauth');
  });

  it('detects api_key from sk-ant-api prefix', () => {
    expect(detectAuthType('sk-ant-api03-abc123')).toBe('api_key');
  });

  it('detects api_key from generic sk- prefix (not oat)', () => {
    expect(detectAuthType('sk-abc123')).toBe('api_key');
  });

  it('detects proxy from pc_ or ccr- prefix', () => {
    expect(detectAuthType('pc_abc123')).toBe('proxy');
    expect(detectAuthType('ccr-xyz789')).toBe('proxy');
  });
});
```

**Note**: If fast-check is not desired, these can be converted to standard Vitest tests with explicit test cases.

### Integration Tests

1. **E2E OAuth Flow**: UI → Profile → Agent → SDK
2. **E2E API Key Flow**: UI → Profile → Agent → SDK + Warning
3. **E2E Proxy Flow**: UI → Profile → Agent → SDK + Base URL
4. **Terminal Integration**: UI → Terminal → CLI
5. **Migration Test**: Legacy data → New format
6. **CLI Project .env**: CLI reads project .auto-claude/.env

### Test Framework

- **Backend**: pytest + Hypothesis
- **Frontend Unit**: Vitest (repository standard)
- **Frontend Property**: Vitest + fast-check (optional, can use explicit test cases)
- **Frontend E2E**: Playwright (via Electron MCP)
- **Iterations**: 100+ per property test

### Test Dependencies

```json
// apps/frontend/package.json - devDependencies
{
  "fast-check": "^3.0.0"  // Optional, for property-based testing
}
```

```txt
# tests/requirements-test.txt
hypothesis>=6.0.0
```
