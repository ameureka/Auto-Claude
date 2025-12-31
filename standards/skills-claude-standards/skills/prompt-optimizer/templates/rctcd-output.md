# R.C.T.C.D 输出模板

结构化提示词的标准输出格式。

---

## Role
{role_description}

## Context
{context_items}

## Task
**主任务**: {main_task}

**子任务**:
{subtasks}

## Constraints
{constraints}

## Deliverables
{deliverables}

---

### 转换说明

| 原始 | 推断 | 依据 |
|------|------|------|
{transformation_table}

**复杂度评估**: {complexity_level} ({complexity_score}/10)
{complexity_factors}

**建议约束说明**:
标记为 [建议] 的约束是系统推断的最佳实践，您可以根据实际需求保留或移除。

---

**请确认或选择操作**:

1. ✅ **确认使用** - 直接使用此提示词
2. ✏️ **调整内容** - 修改某些部分
3. 🔄 **重新生成** - 提供更多信息重新生成
