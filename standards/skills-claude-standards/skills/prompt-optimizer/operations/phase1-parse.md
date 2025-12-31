# Phase 1: Parse - 解析阶段

从原始输入中提取关键信息，为转换阶段做准备。

## 目标

识别和提取输入中的：
- 关键词和意图
- 技术栈线索
- 隐含约束条件
- 任务类型

## 解析步骤

### 1. 分词和关键词提取

```python
def extract_keywords(input_text):
    """提取关键词"""

    # 技术关键词
    tech_keywords = extract_tech_keywords(input_text)

    # 动作关键词
    action_keywords = extract_action_keywords(input_text)

    # 对象关键词（要做什么）
    object_keywords = extract_object_keywords(input_text)

    return {
        "tech": tech_keywords,
        "action": action_keywords,
        "object": object_keywords
    }
```

### 2. 技术栈识别

| 类别 | 关键词 | 推断技术栈 |
|------|--------|------------|
| 前端框架 | react, vue, angular, svelte | 前端开发 |
| 后端框架 | express, django, flask, spring | 后端开发 |
| 语言 | python, javascript, typescript, java | 对应语言 |
| 数据库 | mysql, postgres, mongodb, redis | 数据库操作 |
| 移动端 | ios, android, react native, flutter | 移动开发 |
| DevOps | docker, k8s, ci/cd, jenkins | 运维部署 |

### 3. 任务类型分类

| 动作词 | 任务类型 |
|--------|----------|
| 写、创建、实现、添加 | CREATE (新建) |
| 修改、更新、调整 | UPDATE (修改) |
| 修复、解决、处理 | FIX (修复) |
| 重构、优化、改进 | REFACTOR (重构) |
| 删除、移除、清理 | DELETE (删除) |
| 测试、验证、检查 | TEST (测试) |
| 部署、发布、上线 | DEPLOY (部署) |
| 集成、对接、连接 | INTEGRATE (集成) |

### 4. 隐含约束检测

```python
def detect_implicit_constraints(input_text, tech_stack):
    """检测隐含约束"""

    constraints = []

    # 基于技术栈的约束
    if "react" in tech_stack:
        constraints.append({
            "type": "suggested",
            "content": "遵循 React 最佳实践和 Hooks 规范"
        })

    # 基于任务类型的约束
    if "认证" in input_text or "登录" in input_text:
        constraints.append({
            "type": "suggested",
            "content": "遵循 OWASP 安全最佳实践"
        })

    # 基于关键词的约束
    if "api" in input_text.lower():
        constraints.append({
            "type": "suggested",
            "content": "保持 RESTful 设计原则"
        })

    return constraints
```

### 5. 复杂度评估

| 指标 | 简单 | 中等 | 复杂 |
|------|------|------|------|
| 关键词数量 | 1-3 | 4-7 | 8+ |
| 技术栈数量 | 1 | 2-3 | 4+ |
| 隐含子任务 | 1-2 | 3-5 | 6+ |
| 涉及领域 | 单一 | 跨2个 | 跨3个+ |

## 解析流程

```
输入文本
    │
    ▼
┌─────────────────┐
│ 1. 分词处理     │
│    - 中文分词   │
│    - 英文分词   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 关键词提取   │
│    - 技术词     │
│    - 动作词     │
│    - 对象词     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 技术栈识别   │
│    - 语言       │
│    - 框架       │
│    - 工具       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 任务分类     │
│    - 类型       │
│    - 复杂度     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 5. 约束检测     │
│    - 显式约束   │
│    - 隐含约束   │
└─────────────────┘
    │
    ▼
解析结果
```

## 输出格式

```json
{
  "original_input": "用 React 写一个支持拖拽排序的列表",
  "keywords": {
    "tech": ["react"],
    "action": ["写"],
    "object": ["列表", "拖拽排序"]
  },
  "tech_stack": {
    "primary": "react",
    "category": "frontend",
    "related": ["javascript", "css"]
  },
  "task": {
    "type": "CREATE",
    "main_object": "列表组件",
    "features": ["拖拽", "排序"]
  },
  "complexity": {
    "level": "medium",
    "score": 5,
    "factors": ["拖拽交互", "状态管理"]
  },
  "implicit_constraints": [
    {
      "type": "suggested",
      "content": "遵循 React 最佳实践和 Hooks 规范"
    },
    {
      "type": "suggested",
      "content": "考虑移动端触摸支持"
    }
  ]
}
```

## 特殊情况处理

### 多技术栈

当检测到多个技术栈时，按以下优先级确定主技术栈：
1. 显式指定的（"用 React"）
2. 最具体的（"Next.js" > "React" > "JavaScript"）
3. 出现在前面的

### 模糊意图

当动作词不明确时：
- "搞一个" → CREATE
- "弄一下" → UPDATE (如果有现有对象) / CREATE (如果是新对象)
- "处理" → 根据上下文判断

### 中英文混合

支持中英文混合输入，分别处理后合并结果。

## 检查清单

- [ ] 成功提取关键词
- [ ] 识别技术栈
- [ ] 确定任务类型
- [ ] 评估复杂度
- [ ] 检测隐含约束

## 下一步

解析完成后，进入 [Phase 2: Transform](./phase2-transform.md)
