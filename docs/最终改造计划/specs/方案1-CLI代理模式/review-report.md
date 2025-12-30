# FPF 审查报告 - 方案1 CLI代理模式 Specs (第二轮)

## 审查概述

- **审查日期**: 2025-12-30
- **审查方法**: FPF 第一性原理推理框架
- **审查范围**: requirements.md, design.md, tasks.md
- **触发原因**: 外部反馈指出"统一入口"设计存在根本性缺陷

---

## 发现的问题

### P1: 统一入口假设错误 (严重) ✅ 已修正

**位置**: requirements.md - Requirement 2, design.md - 核心设计决策

**原问题**:
```
所有 Token 类型最终都写入 CLAUDE_CODE_OAUTH_TOKEN，因为这是 SDK 的唯一读取点
```

**缺陷**:
- 原假设认为 SDK 只读取 `CLAUDE_CODE_OAUTH_TOKEN`
- **实际行为**: Claude Code CLI 从类型特定环境变量读取认证:
  - `CLAUDE_CODE_OAUTH_TOKEN` for OAuth
  - `ANTHROPIC_API_KEY` for API Key
  - `ANTHROPIC_AUTH_TOKEN` for Proxy
- SDK 通过 `ClaudeAgentOptions(env={...})` 将环境变量传递给 CLI 子进程

**验证来源**: Context7 SDK 文档 + Anthropic CLI 文档

**修正**:
- 将"统一入口原则"改为"类型特定注入"
- OAuth → `CLAUDE_CODE_OAUTH_TOKEN`
- API Key → `ANTHROPIC_API_KEY`
- Proxy → `ANTHROPIC_AUTH_TOKEN`

---

### P2: API Key/Proxy 变量仅用于"日志"导致认证失败 (严重) ✅ 已修正

**位置**: requirements.md - Requirement 2.3, 2.4

**原问题**:
```
WHEN the token type is `api_key`, THE AuthModule SHALL additionally set `ANTHROPIC_API_KEY` for logging purposes.
```

**缺陷**: 如果 API Key 只是"额外设置用于日志"，而主要写入 `CLAUDE_CODE_OAUTH_TOKEN`，CLI 将无法正确认证。

**修正**:
- API Key 模式: 主要写入 `ANTHROPIC_API_KEY`（CLI 实际读取点）
- Proxy 模式: 主要写入 `ANTHROPIC_AUTH_TOKEN`（CLI 实际读取点）

---

### P3: Requirement 2 与 Requirement 7 逻辑冲突 (中等) ✅ 已修正

**位置**: requirements.md - Requirement 2 vs Requirement 7

**原问题**:
- Req 2: 统一写入 `CLAUDE_CODE_OAUTH_TOKEN`
- Req 7: SDK 环境变量传递列表包含 `ANTHROPIC_API_KEY`

**缺陷**: 如果统一写入 `CLAUDE_CODE_OAUTH_TOKEN`，传递 `ANTHROPIC_API_KEY` 无意义。

**修正**:
- Req 2 改为类型特定注入
- Req 7 添加 `CLAUDE_CODE_OAUTH_TOKEN` 到传递列表
- 两者逻辑一致

---

### P4: Property Test 使用 `"oat" not in token` 逻辑错误 (中等) ✅ 已修正

**位置**: design.md - Property Tests

**原问题**:
```python
elif token.startswith("sk-ant-api") or (token.startswith("sk-") and "oat" not in token):
    assert result == "api_key"
```

**缺陷**:
- `"oat" not in token` 会误判包含 "oat" 子串的 Token（如 `sk-myoatmeal-key`）
- 应该检查前缀，而非子串

**修正**:
```python
elif token.startswith("sk-ant-api"):
    assert result == "api_key"
elif token.startswith("sk-") and not token.startswith("sk-ant-oat"):
    assert result == "api_key"
```

---

### P5: Proxy 验证时机过晚 (中等) ✅ 已修正

**位置**: requirements.md - Requirement 4, tasks.md - Task 9

**原问题**: Proxy 配置验证仅在 ClientFactory 中进行（执行时）

**缺陷**: 用户可能在执行大量准备工作后才发现配置错误

**修正**:
- 主要验证: CLIValidator 中进行（早期失败）
- 二次验证: ClientFactory 中作为安全网
- 更新 Requirement 4 明确两层验证

---

### P6: Hypothesis 依赖未声明 (轻微) ✅ 已修正

**位置**: tasks.md

