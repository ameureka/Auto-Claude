# 需求文档标准 (EARS + INCOSE)

## 概述

需求文档使用两个国际标准来确保需求的精确性和可测试性：
- **EARS (Easy Approach to Requirements Syntax)** - 需求语法模式
- **INCOSE (International Council on Systems Engineering)** - 语义质量规则

## EARS 六种模式

每个需求**必须**遵循以下六种模式之一：

### 1. 普遍型 (Ubiquitous)
系统始终应该做的事情，没有前置条件。

```
THE <system> SHALL <response>
```

**示例**:
- THE system SHALL encrypt all user passwords using bcrypt
- THE API SHALL return responses in JSON format

### 2. 事件驱动型 (Event-driven)
当特定事件发生时系统应该做的事情。

```
WHEN <trigger>, THE <system> SHALL <response>
```

**示例**:
- WHEN a user submits a login form, THE authentication service SHALL validate credentials
- WHEN a file upload completes, THE storage service SHALL generate a thumbnail

### 3. 状态驱动型 (State-driven)
当系统处于特定状态时应该做的事情。

```
WHILE <condition>, THE <system> SHALL <response>
```

**示例**:
- WHILE the user is logged in, THE session manager SHALL refresh tokens every 15 minutes
- WHILE the system is in maintenance mode, THE API SHALL return 503 status codes

### 4. 异常事件型 (Unwanted event)
当不期望的情况发生时系统应该做的事情。

```
IF <condition>, THEN THE <system> SHALL <response>
```

**示例**:
- IF database connection fails, THEN THE system SHALL retry with exponential backoff
- IF user input exceeds maximum length, THEN THE validator SHALL reject the input

### 5. 可选功能型 (Optional feature)
可配置或可选的功能。

```
WHERE <option>, THE <system> SHALL <response>
```

**示例**:
- WHERE two-factor authentication is enabled, THE login flow SHALL require OTP verification
- WHERE dark mode is selected, THE UI SHALL apply dark theme styles

### 6. 复合型 (Complex)
组合多个条件，**必须**按以下顺序：

```
[WHERE] [WHILE] [WHEN/IF] THE <system> SHALL <response>
```

**示例**:
- WHERE premium subscription is active, WHILE user is online, WHEN new content is available, THE notification service SHALL send push notification
- WHILE system load is below 80%, WHEN batch job is scheduled, THE processor SHALL execute immediately

## INCOSE 语义质量规则

所有需求**必须**符合以下规则：

### ✅ 必须遵守

| 规则 | 说明 | 示例 |
|------|------|------|
| 主动语态 | 明确谁做什么 | ✅ THE system SHALL validate ❌ Input shall be validated |
| 单一思想 | 每个需求只表达一件事 | ✅ 分开写 ❌ SHALL validate AND store |
| 明确条件 | 条件必须可测量 | ✅ within 500ms ❌ quickly |
| 定义术语 | 所有术语在术语表中定义 | ✅ THE AuthService (见术语表) |
| 一致术语 | 全文使用相同术语 | ✅ 始终用 "user" ❌ user/customer 混用 |

### ❌ 必须避免

| 禁止项 | 说明 | 错误示例 |
|--------|------|----------|
| 模糊词汇 | quickly, adequate, user-friendly | ❌ respond quickly |
| 逃避条款 | where possible, if feasible | ❌ where possible |
| 否定陈述 | SHALL NOT | ❌ SHALL NOT allow |
| 代词 | it, them, this | ❌ it shall process |
| 绝对词 | never, always, 100% | ❌ always available |
| 解决方案 | 描述如何而非什么 | ❌ using MySQL |

## 文档格式

```markdown
# Requirements Document

## Introduction

[功能/系统的简要描述]

## Glossary

- **System_Name**: [定义]
- **Technical_Term**: [定义]

## Requirements

### Requirement 1

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event], THE [System_Name] SHALL [response]
2. WHILE [state], THE [System_Name] SHALL [response]
3. IF [undesired event], THEN THE [System_Name] SHALL [response]
4. WHERE [optional feature], THE [System_Name] SHALL [response]

### Requirement 2

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. THE [System_Name] SHALL [response]
2. WHEN [event], THE [System_Name] SHALL [response]

[继续更多需求...]
```

## 验收标准数量

每个需求应包含 **2-5 个验收标准**：
- 少于 2 个：需求可能过于简单或不完整
- 多于 5 个：需求可能需要拆分

## 特殊关注：解析器和序列化器

**重要**: 涉及解析或序列化的功能**必须**包含：
1. 解析器需求
2. 打印器/序列化器需求
3. 往返测试 (Round-trip) 验收标准

```markdown
#### Acceptance Criteria

1. WHEN parsing user input, THE parser SHALL validate against the grammar
2. WHEN serializing data, THE serializer SHALL produce valid JSON
3. WHEN data is serialized then parsed, THE system SHALL produce equivalent data
```

## 常见正确性模式

在编写验收标准时，考虑以下常见模式：

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| 不变量 | 操作后保持不变的属性 | 集合大小、树平衡 |
| 往返 | 操作与逆操作组合返回原值 | 序列化/反序列化 |
| 幂等性 | 多次执行等于执行一次 | 去重、数据库更新 |
| 变形属性 | 已知的输入输出关系 | 过滤后长度减少 |
| 错误条件 | 错误输入产生正确错误 | 输入验证 |

## 检查清单

在提交需求文档前，确认：

- [ ] 每个需求遵循 EARS 模式之一
- [ ] 复合需求按 WHERE → WHILE → WHEN/IF → THE → SHALL 顺序
- [ ] 术语表定义了所有系统名称和技术术语
- [ ] 使用主动语态
- [ ] 无模糊词汇 (quickly, adequate 等)
- [ ] 无逃避条款 (where possible 等)
- [ ] 无否定陈述
- [ ] 无代词
- [ ] 每个需求只表达一个思想
- [ ] 解析器/序列化器包含往返测试标准
