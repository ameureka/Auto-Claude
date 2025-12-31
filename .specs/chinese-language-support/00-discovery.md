# Feature Discovery: Chinese Language Support (中文支持)

## 1. 功能概述

为 Auto-Claude 前端应用添加简体中文语言支持，使中文用户能够使用母语操作应用。

## 2. 目标与非目标

### 目标 (In Scope)
- [x] 添加简体中文 (zh-CN) 作为第三种支持语言
- [x] 翻译所有 8 个命名空间的 UI 文本
- [x] 在语言设置中显示中文选项
- [x] 确保语言切换即时生效

### 非目标 (Out of Scope)
- [ ] 繁体中文支持 (zh-TW) - 可作为后续功能
- [ ] 后端 CLI 输出的中文化 - 仅前端 UI
- [ ] 文档的中文翻译 - 仅应用内 UI
- [ ] 日期/数字格式本地化 - 使用现有格式

## 3. 用户旅程

1. 用户打开 Auto-Claude 应用
2. 进入 Settings → Language 设置页面
3. 看到三个语言选项：English, Français, 简体中文
4. 点击"简体中文"
5. 整个应用界面立即切换为中文显示
6. 下次启动应用时保持中文设置

## 4. 输入/输出

| 类型 | 描述 |
|------|------|
| 输入 | 英文翻译文件 (8个 JSON 文件，共 777 行) |
| 输出 | 中文翻译文件 (8个 JSON 文件) + 配置更新 |

## 5. 约束条件

- **兼容性**: 必须与现有 i18n 框架 (react-i18next) 兼容
- **完整性**: 所有 8 个命名空间必须完整翻译
- **一致性**: 翻译术语需保持一致 (如 "Task" 统一翻译为 "任务")
- **回退**: 缺失翻译时回退到英文

## 6. 现状分析

### 当前支持的语言
| 语言 | 代码 | 状态 |
|------|------|------|
| English | en | ✅ 默认语言 |
| Français | fr | ✅ 完整支持 |
| 简体中文 | zh | ⏳ 待添加 |

### i18n 技术栈
- **框架**: react-i18next (^16.5.0)
- **核心库**: i18next (^25.7.3)
- **配置**: 静态导入，无动态加载

### 相关模块

| 文件 | 职责 |
|------|------|
| `apps/frontend/src/shared/constants/i18n.ts` | 语言常量定义 (SupportedLanguage, AVAILABLE_LANGUAGES) |
| `apps/frontend/src/shared/i18n/index.ts` | i18n 初始化配置，资源注册 |
| `apps/frontend/src/shared/i18n/locales/en/*.json` | 英文翻译文件 (8个) |
| `apps/frontend/src/shared/i18n/locales/fr/*.json` | 法文翻译文件 (8个) |
| `apps/frontend/src/renderer/components/settings/LanguageSettings.tsx` | 语言切换 UI 组件 |

### 翻译文件结构

```
apps/frontend/src/shared/i18n/locales/
├── en/
│   ├── common.json         # 通用标签、按钮、错误 (115行)
│   ├── navigation.json     # 侧边栏导航 (32行)
│   ├── settings.json       # 设置页面 (306行)
│   ├── tasks.json          # 任务相关 (86行)
│   ├── onboarding.json     # 引导向导 (93行)
│   ├── welcome.json        # 欢迎屏幕 (16行)
│   ├── dialogs.json        # 对话框 (122行)
│   └── taskReview.json     # 任务审查 (7行)
├── fr/
│   └── [相同结构]
└── zh/                     # 待创建
    └── [相同结构]
```

### 依赖关系

```
LanguageSettings.tsx
    ↓ 使用
AVAILABLE_LANGUAGES (constants/i18n.ts)
    ↓ 定义
SupportedLanguage 类型
    ↓ 约束
i18n.changeLanguage() 参数

i18n/index.ts
    ↓ 导入
locales/{lang}/*.json
    ↓ 注册到
resources 对象
    ↓ 初始化
i18next 实例
```

### 可复用代码

- `locales/en/*.json` - 作为翻译模板
- `locales/fr/*.json` - 作为翻译参考（结构完全一致）
- `LanguageSettings.tsx` - 无需修改，自动读取 AVAILABLE_LANGUAGES

## 7. 历史参考

法语支持的添加模式可作为参考：
- 创建 `locales/fr/` 目录
- 复制英文文件结构
- 翻译所有键值
- 在 `i18n.ts` 中注册资源
- 在 `constants/i18n.ts` 中添加语言选项

## 8. 开放问题

- [x] ~~语言代码使用 `zh` 还是 `zh-CN`?~~ → 使用 `zh` (简洁，与 en/fr 一致)
- [x] ~~是否需要处理 RTL (从右到左)?~~ → 否，中文是 LTR
- [x] ~~专业术语翻译确认~~ → 已确认，见下方术语表

## 9. 术语表 (已确认)

| 英文 | 中文翻译 | 说明 |
|------|----------|------|
| Task | 任务 | 核心概念 |
| Spec | 规格 | 功能规格文档 |
| Agent | 代理 | AI Agent |
| Kanban | 看板 | 任务看板视图 |
| Terminal | 终端 | 代理终端 |
| Worktree | 工作树 | Git 术语 |
| Profile | 配置文件 | Claude 配置文件 |
| Settings | 设置 | 应用设置 |
| Project | 项目 | 项目管理 |
| Build | 构建 | 任务构建 |
| Review | 审查 | 代码审查 |
| Merge | 合并 | 代码合并 |
| Discard | 丢弃 | 丢弃更改 |
| Rate Limit | 速率限制 | API 限制 |
| OAuth | OAuth | 保留英文 |
| API Key | API 密钥 | 认证方式 |
| Save | 保存 | 通用操作 |
| Cancel | 取消 | 通用操作 |
| Delete | 删除 | 通用操作 |
| Create | 创建 | 通用操作 |
| Loading | 加载中 | 状态提示 |
| Error | 错误 | 状态提示 |
| Success | 成功 | 状态提示 |

---

## 审批状态

- [x] 用户确认目标/非目标
- [x] 用户确认术语表
- [x] 用户批准进入 Phase 2

---

**下一步**: 用户批准后，进入 Phase 2 编写正式需求规范 (01-requirements.md)
