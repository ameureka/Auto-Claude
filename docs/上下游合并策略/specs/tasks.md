# Implementation Plan: 上游代码合并

## 概述

合并 upstream/develop 的 11 个新提交到本地 fork，同时保护本地的多认证和 i18n 定制改动。

---

## 潜在冲突文件 (5 个)

| 文件 | 处理策略 |
|------|---------|
| `apps/backend/core/auth.py` | `--ours` 保留本地 |
| `apps/backend/core/client.py` | `--ours` 保留本地 |
| `apps/backend/.env.example` | 手动合并 |
| `apps/frontend/src/shared/i18n/index.ts` | 手动合并 |
| `apps/frontend/package-lock.json` | 重新生成 |

---

## Implementation Plan

- [ ] 1. 准备工作
  - 创建备份分支
  - 验证当前工作区干净
  - _Requirements: 1.1_

- [ ] 1.1 创建备份分支
  - 执行 `git branch backup-$(date +%Y%m%d)`
  - _Requirements: 1.1_

- [ ] 1.2 确保工作区干净
  - 执行 `git status` 确认无未提交改动
  - _Requirements: 1.1_

- [ ] 2. 执行合并
  - 合并上游代码
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2.1 获取上游最新代码
  - 执行 `git fetch upstream`
  - _Requirements: 1.1_

- [ ] 2.2 执行合并
  - 执行 `git merge upstream/develop`
  - _Requirements: 1.1, 1.2_

- [ ] 3. 解决冲突 - 多认证保护
  - 保护 Multi_Auth_System 设计
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 3.1 保护 auth.py
  - 执行 `git checkout --ours apps/backend/core/auth.py`
  - 验证 ANTHROPIC_API_KEY 存在于 AUTH_TOKEN_ENV_VARS
  - _Requirements: 2.1, 2.5_

- [ ] 3.2 保护 client.py
  - 执行 `git checkout --ours apps/backend/core/client.py`
  - _Requirements: 2.2_

> **注意**: `simple_client.py` 和 `cli/utils.py` 上游无改动，不会产生冲突，无需特殊处理。

- [ ] 4. 解决冲突 - i18n 保护
  - 保护中文支持
  - _Requirements: 3.1, 3.2_

- [ ] 4.1 手动合并 i18n/index.ts
  - 保留中文 locale 注册代码
  - 合并上游可能的新 locale 支持
  - _Requirements: 3.1_

- [ ] 5. 解决冲突 - 其他文件
  - _Requirements: 1.3_

- [ ] 5.1 手动合并 .env.example
  - 保留本地认证配置示例
  - 合并上游新增的配置项
  - _Requirements: 1.3_

- [ ] 5.2 重新生成 package-lock.json
  - 执行 `cd apps/frontend && pnpm install`
  - _Requirements: 1.3_

- [ ] 6. 标记冲突已解决
  - 执行 `git add .`
  - _Requirements: 1.3_

- [ ] 7. 完成合并
  - 执行 `git commit -m "merge: sync with upstream/develop, preserve multi-auth design"`
  - _Requirements: 1.3_

- [ ] 8. Checkpoint - 确保合并完成
  - Ensure merge commit is created, ask the user if questions arise.

- [ ] 9. 验证合并结果
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 9.1 运行认证属性测试
  - 执行 `cd apps/backend && pytest tests/test_auth_properties.py -v`
  - **Validates: Requirements 4.1**
  - _Requirements: 4.1_

- [ ]* 9.2 验证前端构建
  - 执行 `cd apps/frontend && pnpm build`
  - **Validates: Requirements 4.2**
  - _Requirements: 4.2_

- [ ] 9.3 验证 --base-branch 修复
  - 检查 spec_runner.py 是否包含 --base-branch 参数
  - _Requirements: 5.1_

- [ ] 10. 最终 Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.