**原问题**: 属性测试使用 Hypothesis，但未在依赖项中声明

**修正**: 在 tasks.md Overview 中添加依赖项说明:
```
hypothesis>=6.0.0
```

---

### P7: Glossary 缺少 CLI 定义 (轻微) ✅ 已修正

**位置**: requirements.md - Glossary

**原问题**: 文档多次提到 CLI，但 Glossary 中无定义

**修正**: 添加 CLI 定义:
```
- **CLI**: Claude Code CLI，SDK 底层调用的命令行工具，实际处理认证
```

---

## 修正汇总

| ID | 严重度 | 文件 | 状态 |
|----|--------|------|------|
| P1 | 严重 | requirements.md, design.md | ✅ 已修正 |
| P2 | 严重 | requirements.md | ✅ 已修正 |
| P3 | 中等 | requirements.md | ✅ 已修正 |
| P4 | 中等 | design.md | ✅ 已修正 |
| P5 | 中等 | requirements.md, tasks.md | ✅ 已修正 |
| P6 | 轻微 | tasks.md | ✅ 已修正 |
| P7 | 轻微 | requirements.md | ✅ 已修正 |

---

## R_eff 计算（修正后）

| 维度 | 修正前 | 修正后 | 改进 |
|------|--------|--------|------|
| 逻辑一致性 | 0.40 | 0.95 | +0.55 |
| 完整性 | 0.70 | 0.92 | +0.22 |
| 可测试性 | 0.75 | 0.93 | +0.18 |
| EARS 合规性 | 0.85 | 0.95 | +0.10 |

**R_eff (修正前) = 0.40** (WLNK: 逻辑一致性 - 统一入口假设错误)
**R_eff (修正后) = 0.92**

---

## 关键改进

### 1. 修正核心认证机制

**修正前 (错误)**:
```
所有 Token → CLAUDE_CODE_OAUTH_TOKEN → SDK → CLI
```

**修正后 (正确)**:
```
OAuth Token  → CLAUDE_CODE_OAUTH_TOKEN → SDK → CLI reads CLAUDE_CODE_OAUTH_TOKEN
API Key      → ANTHROPIC_API_KEY       → SDK → CLI reads ANTHROPIC_API_KEY
Proxy Token  → ANTHROPIC_AUTH_TOKEN    → SDK → CLI reads ANTHROPIC_AUTH_TOKEN
```

### 2. 早期失败原则

- CLIValidator 在执行前验证 Proxy 配置
- 用户尽早得到错误反馈，避免浪费时间

### 3. Property Test 逻辑修正

- 使用 `not token.startswith("sk-ant-oat")` 替代 `"oat" not in token`
- 明确检查顺序：OAuth → `sk-ant-api` → generic `sk-`

### 4. 依赖项文档化

- Hypothesis 添加到测试依赖
- 便于新开发者快速上手

---

## 验证方法

### SDK/CLI 认证行为验证

通过 Context7 查询 `claude-agent-sdk-python` 和 Anthropic 文档确认:

1. **SDK 行为**: `ClaudeAgentOptions(env={...})` 将环境变量传递给 CLI 子进程
2. **CLI 行为**: 从类型特定环境变量读取认证
   - OAuth: `CLAUDE_CODE_OAUTH_TOKEN`
   - API Key: `ANTHROPIC_API_KEY`
   - Proxy: `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`

### 建议的实施验证

1. 实施后运行属性测试验证分类逻辑
2. 使用真实 Token 进行端到端测试
3. 验证现有 OAuth 用户不受影响

---

## 与方案2的关系

方案2（全功能UI改造）的后端部分与方案1一致。本次修正需要同步到方案2:

- [ ] 更新方案2 requirements.md 的后端部分
- [ ] 更新方案2 design.md 的后端架构图
- [ ] 更新方案2 tasks.md Phase 1

**建议**: 先完成方案1实施，验证后再同步到方案2。

---

## 历史记录

### 第一轮审查 (2025-12-30 早)

发现 8 个问题 (P1-P8)，主要是 EARS 格式和表述精确性问题。

### 第二轮审查 (2025-12-30 晚)

基于外部反馈，发现根本性设计缺陷：
- "统一入口"假设错误
- API Key/Proxy 认证会失败

**教训**: 第一轮审查未验证核心假设（SDK 只读取 `CLAUDE_CODE_OAUTH_TOKEN`），导致遗漏严重问题。FPF 审查应始终验证核心假设的正确性。
