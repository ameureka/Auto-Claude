# Implementation Plan: Full-Stack Multi-Auth Support (CLI + UI)

## Overview

本任务清单将方案2（全功能UI改造）的设计转化为可执行的编码任务，包括后端和前端的完整实现。

### 依赖项

- **Backend**: Hypothesis (属性测试) - 添加到 `tests/requirements-test.txt`
- **Frontend**: fast-check (可选，属性测试) - 添加到 `apps/frontend/package.json`

### 关键设计原则

1. **类型特定注入**: 不同 Token 类型写入对应的环境变量（CLI 从类型特定变量读取）
2. **Graphiti 兼容**: 不清理 `ANTHROPIC_API_KEY` 以保持 Graphiti Anthropic provider 兼容
3. **Profile 回退**: 保留 `CLAUDE_CONFIG_DIR` 回退逻辑以兼容现有多 profile
4. **类型检测**: 基于 token 前缀检测类型，而非变量名

### 现有代码状态

**已实现** (在 `apps/backend/core/auth.py`):
- `AUTH_TOKEN_ENV_VARS` 列表
- `get_token_type()` 函数
- `apply_auth_env()` 函数 (需修正为类型特定注入)
- `validate_proxy_config()` 函数

**需修改**:
- `apply_auth_env()` 从统一入口改为类型特定注入
- 不清理 `ANTHROPIC_API_KEY` (Graphiti 兼容)
- CLI 帮助文案和 .env.example

---

## Phase 1: 后端修正（基于方案1修正版）

**Note**: 后端代码已部分实现，但需要修正为类型特定注入。

- [x] 1.1 AUTH_TOKEN_ENV_VARS 列表 (已存在)
- [x] 1.2 SDK_ENV_VARS 列表 (已存在)
- [x] 1.3 get_token_type 函数 (已存在)

- [ ] 1.4 **修正** apply_auth_env 函数
  - 修改为类型特定注入:
    - oauth → `CLAUDE_CODE_OAUTH_TOKEN`
    - api_key → `ANTHROPIC_API_KEY`
    - proxy → `ANTHROPIC_AUTH_TOKEN`
  - **不清理** `ANTHROPIC_API_KEY` (Graphiti 兼容)
  - 清理 `CLAUDE_CODE_OAUTH_TOKEN` 和 `ANTHROPIC_AUTH_TOKEN`
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 1.4.1 编写属性测试: 类型特定注入
  - **Property 2: Type-Specific Environment Injection**
  - 验证 OAuth → CLAUDE_CODE_OAUTH_TOKEN
  - 验证 API Key → ANTHROPIC_API_KEY
  - 验证 Proxy → ANTHROPIC_AUTH_TOKEN
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [x] 1.5 validate_proxy_config 函数 (已存在)

- [ ] 1.6 更新 CLI 帮助文案和示例
  - 更新 `apps/backend/cli/main.py` 帮助文本，移除 "API Key 不支持"
  - 更新 `apps/backend/cli/utils.py` 验证消息
  - 更新 `apps/backend/.env.example` 添加三种认证示例
  - _Requirements: 13.1, 13.2, 13.3_

- [ ] 1.7 实现 CLI 读取项目 .env
  - 修改 `apps/backend/runners/spec_runner.py`
  - 修改 `apps/backend/run.py`
  - 加载 `{project}/.auto-claude/.env`，优先级高于 `apps/backend/.env`
  - _Requirements: 8.5_

- [ ] 2. Checkpoint - 后端完成
  - Ensure all backend tests pass
  - Verify CLI works with all three auth types
  - Verify CLI reads project .env

---

## Phase 2: 前端数据结构

**Note**: 必须保留现有字段 `claudeAuthStatus`, `claudeTokenIsGlobal` 以保持向后兼容。

- [ ] 3. 扩展 Shared Types
- [ ] 3.1 扩展 ProjectEnvConfig 接口
  - 在 `apps/frontend/src/shared/types/project.ts` 中添加新字段
  - 添加 `claudeAuthType?: 'oauth' | 'api_key' | 'proxy'`
  - 添加 `claudeAuthToken?: string`
  - 添加 `claudeBaseUrl?: string`
  - **保留** `claudeOAuthToken` 用于向后兼容
  - **保留** `claudeAuthStatus` 和 `claudeTokenIsGlobal` (现有字段)
  - _Requirements: 3.1, 3.2, 3.3, 3.7_

