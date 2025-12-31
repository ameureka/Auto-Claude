# 澄清请求模板

当输入信息不足时，用于请求用户补充信息。

---

## 输入过短澄清

```markdown
⚠️ **输入信息较少，需要澄清**

您的输入: `{original_input}`

检测到的意图: {detected_intent}

为了生成更准确的结构化提示词，请补充以下信息：

1. **技术栈**: 使用什么编程语言或框架？
   - 例如: React, Python, Node.js 等

2. **任务性质**: 是新建还是修改现有功能？
   - 新建: 从零开始创建
   - 修改: 在现有代码基础上改动

3. **特殊要求**: 有什么约束或偏好？
   - 例如: 性能要求、兼容性、代码风格等

请补充信息后重新提交，或直接回复补充内容。
```

---

## 非编程任务澄清

```markdown
⚠️ **检测到非编程任务**

您的输入: `{original_input}`

prompt-optimizer 专为**编程/开发任务**设计。

检测到的任务类型: {detected_type}

**如果这确实是编程任务**，请补充技术相关的描述，例如：
- 使用的编程语言
- 涉及的框架或工具
- 具体的技术实现目标

**如果是其他类型任务**，建议：
- 写作任务 → 使用通用写作助手
- 翻译任务 → 使用翻译工具
- 问答任务 → 直接提问即可

请确认或补充信息。
```

---

## 模糊意图澄清

```markdown
⚠️ **任务意图不够明确**

您的输入: `{original_input}`

检测到多种可能的意图：

{possible_intents}

请选择或说明您的具体需求：

1. {intent_option_1}
2. {intent_option_2}
3. {intent_option_3}
4. 其他（请说明）

请输入选项编号或直接描述。
```

---

## 技术栈不明确澄清

```markdown
⚠️ **技术栈不明确**

您的输入: `{original_input}`

未能确定使用的技术栈。请选择或说明：

**前端**:
- [ ] React
- [ ] Vue
- [ ] Angular
- [ ] 原生 JavaScript/HTML/CSS

**后端**:
- [ ] Node.js
- [ ] Python (Django/Flask)
- [ ] Java (Spring)
- [ ] Go

**其他**:
- [ ] 移动端 (iOS/Android/React Native)
- [ ] 数据库操作
- [ ] DevOps/部署

请选择适用的技术栈，或直接说明。
```

---

## 复杂任务拆分建议

```markdown
⚠️ **任务较为复杂，建议拆分**

您的输入: `{original_input}`

检测到的复杂度: **{complexity_level}** ({complexity_score}/10)

涉及多个领域：
{complexity_factors}

**建议拆分为以下子任务**：

1. {suggested_subtask_1}
2. {suggested_subtask_2}
3. {suggested_subtask_3}

您可以：
- **继续处理**: 生成完整的结构化提示词（可能较长）
- **分别优化**: 对每个子任务单独生成提示词

请选择处理方式。
```

---

## 通用澄清模板

```markdown
⚠️ **需要更多信息**

您的输入: `{original_input}`

{clarification_reason}

请补充以下信息：

{questions}

或者，您可以：
- 提供更详细的描述
- 举一个具体的例子
- 说明期望的最终效果
```
