# Phase 3: Output - 输出阶段

将转换结果格式化为用户友好的 R.C.T.C.D 结构化提示词。

## 目标

生成清晰、可读、可直接使用的结构化提示词。

## 输出格式

### 标准输出模板

```markdown
## Role
[推断的角色描述]

## Context
- [上下文信息1]
- [上下文信息2]
- [上下文信息3]

## Task
**主任务**: [主任务描述]

**子任务**:
1. [子任务1]
2. [子任务2]
3. [子任务3]

## Constraints
- [显式约束]
- [建议] 建议约束1
- [建议] 建议约束2

## Deliverables
- [ ] 交付物1
- [ ] 交付物2
- [ ] 交付物3
```

## 格式化规则

### 1. Role 格式化

```python
def format_role(role_data):
    """格式化角色部分"""

    output = "## Role\n"
    output += role_data["title"]

    if role_data.get("expertise"):
        output += f"，精通 {role_data['expertise']}"

    return output
```

### 2. Context 格式化

```python
def format_context(context_list):
    """格式化上下文部分"""

    output = "## Context\n"

    for item in context_list:
        output += f"- {item}\n"

    return output
```

### 3. Task 格式化

```python
def format_task(task_data):
    """格式化任务部分"""

    output = "## Task\n"
    output += f"**主任务**: {task_data['main']}\n\n"

    if task_data.get("subtasks"):
        output += "**子任务**:\n"
        for i, subtask in enumerate(task_data["subtasks"], 1):
            output += f"{i}. {subtask}\n"

    return output
```

### 4. Constraints 格式化

```python
def format_constraints(constraints):
    """格式化约束部分"""

    output = "## Constraints\n"

    for c in constraints:
        if c["type"] == "explicit":
            output += f"- {c['content']}\n"
        elif c["type"] == "suggested":
            output += f"- [建议] {c['content']}\n"
        elif c["type"] == "required":
            output += f"- [必须] {c['content']}\n"

    return output
```

### 5. Deliverables 格式化

```python
def format_deliverables(deliverables):
    """格式化交付物部分"""

    output = "## Deliverables\n"

    for d in deliverables:
        if d.startswith("[ ]"):
            output += f"- {d}\n"
        else:
            output += f"- [ ] {d}\n"

    return output
```

## 转换说明生成

在输出结构化提示词后，附加转换说明帮助用户理解：

```markdown
---

### 转换说明

| 原始 | 推断 | 依据 |
|------|------|------|
| "写" | CREATE 类型 | 动作词映射 |
| "React" | 前端开发 | 技术栈识别 |
| "拖拽排序" | 交互功能 | 功能特征提取 |

**复杂度评估**: 中等
- 涉及拖拽交互实现
- 需要状态管理
- 可能需要第三方库

**建议约束说明**:
- 标记为 [建议] 的约束是系统推断的最佳实践
- 您可以根据实际需求保留或移除
```

## 输出流程

```
R.C.T.C.D 数据
      │
      ▼
┌─────────────────┐
│ 格式化 Role     │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ 格式化 Context  │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ 格式化 Task     │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ 格式化          │
│ Constraints     │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ 格式化          │
│ Deliverables    │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ 生成转换说明    │
└─────────────────┘
      │
      ▼
完整输出
```

## 完整输出示例

### 输入
```
用 React 写一个支持拖拽排序的列表
```

### 输出
```markdown
## Role
资深前端开发工程师，精通 React 和拖拽交互实现

## Context
- React 项目
- 需要实现列表项的拖拽排序功能
- 可能需要使用拖拽库（如 react-beautiful-dnd, dnd-kit）

## Task
**主任务**: 实现支持拖拽排序的列表组件

**子任务**:
1. 选择并集成拖拽库
2. 创建可拖拽的列表项组件
3. 实现拖拽排序逻辑
4. 处理排序后的状态更新
5. 添加拖拽视觉反馈

## Constraints
- [建议] 使用成熟的拖拽库而非原生实现
- [建议] 确保移动端触摸支持
- [建议] 考虑无障碍访问（键盘操作）

## Deliverables
- [ ] DraggableList 组件
- [ ] DraggableItem 子组件
- [ ] 排序状态管理 hook
- [ ] 使用示例和文档

---

### 转换说明

| 原始 | 推断 | 依据 |
|------|------|------|
| "写" | CREATE 类型 | 动作词映射 |
| "React" | 前端开发 | 技术栈识别 |
| "拖拽排序" | 交互功能 | 功能特征提取 |
| "列表" | 组件类型 | 对象识别 |

**复杂度评估**: 中等 (5/10)
- 涉及拖拽交互实现
- 需要状态管理
- 可能需要第三方库

**建议约束说明**:
标记为 [建议] 的约束是系统推断的最佳实践，您可以根据实际需求保留或移除。
```

## 检查清单

- [ ] 五个部分完整输出
- [ ] 格式正确（Markdown）
- [ ] 约束标记清晰
- [ ] 交付物可勾选
- [ ] 转换说明清晰

## 下一步

输出完成后，进入 [Phase 4: Confirm](./phase4-confirm.md)
