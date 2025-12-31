# Phase 2: Transform - 转换阶段

将解析结果转换为 R.C.T.C.D 结构化格式。

## 目标

基于 Phase 1 的解析结果，生成完整的 R.C.T.C.D 五要素。

## 转换规则

### R - Role (角色)

#### 推断逻辑

```python
def infer_role(parse_result):
    """根据解析结果推断角色"""

    tech_stack = parse_result["tech_stack"]["primary"]
    category = parse_result["tech_stack"]["category"]
    task_type = parse_result["task"]["type"]

    # 基于技术栈类别
    role_map = {
        "frontend": "资深前端开发工程师",
        "backend": "资深后端开发工程师",
        "fullstack": "资深全栈开发工程师",
        "mobile": "资深移动端开发工程师",
        "devops": "资深 DevOps 工程师",
        "database": "资深数据库工程师",
        "security": "资深安全工程师",
        "data": "资深数据工程师",
        "ml": "资深机器学习工程师"
    }

    base_role = role_map.get(category, "资深软件开发工程师")

    # 添加专业修饰
    if task_type == "REFACTOR":
        base_role = "资深软件架构师"

    # 添加技术栈专长
    if tech_stack:
        base_role += f"，精通 {tech_stack.title()}"

    return base_role
```

#### Role 推断表

| 技术栈/场景 | 推断角色 |
|-------------|----------|
| React/Vue/Angular | 资深前端开发工程师，精通 [框架] |
| Node.js/Express | 资深后端开发工程师，精通 Node.js |
| Python/Django/Flask | 资深后端开发工程师，精通 Python |
| 数据库/SQL | 资深数据库工程师 |
| Docker/K8s/CI/CD | 资深 DevOps 工程师 |
| 认证/加密/安全 | 资深安全工程师 |
| 重构/架构设计 | 资深软件架构师 |
| 测试/QA | 资深测试工程师 |
| 默认 | 资深软件开发工程师 |

---

### C - Context (上下文)

#### 提取规则

```python
def build_context(parse_result, project_info=None):
    """构建上下文信息"""

    context = []

    # 1. 技术栈上下文
    tech = parse_result["tech_stack"]
    if tech["primary"]:
        context.append(f"技术栈: {tech['primary'].title()}")
        if tech["related"]:
            context.append(f"相关技术: {', '.join(tech['related'])}")

    # 2. 任务上下文
    task = parse_result["task"]
    if task["type"] == "CREATE":
        context.append("需要创建新的功能/组件")
    elif task["type"] == "UPDATE":
        context.append("需要修改现有功能")
    elif task["type"] == "FIX":
        context.append("需要修复已知问题")
    elif task["type"] == "REFACTOR":
        context.append("需要重构现有代码")

    # 3. 项目上下文（如果有）
    if project_info:
        context.append(f"项目类型: {project_info['type']}")
        context.append(f"项目环境: {project_info['env']}")

    # 4. 复杂度上下文
    complexity = parse_result["complexity"]
    if complexity["factors"]:
        context.append(f"涉及: {', '.join(complexity['factors'])}")

    return context
```

#### Context 模板

```markdown
## Context
- 技术栈: [主要技术]
- 相关技术: [相关技术列表]
- 任务性质: [新建/修改/修复/重构]
- 涉及领域: [涉及的技术领域]
- [其他相关背景信息]
```

---

### T - Task (任务)

#### 分解规则

```python
def decompose_task(parse_result):
    """分解任务为主任务和子任务"""

    main_task = parse_result["task"]["main_object"]
    features = parse_result["task"]["features"]
    task_type = parse_result["task"]["type"]
    complexity = parse_result["complexity"]["level"]

    # 主任务描述
    action_map = {
        "CREATE": "创建",
        "UPDATE": "修改",
        "FIX": "修复",
        "REFACTOR": "重构",
        "DELETE": "删除",
        "TEST": "测试",
        "DEPLOY": "部署",
        "INTEGRATE": "集成"
    }

    main = f"{action_map[task_type]}{main_task}"

    # 子任务生成
    subtasks = generate_subtasks(main_task, features, task_type, complexity)

    return {
        "main": main,
        "subtasks": subtasks
    }

def generate_subtasks(main_task, features, task_type, complexity):
    """生成子任务列表"""

    subtasks = []

    # 基础子任务（根据任务类型）
    if task_type == "CREATE":
        subtasks.append(f"设计 {main_task} 的结构和接口")
        subtasks.append(f"实现 {main_task} 的核心逻辑")
    elif task_type == "REFACTOR":
        subtasks.append(f"分析现有 {main_task} 的架构")
        subtasks.append(f"设计新的 {main_task} 架构")
        subtasks.append(f"逐步迁移到新架构")

    # 功能相关子任务
    for feature in features:
        subtasks.append(f"实现 {feature} 功能")

    # 通用子任务
    if complexity in ["medium", "complex"]:
        subtasks.append("添加错误处理")
        subtasks.append("编写测试用例")

    return subtasks
```