- [ ] 3.2 扩展 ClaudeProfile 接口
  - 在 `apps/frontend/src/shared/types/agent.ts` 中添加新字段
  - 添加 `tokenType?: 'oauth' | 'api_key' | 'proxy'`
  - 添加 `tokenValue?: string`
  - 添加 `baseUrl?: string`
  - **保留** `oauthToken` 用于向后兼容
  - _Requirements: 3.4, 3.5, 3.6_

- [ ] 3.3 创建 AuthType 类型定义
  - 创建共享的 `AuthType` 类型
  - `type AuthType = 'oauth' | 'api_key' | 'proxy'`
  - _Requirements: 3.1, 3.4_

- [ ] 3.4 更新 IPC 类型定义
  - 在 `apps/frontend/src/shared/types/ipc.ts` 中更新 `ISourceEnvConfig`
  - 添加 `claudeAuthType`, `claudeAuthToken`, `claudeBaseUrl`
  - 防止 IPC 通信类型断裂
  - _Requirements: 3.8_

- [ ]* 3.5 编写类型测试
  - 验证类型定义正确性
  - 验证 IPC 类型与 ProjectEnvConfig 一致
  - **Validates: Requirements 3.1-3.8**

- [ ] 4. Checkpoint - 数据结构完成
  - Ensure TypeScript compilation passes
  - Verify no type errors in dependent files
  - Verify IPC handlers compile without errors

---

## Phase 3: 前端环境注入

**Note**: 使用类型特定注入，CLI 从对应变量读取认证。保留 CLAUDE_CONFIG_DIR 回退逻辑。

- [ ] 5. 修改 ProfileManager
- [ ] 5.1 实现 getActiveProfileEnv 类型特定注入
  - 在 `apps/frontend/src/main/claude-profile-manager.ts` 中修改
  - **类型特定注入** (非统一入口):
    - oauth → `CLAUDE_CODE_OAUTH_TOKEN`
    - api_key → `ANTHROPIC_API_KEY`
    - proxy → `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`
  - **保留** CLAUDE_CONFIG_DIR 回退逻辑 (非默认 profile 兼容)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5.2 实现 setProfileToken 扩展
  - 支持 tokenType 参数
  - 支持 baseUrl 参数（proxy 模式）
  - 使用 encryptToken 加密存储
  - _Requirements: 12.1_

- [ ] 5.3 实现 getActiveProfile 迁移逻辑
  - 检测旧字段 `oauthToken`
  - 自动迁移到新字段格式
  - 优先使用新字段
  - _Requirements: 11.2, 11.3_

- [ ]* 5.4 编写属性测试: Profile 类型特定注入 (Vitest)
  - **Property 7: Frontend Profile Type-Specific Injection**
  - 验证 OAuth → CLAUDE_CODE_OAUTH_TOKEN
  - 验证 API Key → ANTHROPIC_API_KEY
  - 验证 Proxy → ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ]* 5.5 编写属性测试: Profile 回退行为 (Vitest)
  - **Property 8: Frontend Profile Fallback Behavior**
  - 验证非默认 profile 无 token 时返回 CLAUDE_CONFIG_DIR
  - **Validates: Requirements 4.5**

- [ ] 6. 修改 TerminalHandler
- [ ] 6.1 扩展 invokeClaude 支持类型特定导出
  - 在 `apps/frontend/src/main/terminal/claude-integration-handler.ts` 中修改
  - **扩展现有 invokeClaude()** (不创建新的 generateEnvExports)
  - 在现有临时文件逻辑中添加类型特定导出:
    - oauth → `export CLAUDE_CODE_OAUTH_TOKEN=...`
    - api_key → `export ANTHROPIC_API_KEY=...`
    - proxy → `export ANTHROPIC_AUTH_TOKEN=... && export ANTHROPIC_BASE_URL=...`
  - **保留** 现有 history protection 逻辑 (HISTFILE=/dev/null)
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 6.2 实现 validateProxyConfig 校验
  - proxy 模式检查 baseUrl
  - 缺失时返回错误并阻断注入
  - _Requirements: 5.4_

