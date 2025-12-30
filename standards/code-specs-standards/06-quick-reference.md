# Kiro Specs 快速参考卡片

## 文件结构

```
.kiro/specs/{feature-name}/
├── requirements.md    # 需求文档
├── design.md          # 设计文档
└── tasks.md           # 任务清单
```

## EARS 模式速查

| 模式 | 语法 | 用途 |
|------|------|------|
| 普遍型 | `THE <system> SHALL <response>` | 始终成立 |
| 事件驱动 | `WHEN <trigger>, THE <system> SHALL <response>` | 事件触发 |
| 状态驱动 | `WHILE <condition>, THE <system> SHALL <response>` | 状态期间 |
| 异常事件 | `IF <condition>, THEN THE <system> SHALL <response>` | 错误处理 |
| 可选功能 | `WHERE <option>, THE <system> SHALL <response>` | 可配置 |
| 复合型 | `[WHERE] [WHILE] [WHEN/IF] THE <system> SHALL <response>` | 多条件 |

## INCOSE 规则速查

### ✅ 必须
- 主动语态
- 单一思想
- 明确可测量条件
- 定义术语
- 一致术语

### ❌ 禁止
- 模糊词 (quickly, adequate)
- 逃避条款 (where possible)
- 否定陈述 (SHALL NOT)
- 代词 (it, them)
- 绝对词 (never, always)

## 属性模式速查

| 模式 | 公式 | 示例 |
|------|------|------|
| 不变量 | `f(x).property === x.property` | 长度保持 |
| 往返 | `decode(encode(x)) === x` | 序列化 |
| 幂等 | `f(f(x)) === f(x)` | 去重 |
| 变形 | `len(filter(x)) <= len(x)` | 过滤 |
| 合流 | `f(g(x)) === g(f(x))` | 顺序无关 |

## 属性格式

```markdown
**Property N: 属性名称**

*For any* [输入描述], [属性声明]

**Validates: Requirements X.Y**
```

## 任务格式

```markdown
- [ ] 1. 顶级任务
- [ ] 1.1 子任务
  - 详情
  - _Requirements: X.Y_
- [ ]* 1.2 可选测试任务
  - **Property N: 属性名称**
  - **Validates: Requirements X.Y**
```

## 工作流程

```
需求 → 审批 → 设计 → 审批 → 任务 → 审批 → 执行
```

## 属性测试框架

| 语言 | 框架 |
|------|------|
| TypeScript | fast-check |
| Python | Hypothesis |
| Rust | proptest |
| Java | jqwik |

## 关键检查点

### 需求文档
- [ ] EARS 模式
- [ ] INCOSE 规则
- [ ] 术语表
- [ ] 解析器有往返标准

### 设计文档
- [ ] Prework 分析
- [ ] 属性反思
- [ ] "For any" 声明
- [ ] 需求引用
- [ ] 测试框架指定

### 任务清单
- [ ] 两级层级
- [ ] 只有子任务可选
- [ ] 属性紧跟实现
- [ ] 需求引用
- [ ] Checkpoint
