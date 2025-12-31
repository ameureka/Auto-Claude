# Implementation Plan: Chinese Language Support (中文支持)

## Overview

本任务清单将中文语言支持的设计转化为可执行的编码任务。实施顺序遵循"底层配置 → 翻译文件 → 注册集成 → 测试验证"的原则。

## Dependencies

- 无外部依赖需要安装
- 基于现有 react-i18next 框架

## Tasks

- [ ] 1. 更新语言配置常量
- [ ] 1.1 修改 SupportedLanguage 类型
  - 在 `apps/frontend/src/shared/constants/i18n.ts` 中添加 'zh'
  - 更新类型定义: `export type SupportedLanguage = 'en' | 'fr' | 'zh';`
  - 验证 DEFAULT_LANGUAGE 保持为 'en' (不变量检查)
  - _Requirements: 1.1, 1.3_

- [ ] 1.2 添加中文到 AVAILABLE_LANGUAGES
  - 添加 `{ value: 'zh' as const, label: 'Chinese', nativeLabel: '简体中文' }`
  - _Requirements: 1.2_

- [ ]* 1.3 编写属性测试: 语言配置
  - **Property 1: Language type includes Chinese**
  - **Property 2: Available languages includes Chinese entry**
  - **Validates: Requirements 1.1, 1.2**

- [ ] 2. 创建中文翻译文件
- [ ] 2.1 创建 zh/common.json
  - 复制 `locales/en/common.json` 结构
  - 翻译所有键值为中文
  - 保留插值占位符 ({{...}})
  - _Requirements: 3.1, 6.1, 6.2, 6.3_

- [ ] 2.2 创建 zh/navigation.json
  - 复制 `locales/en/navigation.json` 结构
  - 翻译所有键值为中文
  - _Requirements: 3.2, 6.1, 6.2_

- [ ] 2.3 创建 zh/settings.json
  - 复制 `locales/en/settings.json` 结构
  - 翻译所有键值为中文
  - 保留插值占位符
  - _Requirements: 3.3, 6.1, 6.2, 6.3_

- [ ] 2.4 创建 zh/tasks.json
  - 复制 `locales/en/tasks.json` 结构
  - 翻译所有键值为中文
  - _Requirements: 3.4, 6.1, 6.2_

- [ ] 2.5 创建 zh/welcome.json
  - 复制 `locales/en/welcome.json` 结构
  - 翻译所有键值为中文
  - _Requirements: 3.5, 6.1, 6.2_

- [ ] 2.6 创建 zh/onboarding.json
  - 复制 `locales/en/onboarding.json` 结构
  - 翻译所有键值为中文
  - _Requirements: 3.6, 6.1, 6.2_

- [ ] 2.7 创建 zh/dialogs.json
  - 复制 `locales/en/dialogs.json` 结构
  - 翻译所有键值为中文
  - 保留插值占位符
  - _Requirements: 3.7, 6.1, 6.2, 6.3_

- [ ] 2.8 创建 zh/taskReview.json
  - 复制 `locales/en/taskReview.json` 结构
  - 翻译所有键值为中文
  - _Requirements: 3.8, 6.1, 6.2_

- [ ] 3. Checkpoint - 翻译文件完成
  - 确保所有 8 个翻译文件已创建
  - 确保 JSON 语法正确
  - Ensure all translation files are valid JSON, ask the user if questions arise.

- [ ] 4. 注册中文翻译资源
- [ ] 4.1 导入中文翻译文件
  - 在 `apps/frontend/src/shared/i18n/index.ts` 中添加导入语句
  - 导入所有 8 个 zh/*.json 文件
  - _Requirements: 2.1_

- [ ] 4.2 注册到 resources 对象
  - 在 resources 对象中添加 'zh' 键
  - 包含所有 8 个命名空间
  - _Requirements: 2.2, 2.3_

- [ ]* 4.3 编写属性测试: 资源注册
  - **Property 3: Chinese resources registered for all namespaces**
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ] 5. 编写翻译完整性测试
- [ ]* 5.1 编写键完整性测试
  - 创建 `apps/frontend/src/__tests__/i18n/translation-completeness.test.ts`
  - 验证 zh/*.json 包含 en/*.json 的所有键
  - **Property 4: Translation key completeness**
  - **Validates: Requirements 3.1-3.8**

- [ ]* 5.2 编写插值占位符测试
  - 创建 `apps/frontend/src/__tests__/i18n/interpolation.test.ts`
  - 验证中文翻译保留所有 {{...}} 占位符
  - **Property 5: Interpolation placeholder preservation**
  - **Validates: Requirements 6.3**

- [ ]* 5.3 编写回退机制测试
  - 验证缺失键回退到英文
  - 验证双重缺失时显示翻译键本身
  - **Property 6: Fallback to English**
  - **Validates: Requirements 5.1, 5.2**

- [ ] 6. Checkpoint - 确保所有测试通过
  - 运行 `npm run test` 验证所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. 集成验证
- [ ] 7.1 验证语言切换功能
  - 启动应用，进入 Settings → Language
  - 确认显示"简体中文"选项
  - 点击切换，验证 UI 更新为中文
  - _Requirements: 4.1, 4.2_

- [ ] 7.2 验证语言持久化
  - 切换到中文后重启应用
  - 确认应用保持中文显示
  - _Requirements: 4.3_

- [ ] 8. 最终 Checkpoint - 确保所有测试通过
  - 运行完整测试套件
  - 验证 TypeScript 编译无错误
  - Ensure all tests pass, ask the user if questions arise.

---

## 术语翻译参考

在翻译过程中使用以下术语表确保一致性：

| English | Chinese |
|---------|---------|
| Task | 任务 |
| Spec | 规格 |
| Agent | 代理 |
| Kanban | 看板 |
| Terminal | 终端 |
| Worktree | 工作树 |
| Profile | 配置文件 |
| Settings | 设置 |
| Project | 项目 |
| Build | 构建 |
| Review | 审查 |
| Merge | 合并 |
| Discard | 丢弃 |
| Rate Limit | 速率限制 |
| Save | 保存 |
| Cancel | 取消 |
| Delete | 删除 |
| Create | 创建 |
| Loading | 加载中 |
| Error | 错误 |
| Success | 成功 |

---

## 审批状态

- [ ] 用户确认任务清单
- [ ] 用户批准进入 Phase 5 实施

---

**下一步**: 用户批准后，进入 Phase 5 开始迭代实施
