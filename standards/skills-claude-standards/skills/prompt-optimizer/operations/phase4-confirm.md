# Phase 4: Confirm - 确认阶段

让用户确认或调整生成的结构化提示词。

## 目标

- 展示生成结果供用户审核
- 收集用户反馈
- 支持迭代优化

## 确认流程

```
输出结果
    │
    ▼
┌─────────────────┐
│ 展示结构化提示词 │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 询问用户确认    │
└─────────────────┘
    │
    ├── 确认 ──────────▶ 完成
    │
    ├── 调整 ──────────▶ 收集修改意见
    │                         │
    │                         ▼
    │                   ┌─────────────┐
    │                   │ 重新生成    │
    │                   └─────────────┘
    │                         │
    │                         └──────▶ 返回展示
    │
    └── 重新开始 ──────▶ 返回 Phase 0
```

## 确认提示

### 标准确认提示

```markdown
---

以上是根据您的输入生成的结构化提示词。

**请确认或选择操作**:

1. ✅ **确认使用** - 直接使用此提示词
2. ✏️ **调整内容** - 修改某些部分
3. 🔄 **重新生成** - 提供更多信息重新生成

请输入选项编号或直接说明需要调整的内容。
```

### 快捷确认

如果用户输入简短确认词，直接完成：

| 用户输入 | 操作 |
|----------|------|
| 好、ok、确认、可以 | 确认使用 |
| 改、调整、修改 | 进入调整模式 |
| 重来、重新 | 重新开始 |

## 调整模式

### 支持的调整类型

| 调整类型 | 示例 | 处理方式 |
|----------|------|----------|
| 修改 Role | "角色改成架构师" | 更新 Role 部分 |
| 添加 Context | "补充：使用 TypeScript" | 追加 Context |
| 修改 Task | "主任务改成重构" | 更新 Task 部分 |
| 移除约束 | "移除第二个建议" | 删除指定约束 |
| 添加交付物 | "加上单元测试" | 追加 Deliverables |

### 调整处理逻辑

```python
def handle_adjustment(adjustment_input, current_output):
    """处理用户调整请求"""

    # 解析调整意图
    intent = parse_adjustment_intent(adjustment_input)

    if intent["type"] == "modify_role":
        current_output["role"] = intent["new_value"]

    elif intent["type"] == "add_context":
        current_output["context"].append(intent["new_value"])

    elif intent["type"] == "modify_task":
        if intent["target"] == "main":
            current_output["task"]["main"] = intent["new_value"]
        else:
            # 修改子任务
            pass

    elif intent["type"] == "remove_constraint":
        index = intent["index"]
        current_output["constraints"].pop(index)

    elif intent["type"] == "add_deliverable":
        current_output["deliverables"].append(intent["new_value"])

    return current_output
```

### 调整确认

调整后重新展示并确认：

```markdown
---

已根据您的反馈更新：

**变更内容**:
- [变更1描述]
- [变更2描述]

[更新后的完整输出]

请确认是否满意，或继续调整。
```

## 迭代优化

支持多轮调整，直到用户满意：

```
第1轮: 生成初始版本
    │
    ▼
用户: "角色改成架构师"
    │
    ▼
第2轮: 更新 Role
    │
    ▼
用户: "加上性能优化的约束"
    │
    ▼
第3轮: 添加 Constraint
    │
    ▼
用户: "好的"
    │
    ▼
完成 ✅
```

## 完成输出

确认后的最终输出：

```markdown
---

✅ **提示词已确认**

您可以直接复制以下内容使用：

```
[最终的结构化提示词]
```

**使用建议**:
- 将此提示词发送给 AI 助手
- 根据 AI 的回复，可以进一步细化需求
- 交付物清单可用于验收检查
```

## 会话记录

记录本次优化过程，便于后续参考：

```json
{
  "session_id": "po-20241231-001",
  "original_input": "用 React 写一个支持拖拽排序的列表",
  "iterations": [
    {
      "round": 1,
      "action": "generate",
      "output": "..."
    },
    {
      "round": 2,
      "action": "adjust",
      "adjustment": "角色改成架构师",
      "output": "..."
    }
  ],
  "final_output": "...",
  "confirmed_at": "2024-12-31T10:30:00Z"
}
```

## 检查清单

- [ ] 展示完整输出
- [ ] 提供确认选项
- [ ] 支持调整操作
- [ ] 支持多轮迭代
- [ ] 记录会话历史

## 完成

用户确认后，prompt-optimizer 流程结束。
