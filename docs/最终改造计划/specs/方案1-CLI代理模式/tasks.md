# Implementation Plan: CLI Multi-Auth Support

## Overview

本任务清单将方案1（CLI代理模式）的设计转化为可执行的编码任务。

### 依赖项

- **Hypothesis**: 属性测试框架，需添加到 `tests/requirements-test.txt`
  ```
  hypothesis>=6.0.0
  ```

### 关键设计原则

1. **类型特定注入**: 不同 Token 类型写入对应的环境变量（CLI 从类型特定变量读取）
2. **早期失败**: Proxy 配置验证在 CLIValidator 中进行，尽早阻断错误配置
3. **向后兼容**: 现有 OAuth 用户无需任何更改

---

- [ ] 1. 修改 AuthModule 常量和基础函数
- [ ] 1.1 扩展 AUTH_TOKEN_ENV_VARS 列表
  - 在 `apps/backend/core/auth.py` 中添加 `ANTHROPIC_API_KEY` 到优先级列表
  - 更新注释说明新的优先级顺序
  - _Requirements: 3.1, 7.1_

- [ ] 1.2 扩展 SDK_ENV_VARS 列表
  - 添加 `ANTHROPIC_API_KEY` 到 SDK 环境变量传递列表
  - _Requirements: 7.1, 7.2_

- [ ] 1.3 实现 get_token_type 函数
  - 创建 Token 类型检测函数
  - 实现 OAuth 前缀匹配 (`sk-ant-oat01-`, `sk-ant-oat`)
  - 实现 API Key 前缀匹配 (`sk-ant-api`, `sk-` excluding oat)
  - 实现 Proxy 前缀匹配 (`pc_`, `ccr-`)
  - 返回 `unknown` 作为默认值
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 1.4 编写属性测试: Token 分类正确性
  - **Property 1: Token Classification Correctness**
  - 使用 Hypothesis 生成随机 Token 字符串
  - 验证分类结果与前缀规则一致
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [ ] 2. 实现类型特定环境注入
- [ ] 2.1 实现 apply_auth_env 函数
  - 清理冲突变量 (`CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`)
  - 根据 Token 类型写入对应环境变量:
    - oauth → `CLAUDE_CODE_OAUTH_TOKEN`
    - api_key → `ANTHROPIC_API_KEY`
    - proxy → `ANTHROPIC_AUTH_TOKEN`
    - unknown → `CLAUDE_CODE_OAUTH_TOKEN` (fallback)
  - 返回 Token 类型字符串
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 2.2 编写属性测试: 类型特定注入
  - **Property 2: Type-Specific Environment Injection**
  - 验证 OAuth Token 写入 `CLAUDE_CODE_OAUTH_TOKEN`
  - 验证 API Key Token 写入 `ANTHROPIC_API_KEY`
  - 验证 Proxy Token 写入 `ANTHROPIC_AUTH_TOKEN`
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ]* 2.3 编写属性测试: 冲突变量清理
  - **Property 3: Conflicting Variable Cleanup**
  - 预设多个冲突变量，验证调用后只保留正确变量
  - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 2.4 实现 is_api_key_mode 辅助函数
  - 检查当前是否使用 API Key 模式
  - _Requirements: 5.1_

- [ ]* 2.5 编写属性测试: 优先级解析确定性
  - **Property 4: Priority Resolution Determinism**
  - 预设多个 Token 环境变量，验证优先级解析正确
  - 验证 CLAUDE_CODE_OAUTH_TOKEN > ANTHROPIC_AUTH_TOKEN > ANTHROPIC_API_KEY
  - **Validates: Requirements 3.1, 3.2**

- [ ] 3. 实现 Proxy 配置验证
- [ ] 3.1 实现 validate_proxy_config 函数
  - 检查 Token 类型是否为 `proxy`
  - 验证 `ANTHROPIC_BASE_URL` 是否设置
  - 返回 `(is_valid, error_message)` 元组
  - _Requirements: 4.1, 4.2_

- [ ]* 3.2 编写属性测试: Proxy 验证完整性
  - **Property 5: Proxy Validation Completeness**
  - 验证 Proxy Token 在缺少 Base URL 时返回错误
  - 验证 Proxy Token 在设置 Base URL 时返回成功
  - **Validates: Requirements 4.1, 4.2**

