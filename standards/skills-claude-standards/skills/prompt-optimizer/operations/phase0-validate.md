# Phase 0: Validate - 输入验证

在解析和转换之前，验证输入的有效性。

## 目标

确保输入满足处理要求，对无效输入提供友好的错误提示和引导。

## 验证规则

### 1. 非空检查

```python
if not input or input.strip() == "":
    return Error("输入不能为空")
```

### 2. 长度检查

```python
MIN_LENGTH = 3
MAX_LENGTH = 2000

length = len(input.strip())

if length < MIN_LENGTH:
    return Error("输入过短，无法推断任务意图")

if length > MAX_LENGTH:
    return Error("输入超过 2000 字符限制")
```

### 3. 极短输入检测

```python
SHORT_THRESHOLD = 10

if length < SHORT_THRESHOLD:
    return Clarification("输入信息较少，需要澄清")
```

### 4. 任务意图检测

```python
# 检测是否包含动作词
action_keywords = [
    "写", "创建", "实现", "添加", "修改", "修复", "重构", "优化",
    "删除", "移除", "更新", "升级", "集成", "部署", "测试",
    "write", "create", "implement", "add", "modify", "fix", "refactor",
    "optimize", "delete", "remove", "update", "upgrade", "integrate",
    "deploy", "test", "build", "design"
]

has_action = any(keyword in input.lower() for keyword in action_keywords)

if not has_action:
    # 可能是问答类请求
    return Warning("未检测到明确的任务动作")
```

### 5. 编程相关性检测

```python
# 技术关键词
tech_keywords = [
    # 语言
    "python", "javascript", "typescript", "java", "go", "rust", "c++",
    # 框架
    "react", "vue", "angular", "next", "node", "django", "flask", "spring",
    # 概念
    "api", "数据库", "前端", "后端", "组件", "函数", "类", "接口",
    "功能", "模块", "页面", "服务", "代码", "程序"
]

is_programming = any(keyword in input.lower() for keyword in tech_keywords)

if not is_programming:
    return Warning("检测到非编程任务")
```

## 验证流程

```
输入
  │
  ▼
┌─────────────┐
│ 非空检查    │──── 空 ────▶ 错误: 输入不能为空
└─────────────┘
  │ 非空
  ▼
┌─────────────┐
│ 长度检查    │──── <3 ────▶ 错误: 输入过短
└─────────────┘
  │            └── >2000 ──▶ 错误: 输入过长
  │ 3-2000
  ▼
┌─────────────┐
│ 极短检测    │──── <10 ───▶ 澄清: 请补充信息
└─────────────┘
  │ ≥10
  ▼
┌─────────────┐
│ 意图检测    │──── 无动作 ─▶ 警告: 可能是问答
└─────────────┘
  │ 有动作
  ▼
┌─────────────┐
│ 相关性检测  │──── 非编程 ─▶ 警告: 非编程任务
└─────────────┘
  │ 编程相关
  ▼
验证通过 ✅
```

## 输出格式

### 验证通过

```json
{
  "status": "valid",
  "input": "原始输入",
  "normalized": "规范化后的输入",
  "length": 42,
  "detected": {
    "has_action": true,
    "is_programming": true,
    "language": "zh"
  }
}
```

### 验证失败

```json
{
  "status": "error",
  "code": "INPUT_TOO_SHORT",
  "message": "输入过短，无法推断任务意图",
  "suggestion": "请提供更详细的描述..."
}
```

### 需要澄清

```json
{
  "status": "clarification",
  "code": "INPUT_NEEDS_CLARIFICATION",
  "detected_intent": "推断的意图",
  "questions": [
    "使用什么技术栈？",
    "是新建还是修改现有功能？",
    "有什么特殊要求？"
  ]
}
```

### 警告（可继续）

```json
{
  "status": "warning",
  "code": "NON_PROGRAMMING_TASK",
  "message": "检测到非编程任务",
  "can_continue": true,
  "suggestion": "如果这确实是编程任务，请补充技术相关的描述"
}
```

## 检查清单

- [ ] 输入非空
- [ ] 长度在 3-2000 字符范围内
- [ ] 长度 ≥ 10 字符（或已完成澄清）
- [ ] 包含任务动作词
- [ ] 与编程相关

## 下一步

验证通过后，进入 [Phase 1: Parse](./phase1-parse.md)
