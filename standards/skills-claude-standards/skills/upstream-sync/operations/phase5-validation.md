# Phase 5: Validation (验证)

> **目标**: 验证合并结果正确性
> **输入**: Merge Commit
> **输出**: `validation-report.md`

---

## 操作步骤

### Step 5.1: 运行测试套件

```bash
# 后端测试
cd apps/backend
pytest tests/ -v

# 特定测试（如认证测试）
pytest tests/test_auth_properties.py -v
```

**预期结果**: 所有测试通过

### Step 5.2: 构建验证

```bash
# 前端构建
cd apps/frontend
pnpm build

# 后端语法检查（如有）
cd apps/backend
python -m py_compile core/auth.py core/client.py
```

**预期结果**: 构建成功，无错误

### Step 5.3: 核心功能检查

#### 多认证系统检查

```bash
# 检查 ANTHROPIC_API_KEY 支持
grep -n "ANTHROPIC_API_KEY" apps/backend/core/auth.py

# 预期输出应包含:
# - AUTH_TOKEN_ENV_VARS 中有 ANTHROPIC_API_KEY
# - SDK_ENV_VARS 中有 ANTHROPIC_API_KEY

# 检查认证函数
grep -n "apply_auth_env\|get_token_type\|validate_proxy_config" apps/backend/core/auth.py
```

#### i18n 中文支持检查

```bash
# 检查中文 locale 注册
grep -n "zh" apps/frontend/src/shared/i18n/index.ts

# 预期输出应包含:
# - import zhCommon from './locales/zh/common.json'
# - zh: { common: zhCommon, ... }

# 检查中文翻译文件存在
ls apps/frontend/src/shared/i18n/locales/zh/
```

#### 配置文件检查

```bash
# 检查 .env.example 包含多认证配置
grep -n "Method 1\|Method 2\|Method 3\|ANTHROPIC_API_KEY" apps/backend/.env.example
```

### Step 5.4: 上游新功能检查

验证上游新功能已正确合并：

```bash
# 示例：检查 --base-branch 参数
grep -n "base-branch\|base_branch" apps/backend/runners/spec_runner.py

# 示例：检查新增文件
ls apps/backend/runners/gitlab/  # 如果上游新增了 GitLab 集成
```

### Step 5.5: 回归测试

运行完整测试套件确保没有回归：

```bash
# 完整测试
cd apps/backend
pytest tests/ -v --tb=short

# 前端测试（如有）
cd apps/frontend
pnpm test
```

---

## 验证清单

### 必须通过 ✅

| 检查项 | 命令 | 预期结果 |
|--------|------|---------|
| 测试通过 | `pytest tests/ -v` | 全部 PASSED |
| 构建成功 | `pnpm build` | 无错误 |
| ANTHROPIC_API_KEY 存在 | `grep ANTHROPIC_API_KEY auth.py` | 找到匹配 |
| 中文 locale 注册 | `grep "zh" i18n/index.ts` | 找到匹配 |

### 建议检查 ⚠️

| 检查项 | 命令 | 说明 |
|--------|------|------|
| 上游新功能 | 根据上游提交检查 | 确保新功能可用 |
| 类型检查 | `pnpm typecheck` | TypeScript 类型正确 |
| Lint 检查 | `pnpm lint` | 代码风格正确 |

---

## 输出模板

生成 `validation-report.md`：

```markdown
# 合并验证报告

> **生成时间**: YYYY-MM-DD HH:MM
> **合并提交**: <commit-hash>

---

## 测试结果

### 后端测试

```
pytest tests/ -v
============================= test session starts ==============================
...
============================== X passed in Y.YYs ===============================
```

**状态**: ✅ 通过 / ❌ 失败

### 前端构建

```
pnpm build
...
✓ built in X.XXs
```

**状态**: ✅ 通过 / ❌ 失败

---

## 核心功能验证

### 多认证系统

| 检查项 | 结果 |
|--------|------|
| ANTHROPIC_API_KEY 在 AUTH_TOKEN_ENV_VARS | ✅ |
| ANTHROPIC_API_KEY 在 SDK_ENV_VARS | ✅ |
| apply_auth_env 函数存在 | ✅ |
| get_token_type 函数存在 | ✅ |
| validate_proxy_config 函数存在 | ✅ |

### i18n 中文支持

| 检查项 | 结果 |
|--------|------|
| 中文 locale 注册 | ✅ |
| common.json 存在 | ✅ |
| navigation.json 存在 | ✅ |
| settings.json 存在 | ✅ |
| tasks.json 存在 | ✅ |
| welcome.json 存在 | ✅ |
| onboarding.json 存在 | ✅ |
| dialogs.json 存在 | ✅ |
| taskReview.json 存在 | ✅ |

### 配置文件

| 检查项 | 结果 |
|--------|------|
| .env.example 包含 Method 1/2/3 | ✅ |

---

## 上游新功能

| 功能 | 来源提交 | 验证结果 |
|------|---------|---------|
| --base-branch 参数 | #428 | ✅ 存在 |
| GitLab 集成 | #254 | ✅ 文件存在 |
| ... | ... | ... |

---

## 验证结论

| 类别 | 状态 |
|------|------|
| 测试 | ✅ 全部通过 |
| 构建 | ✅ 成功 |
| 核心功能 | ✅ 保护完整 |
| 上游功能 | ✅ 正确合并 |

**总体结论**: ✅ 验证通过，可以进入 Phase 6 发布
```

---

## 故障排除

### 测试失败

1. 检查失败的测试用例
2. 确认是否遗漏了保护文件
3. 检查上游是否有破坏性更改
4. 查看测试日志定位问题

```bash
# 查看详细失败信息
pytest tests/test_xxx.py -v --tb=long
```

### 构建失败

1. 检查 TypeScript 类型错误
2. 检查缺失的依赖
3. 检查导入路径是否正确

```bash
# 查看详细错误
pnpm build 2>&1 | head -50
```

### 核心功能检查失败

如果关键代码不存在，说明保护策略执行有误：

```bash
# 回滚到合并前
git reset --hard HEAD~1

# 重新执行 Phase 4，确保正确保护文件
```

---

## 检查点

在进入 Phase 6 之前，确认：

- [ ] 所有测试通过
- [ ] 构建成功
- [ ] 核心功能验证通过
- [ ] 上游新功能正确合并
- [ ] `validation-report.md` 已生成