- [ ] 4. 修改错误消息
- [ ] 4.1 更新 require_auth_token 错误消息
  - 列出三种支持的认证方法
  - 包含 OAuth 设置指南 (`claude setup-token`)
  - 包含 API Key 设置指南 (`ANTHROPIC_API_KEY`)
  - 包含 Proxy 设置指南 (`ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 5. Checkpoint - AuthModule 完成
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. 修改 ClientFactory
- [ ] 6.1 更新 create_client 函数导入
  - 导入 `apply_auth_env`, `get_token_type`, `validate_proxy_config`
  - _Requirements: 2.1_

- [ ] 6.2 实现类型特定认证注入
  - 调用 `apply_auth_env(token)` 替换直接写入
  - 获取 `token_type` 用于后续逻辑
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 6.3 添加 Proxy 配置校验
  - 调用 `validate_proxy_config()`
  - 校验失败时抛出 `ValueError`
  - _Requirements: 4.2_

- [ ] 6.4 添加认证模式警告
  - API Key 模式: 打印计费警告
  - Proxy 模式: 打印 Base URL 信息
  - _Requirements: 5.1, 4.3_

- [ ] 7. 修改 SimpleClientFactory
- [ ] 7.1 更新 create_simple_client 函数导入
  - 导入 `apply_auth_env`
  - _Requirements: 8.3_

- [ ] 7.2 实现类型特定认证注入
  - 调用 `apply_auth_env(token)` 替换直接写入 `os.environ`
  - 移除内联 `import os`
  - _Requirements: 2.1, 2.2, 2.3, 8.3_

- [ ] 8. Checkpoint - ClientFactories 完成
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. 修改 CLIValidator (早期验证)
- [ ] 9.1 更新 validate_environment 函数导入
  - 导入 `get_token_type`, `validate_proxy_config`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1_

- [ ] 9.2 实现早期 Proxy 配置校验
  - 调用 `validate_proxy_config()` 在执行前验证
  - 校验失败时返回 `False` 阻断执行（早期失败原则）
  - 成功时显示 Base URL
  - _Requirements: 4.1, 4.2_

- [ ] 9.3 实现认证模式显示
  - 调用 `get_token_type()` 获取类型
  - 打印当前认证模式 (OAuth / API Key / Proxy)
  - _Requirements: 5.2_

- [ ] 9.4 添加 API Key 警告框
  - 显示醒目的计费警告
  - 建议设置预算上限
  - _Requirements: 5.1, 5.2_

- [ ] 9.5 更新无 Token 错误消息
  - 列出三种支持的认证方法
  - _Requirements: 6.1_

- [ ] 10. Checkpoint - CLIValidator 完成
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. 编写集成测试
- [ ]* 11.1 编写 OAuth 模式集成测试
  - 验证现有 OAuth 流程不受影响
  - **Validates: Requirements 8.1, 8.2**

- [ ]* 11.2 编写 API Key 模式集成测试
  - 验证 API Key 可正常认证
  - 验证警告消息显示
  - **Validates: Requirements 5.1, 5.2**

- [ ]* 11.3 编写 Proxy 模式集成测试
  - 验证 Proxy Token + Base URL 可正常认证
  - 验证缺少 Base URL 时阻断
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ]* 11.4 编写属性测试: 向后兼容性
  - **Property 6: Backward Compatibility**
  - 验证 OAuth 路径行为一致
  - 验证 Keychain 路径行为一致
  - **Validates: Requirements 8.1, 8.2, 8.3**

- [ ] 12. 更新 .env.example
- [ ] 12.1 添加认证配置示例
  - 添加 OAuth Token 示例和注释
  - 添加 API Key 示例和注释
  - 添加 Proxy Token + Base URL 示例和注释
  - _Requirements: 6.2, 6.3, 6.4_

- [ ] 13. 最终 Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.
  - 验证 OAuth 模式正常工作
  - 验证 API Key 模式正常工作并显示警告
  - 验证 Proxy 模式正常工作并校验 Base URL
