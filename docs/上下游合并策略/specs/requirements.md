# Requirements Document: 上游代码合并

## Introduction

将 upstream/develop (AndyMik90/Auto-Claude) 的最新代码合并到本地 fork，同时保留本地的多认证 (Multi-Auth) 和多语言 (i18n) 定制改动。

## Glossary

- **Upstream**: 上游仓库 (https://github.com/AndyMik90/Auto-Claude)
- **Local_Fork**: 本地 fork 仓库 (ameureka/Auto-Claude)
- **Multi_Auth_System**: 本地定制的多认证系统，支持 OAuth、API Key、Proxy 三种模式
- **Design_Conflict**: 上游故意移除 ANTHROPIC_API_KEY 支持，与本地设计意图相反
- **Conflict_File**: 本地和上游都修改了的文件

## Requirements

### Requirement 1: 代码同步

**User Story:** As a developer, I want to sync upstream changes, so that I can get bug fixes and new features.

#### Acceptance Criteria

1. WHEN upstream/develop has new commits, THE Merge_System SHALL fetch all new commits
2. THE Merge_System SHALL identify all Conflict_Files before merge
3. THE Merge_System SHALL preserve all Local_Fork customizations

### Requirement 2: 多认证设计保护

**User Story:** As a developer, I want to protect my Multi_Auth_System design, so that ANTHROPIC_API_KEY support is preserved.

#### Acceptance Criteria

1. WHEN merging auth.py, THE Merge_System SHALL preserve local AUTH_TOKEN_ENV_VARS including ANTHROPIC_API_KEY
2. WHEN merging client.py, THE Merge_System SHALL preserve Multi_Auth_System type-specific injection logic
3. WHEN merging simple_client.py, THE Merge_System SHALL preserve Multi_Auth_System type-specific injection logic
4. WHEN merging cli/utils.py, THE Merge_System SHALL preserve early proxy validation logic
5. IF upstream removes ANTHROPIC_API_KEY, THEN THE Merge_System SHALL restore it from local version

### Requirement 3: i18n 保护

**User Story:** As a developer, I want to preserve Chinese language support, so that i18n customization is maintained.

#### Acceptance Criteria

1. WHEN merging i18n/index.ts, THE Merge_System SHALL preserve Chinese locale registration
2. THE Merge_System SHALL preserve all zh/*.json locale files

### Requirement 4: 合并验证

**User Story:** As a developer, I want to verify the merge, so that all functionality works correctly.

#### Acceptance Criteria

1. WHEN merge is complete, THE Test_System SHALL pass all auth property tests
2. WHEN merge is complete, THE Build_System SHALL compile without errors
3. IF any test fails, THEN THE Merge_System SHALL report the failure to user

### Requirement 5: 上游新功能集成

**User Story:** As a developer, I want to get upstream new features, so that I benefit from community improvements.

#### Acceptance Criteria

1. THE Merge_System SHALL integrate PR #428 (spec_runner --base-branch fix)
2. THE Merge_System SHALL integrate GitLab integration (if no conflicts)
3. THE Merge_System SHALL integrate UI improvements from upstream