- [ ]* 6.3 编写属性测试: Terminal 类型特定导出 (Vitest)
  - **Property 9: Frontend Terminal Type-Specific Export**
  - 验证 OAuth → CLAUDE_CODE_OAUTH_TOKEN
  - 验证 API Key → ANTHROPIC_API_KEY
  - 验证 Proxy → ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ]* 6.4 编写属性测试: Terminal Proxy 校验 (Vitest)
  - **Property 10: Frontend Terminal Proxy Validation**
  - 验证 proxy 缺少 baseUrl 时阻断
  - **Validates: Requirements 5.4, 10.2**

- [ ] 7. 修改 RateLimitDetector
- [ ] 7.1 委托 ProfileManager.getActiveProfileEnv()
  - 在 `apps/frontend/src/main/rate-limit-detector.ts` 中修改
  - 委托 ProfileManager 获取环境变量 (确保类型特定注入一致)
  - _Requirements: 6.1_

- [ ] 7.2 实现 shouldShowOAuthExpiredWarning 方法
  - 新增方法: `shouldShowOAuthExpiredWarning(tokenType: AuthType): boolean`
  - 只对 oauth 类型返回 true
  - api_key 和 proxy 返回 false
  - _Requirements: 6.2, 6.3, 6.4_

- [ ]* 7.3 编写属性测试: OAuth 警告抑制 (Vitest)
  - **Property 11: Frontend OAuth Warning Suppression**
  - 验证 api_key 和 proxy 不显示警告
  - **Validates: Requirements 6.2, 6.3**

- [ ] 8. 修改 AgentQueue
- [ ] 8.1 实现 buildAgentEnv 合并逻辑
  - 在 `apps/frontend/src/main/agent/agent-queue.ts` 中修改
  - 合并优先级 (高到低):
    1. Profile env (from ProfileManager)
    2. Project .env (from autoBuildSource/.env)
    3. Project settings
    4. process.env
  - _Requirements: 7.1_

- [ ] 8.2 实现 logEnvSafe 安全日志
  - 敏感 key 只显示前 6 位 + `...`
  - 短于 6 位显示 `[short]`
  - 覆盖 CLAUDE_CODE_OAUTH_TOKEN, ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN
  - _Requirements: 7.2, 7.3, 12.3_

- [ ]* 8.3 编写属性测试: Env 合并优先级 (Vitest)
  - **Property 12: Frontend Agent Env Merge Precedence**
  - 验证 profile 覆盖 project
  - **Validates: Requirements 7.1**

- [ ]* 8.4 编写属性测试: Token 掩码 (Vitest)
  - **Property 13: Frontend Token Masking**
  - 验证 >= 6 位显示前 6 位 + `...`
  - 验证 < 6 位显示 `[short]`
  - **Validates: Requirements 7.2, 7.3, 12.3**

- [ ] 9. Checkpoint - 环境注入完成
  - Ensure all injection tests pass (Vitest)
  - Verify agent execution works with all auth types
  - Verify CLAUDE_CONFIG_DIR fallback works

---

## Phase 4: 前端 .env 读写

**Note**: 类型检测基于 token 前缀，而非变量名。与后端 `get_token_type()` 逻辑一致。

