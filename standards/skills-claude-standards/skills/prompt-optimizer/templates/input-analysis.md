# 输入分析模板

用于记录 Phase 1 解析阶段的分析结果。

## 基本信息

| 字段 | 值 |
|------|-----|
| 原始输入 | `{original_input}` |
| 输入长度 | {length} 字符 |
| 检测语言 | {language} |
| 分析时间 | {timestamp} |

## 关键词提取

### 技术关键词

| 关键词 | 类别 | 置信度 |
|--------|------|--------|
| {tech_keyword_1} | {category_1} | {confidence_1} |
| {tech_keyword_2} | {category_2} | {confidence_2} |

### 动作关键词

| 关键词 | 映射类型 |
|--------|----------|
| {action_1} | {type_1} |
| {action_2} | {type_2} |

### 对象关键词

| 关键词 | 说明 |
|--------|------|
| {object_1} | {desc_1} |
| {object_2} | {desc_2} |

## 技术栈识别

```yaml
primary: {primary_tech}
category: {tech_category}
related:
  - {related_tech_1}
  - {related_tech_2}
confidence: {tech_confidence}
```

## 任务分析

```yaml
type: {task_type}  # CREATE/UPDATE/FIX/REFACTOR/DELETE/TEST/DEPLOY/INTEGRATE
main_object: {main_object}
features:
  - {feature_1}
  - {feature_2}
```

## 复杂度评估

| 指标 | 值 | 权重 | 得分 |
|------|-----|------|------|
| 关键词数量 | {keyword_count} | 0.2 | {score_1} |
| 技术栈数量 | {tech_count} | 0.2 | {score_2} |
| 隐含子任务 | {subtask_count} | 0.3 | {score_3} |
| 涉及领域 | {domain_count} | 0.3 | {score_4} |
| **总计** | - | 1.0 | **{total_score}** |

**复杂度级别**: {complexity_level} ({total_score}/10)

## 隐含约束

| 约束内容 | 类型 | 来源 |
|----------|------|------|
| {constraint_1} | {type_1} | {source_1} |
| {constraint_2} | {type_2} | {source_2} |

## 解析状态

- [ ] 关键词提取完成
- [ ] 技术栈识别完成
- [ ] 任务类型确定
- [ ] 复杂度评估完成
- [ ] 隐含约束检测完成

## 备注

{notes}