#### Task 模板

```markdown
## Task
**主任务**: [动作][对象]

**子任务**:
1. [子任务1]
2. [子任务2]
3. [子任务3]
...
```

---

### C - Constraints (约束)

#### 约束分类

| 类型 | 标记 | 说明 |
|------|------|------|
| 显式约束 | (无标记) | 用户明确指定的约束 |
| 建议约束 | [建议] | 系统推断的约束，用户可选 |
| 强制约束 | [必须] | 安全/规范相关的强制约束 |

#### 约束生成规则

```python
def generate_constraints(parse_result):
    """生成约束条件"""

    constraints = []

    # 1. 提取显式约束（用户输入中的）
    explicit = extract_explicit_constraints(parse_result["original_input"])
    constraints.extend(explicit)

    # 2. 添加建议约束（基于技术栈）
    tech_constraints = get_tech_constraints(parse_result["tech_stack"])
    for c in tech_constraints:
        constraints.append({"type": "suggested", "content": c})

    # 3. 添加安全约束（基于任务类型）
    if involves_security(parse_result):
        constraints.append({
            "type": "required",
            "content": "遵循 OWASP 安全最佳实践"
        })

    # 4. 添加通用约束
    constraints.append({
        "type": "suggested",
        "content": "遵循现有代码风格和规范"
    })

    return constraints
```

#### Constraints 模板

```markdown
## Constraints
- [显式约束1]
- [显式约束2]
- [建议] 建议约束1
- [建议] 建议约束2
- [必须] 强制约束（如有）
```

---

### D - Deliverables (交付物)

#### 交付物生成规则

```python
def generate_deliverables(parse_result, task):
    """生成交付物清单"""

    deliverables = []
    task_type = parse_result["task"]["type"]
    main_object = parse_result["task"]["main_object"]

    # 基于任务类型的交付物
    if task_type == "CREATE":
        deliverables.append(f"{main_object} 实现代码")
        deliverables.append(f"{main_object} 相关样式/配置")
    elif task_type == "REFACTOR":
        deliverables.append("重构后的代码")
        deliverables.append("迁移文档")
    elif task_type == "FIX":
        deliverables.append("修复后的代码")
        deliverables.append("问题根因分析")

    # 基于复杂度的交付物
    if parse_result["complexity"]["level"] in ["medium", "complex"]:
        deliverables.append("单元测试")
        deliverables.append("使用文档/示例")

    # 格式化为 checkbox
    return [f"[ ] {d}" for d in deliverables]
```

#### Deliverables 模板

```markdown
## Deliverables
- [ ] 交付物1
- [ ] 交付物2
- [ ] 交付物3
...
```

## 转换流程

```
解析结果
    │
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Role    │  │ Context │  │ Task    │  │Constrai-│
│ 推断    │  │ 构建    │  │ 分解    │  │nts 生成 │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
    │              │            │            │
    └──────────────┴────────────┴────────────┘
                        │
                        ▼
                ┌─────────────┐
                │ Deliverables│
                │ 生成        │
                └─────────────┘
                        │
                        ▼
                R.C.T.C.D 结构
```

## 输出格式

```json
{
  "role": "资深前端开发工程师，精通 React 和拖拽交互实现",
  "context": [
    "React 项目",
    "需要实现列表项的拖拽排序功能",
    "可能需要使用拖拽库"
  ],
  "task": {
    "main": "实现支持拖拽排序的列表组件",
    "subtasks": [
      "选择并集成拖拽库",
      "创建可拖拽的列表项组件",
      "实现拖拽排序逻辑",
      "处理排序后的状态更新",
      "添加拖拽视觉反馈"
    ]
  },
  "constraints": [
    {"type": "suggested", "content": "使用成熟的拖拽库而非原生实现"},
    {"type": "suggested", "content": "确保移动端触摸支持"},
    {"type": "suggested", "content": "考虑无障碍访问"}
  ],
  "deliverables": [
    "[ ] DraggableList 组件",
    "[ ] DraggableItem 子组件",
    "[ ] 排序状态管理 hook",
    "[ ] 使用示例和文档"
  ]
}
```

## 检查清单

- [ ] Role 推断合理
- [ ] Context 信息完整
- [ ] Task 分解清晰
- [ ] Constraints 标记正确（显式/建议/必须）
- [ ] Deliverables 可验证

## 下一步

转换完成后，进入 [Phase 3: Output](./phase3-output.md)