- [ ] 10. 修改 EnvHandlers
- [ ] 10.1 实现 writeEnvFile 类型特定写入
  - 在 `apps/frontend/src/main/ipc-handlers/env-handlers.ts` 中修改
  - oauth: 写入 `CLAUDE_CODE_OAUTH_TOKEN`
  - api_key: 写入 `ANTHROPIC_API_KEY`
  - proxy: 写入 `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 10.2 实现 readEnvFile 类型检测
  - 读取所有认证相关变量
  - 调用 detectAuthType() 基于 **token 前缀** 检测类型
  - 返回完整的 ProjectEnvConfig
  - _Requirements: 8.4_

- [ ] 10.3 实现 detectAuthType 辅助函数
  - **基于 token 前缀检测** (与后端 get_token_type 一致):
    - `sk-ant-oat01-` 或 `sk-ant-oat` → `oauth`
    - `sk-ant-api` → `api_key`
    - `sk-` (非 oat) → `api_key` (fallback)
    - `pc_` 或 `ccr-` → `proxy`
    - 其他 → `unknown`
  - **不基于变量名检测** (避免前后端不一致)
  - _Requirements: 8.4_

- [ ]* 10.4 编写属性测试: Env 文件类型检测 (Vitest)
  - **Property 14: Frontend Env File Type Detection**
  - 验证 token 前缀检测正确性
  - 验证与后端 get_token_type 行为一致
  - **Validates: Requirements 8.4**

- [ ] 11. 修改 autobuild-source-handlers
- [ ] 11.1 支持 claudeAuthType 读写
  - 在 `apps/frontend/src/main/ipc-handlers/autobuild-source-handlers.ts` 中修改
  - 支持三类 token 写入
  - 读取时调用 detectAuthType() 返回实际生效的认证类型
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 12. Checkpoint - .env 读写完成
  - Ensure env file tests pass (Vitest)
  - Verify .env correctly reflects auth type
  - Verify detectAuthType matches backend get_token_type

---

## Phase 5: 前端 UI 组件

- [ ] 13. 创建 AuthSection 组件
- [ ] 13.1 实现认证类型选择器
  - 在 `apps/frontend/src/renderer/components/project-settings/ClaudeAuthSection.tsx` 中创建
  - 三个选项: OAuth (Recommended), API Key (Direct Billing), Proxy/Enterprise
  - _Requirements: 9.1_

- [ ] 13.2 实现 Token 输入框
  - 根据类型显示不同 label
  - 使用 password 类型隐藏值
  - _Requirements: 9.5_

- [ ] 13.3 实现 API Key 警告
  - 选择 api_key 时显示计费警告
  - _Requirements: 9.2_

- [ ] 13.4 实现 OAuth 提示
  - 选择 oauth 时显示 `claude setup-token` 提示
  - _Requirements: 9.3_

- [ ] 13.5 实现 Proxy Base URL 输入
  - 选择 proxy 时显示 Base URL 输入框
  - 标记为必填
  - _Requirements: 9.4, 10.1_

- [ ] 13.6 实现 Proxy 验证
  - 保存前验证 Base URL 不为空
  - 显示错误提示
  - _Requirements: 10.2_

- [ ] 14. 修改 EnvConfigModal
- [ ] 14.1 支持手动输入多类型
  - 在 `apps/frontend/src/renderer/components/EnvConfigModal.tsx` 中修改
  - 支持 API Key / Proxy 手动输入
  - `claude setup-token` 提示仅在 OAuth 时显示
  - _Requirements: 9.1, 9.3_

- [ ] 15. 修改 IntegrationSettings
- [ ] 15.1 Profile 卡片展示 tokenType
  - 在 `apps/frontend/src/renderer/components/settings/IntegrationSettings.tsx` 中修改
  - 显示当前认证类型
  - _Requirements: 9.1_

- [ ] 15.2 认证状态判断适配
  - 适配 API Key 和 Proxy 的状态判断
  - 使用 hasValidToken() 进行多类型验证
  - _Requirements: 6.2, 6.3, 11.6_

- [ ] 16. Checkpoint - UI 组件完成
  - Ensure UI renders correctly
  - Verify all auth types can be configured
  - Verify i18n keys added for new UI text

---

## Phase 6: 数据迁移和兼容性

**Note**: 需要升级 Profile 存储版本，扩展 hasValidToken 支持多类型验证。

- [ ] 17. 实现数据迁移逻辑
- [ ] 17.1 ProjectEnvConfig 迁移
  - 检测 `claudeOAuthToken` 存在但 `claudeAuthType` 缺失
  - 自动设置 `claudeAuthType: 'oauth'`
  - _Requirements: 11.1_

- [ ] 17.2 ClaudeProfile 迁移
  - 检测 `oauthToken` 存在但 `tokenType` 缺失
  - 自动迁移到新字段格式: `tokenType: 'oauth'`, `tokenValue: oauthToken`
  - _Requirements: 11.2_

- [ ] 17.3 优先级处理
  - 新字段优先于旧字段
  - _Requirements: 11.3_

- [ ] 17.4 Profile 存储版本升级
  - 在 `apps/frontend/src/main/claude-profile/profile-storage.ts` 中修改
  - 定义 ProfileStorageV1 (旧格式: oauthToken)
  - 定义 ProfileStorageV2 (新格式: tokenType, tokenValue, baseUrl)
  - 实现 migrateProfile(v1: V1): V2 迁移函数
  - 启动时自动检测并迁移旧版本数据
  - _Requirements: 11.5_

- [ ] 17.5 扩展 hasValidToken 函数
  - 在 `apps/frontend/src/main/claude-profile/profile-utils.ts` 中修改
  - 支持多类型验证:
    - OAuth: `sk-ant-oat` 前缀
    - API Key: `sk-ant-api` 或 `sk-` (非 oat) 前缀
    - Proxy: `pc_` 或 `ccr-` 前缀 + baseUrl 存在
  - _Requirements: 11.6_

- [ ]* 17.6 编写属性测试: 数据迁移正确性 (Vitest)
  - **Property 15: Data Migration Correctness**
  - 验证 V1 → V2 迁移逻辑正确
  - 验证旧字段自动迁移
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.5**

- [ ]* 17.7 编写属性测试: hasValidToken 多类型 (Vitest)
  - **Property 16: Token Validity Multi-Type**
  - 验证 OAuth token 验证
  - 验证 API Key token 验证
  - 验证 Proxy token + baseUrl 验证
  - **Validates: Requirements 11.6**

- [ ] 18. Checkpoint - 迁移完成
  - Ensure migration tests pass (Vitest)
  - Verify existing OAuth users unaffected
  - Verify storage version upgrade works
  - Verify hasValidToken works for all types

---

## Phase 7: 集成测试和验收

- [ ] 19. 编写集成测试
- [ ]* 19.1 E2E OAuth 流程测试
  - UI → Profile → Agent → SDK → CLI
  - 验证完整流程
  - 验证 CLAUDE_CODE_OAUTH_TOKEN 正确传递
  - **Validates: Requirements 4.1, 5.1, 7.1**

- [ ]* 19.2 E2E API Key 流程测试
  - UI → Profile → Agent → SDK → CLI
  - 验证警告显示
  - 验证 ANTHROPIC_API_KEY 正确传递
  - **Validates: Requirements 4.2, 5.2, 9.2**

- [ ]* 19.3 E2E Proxy 流程测试
  - UI → Profile → Agent → SDK → CLI
  - 验证 Base URL 传递
  - 验证 ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL 正确传递
  - **Validates: Requirements 4.3, 5.3, 10.1, 10.2**

- [ ]* 19.4 Terminal 集成测试
  - UI → Terminal → CLI
  - 验证环境变量正确注入 (类型特定)
  - 验证 history protection 保留
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ]* 19.5 迁移集成测试
  - 旧数据 → 新格式
  - 验证无缝迁移
  - 验证 hasValidToken 多类型
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.5, 11.6**

- [ ]* 19.6 CLI 项目 .env 集成测试
  - CLI 读取 {project}/.auto-claude/.env
  - 验证优先级: 项目 .env > 全局 .env
  - **Validates: Requirements 8.5**

- [ ] 20. 更新文档
- [ ] 20.1 更新 .env.example
  - 添加三种认证方式示例
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 20.2 更新 README
  - 添加 UI 认证配置说明
  - _Requirements: 9.1_

- [ ] 21. 最终 Checkpoint - 确保所有测试通过
  - Ensure all tests pass (pytest + Vitest), ask the user if questions arise.
  - 验证 CLI 三种认证正常工作
  - 验证 CLI 读取项目 .env 正常工作
  - 验证 UI 三种认证正常工作
  - 验证 Terminal 注入正常工作 (类型特定)
  - 验证旧 OAuth 用户不受影响
  - 验证数据迁移正常工作
  - 验证 hasValidToken 多类型正常工作
  - 验证 ANTHROPIC_API_KEY 不被清理 (Graphiti 兼容)
