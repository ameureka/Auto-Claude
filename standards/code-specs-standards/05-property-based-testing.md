# 属性测试 (Property-Based Testing) 方法论

## 概述

属性测试 (PBT) 是一种强大的软件正确性验证方法。与传统的示例测试不同，属性测试验证的是**对所有有效输入都应该成立的属性**。

## 核心概念

### 什么是属性？

属性是一个关于系统行为的**全称量化声明**：

> "对于所有有效输入 X，系统行为 Y 应该成立"

### 属性 vs 示例

| 示例测试 | 属性测试 |
|----------|----------|
| 测试特定输入 | 测试所有输入 |
| `add(2, 3) === 5` | `∀a,b: add(a, b) === add(b, a)` |
| 手动选择边界 | 自动发现边界 |
| 覆盖已知情况 | 发现未知情况 |

## 七种常见属性模式

### 1. 不变量 (Invariants)

操作后保持不变的属性。

**适用场景**: 集合操作、数据转换、树结构

```typescript
// 属性: map 操作保持集合大小
test.prop([fc.array(fc.integer())])('map preserves length', (arr) => {
  const mapped = arr.map(x => x * 2);
  expect(mapped.length).toBe(arr.length);
});
```

**常见不变量**:
- 集合大小
- 排序后的内容
- 树的平衡性
- 对象的约束 (`start <= end`)

### 2. 往返属性 (Round-trip)

操作与逆操作组合返回原值。

**适用场景**: 序列化/反序列化、编码/解码、解析/打印

```typescript
// 属性: JSON 往返
test.prop([fc.jsonValue()])('JSON round trip', (value) => {
  const serialized = JSON.stringify(value);
  const deserialized = JSON.parse(serialized);
  expect(deserialized).toEqual(value);
});
```

**重要**: 所有解析器和序列化器**必须**有往返属性测试。

### 3. 幂等性 (Idempotence)

多次执行等于执行一次：`f(x) === f(f(x))`

**适用场景**: 去重、格式化、数据库更新、消息处理

```typescript
// 属性: 去重是幂等的
test.prop([fc.array(fc.integer())])('distinct is idempotent', (arr) => {
  const once = distinct(arr);
  const twice = distinct(distinct(arr));
  expect(twice).toEqual(once);
});
```

### 4. 变形属性 (Metamorphic)

已知的输入输出关系，不需要知道具体结果。

**适用场景**: 过滤、搜索、排序

```typescript
// 属性: 过滤减少或保持长度
test.prop([fc.array(fc.integer()), fc.func(fc.boolean())])
('filter reduces length', (arr, predicate) => {
  const filtered = arr.filter(predicate);
  expect(filtered.length).toBeLessThanOrEqual(arr.length);
});
```

### 5. 模型测试 (Model-based)

优化实现 vs 简单参考实现。

**适用场景**: 算法优化、缓存、复杂数据结构

```typescript
// 属性: 优化排序与标准排序结果相同
test.prop([fc.array(fc.integer())])('optimized sort matches reference', (arr) => {
  const optimized = quickSort([...arr]);
  const reference = [...arr].sort((a, b) => a - b);
  expect(optimized).toEqual(reference);
});
```

### 6. 合流性 (Confluence)

操作顺序不影响最终结果。

**适用场景**: 并发操作、CRDT、事件处理

```typescript
// 属性: 集合操作顺序无关
test.prop([fc.set(fc.integer()), fc.integer(), fc.integer()])
('set operations commute', (set, a, b) => {
  const order1 = new Set(set).add(a).add(b);
  const order2 = new Set(set).add(b).add(a);
  expect(order1).toEqual(order2);
});
```

### 7. 错误条件 (Error Conditions)

错误输入产生正确的错误响应。

**适用场景**: 输入验证、边界检查、错误处理

```typescript
// 属性: 空白字符串被拒绝
test.prop([fc.stringOf(fc.constantFrom(' ', '\t', '\n'))])
('whitespace-only strings are rejected', (whitespace) => {
  expect(() => createTask(whitespace)).toThrow();
});
```

## 生成器设计

### 智能约束

不要生成所有可能的输入，而是约束到有意义的输入空间：

```typescript
// 差: 生成任意字符串
fc.string()

// 好: 生成有效的电子邮件格式
fc.emailAddress()

// 好: 生成符合业务规则的数据
fc.record({
  name: fc.string({ minLength: 1, maxLength: 100 }),
  age: fc.integer({ min: 0, max: 150 }),
  email: fc.emailAddress()
})
```

### 边界情况覆盖

确保生成器覆盖边界情况：

```typescript
// 包含空数组、单元素、大数组
fc.array(fc.integer(), { minLength: 0, maxLength: 1000 })

// 包含空字符串、单字符、长字符串
fc.string({ minLength: 0, maxLength: 10000 })

// 包含负数、零、正数
fc.integer({ min: -1000000, max: 1000000 })
```

## 测试配置

### 迭代次数

每个属性测试**应该**运行至少 100 次迭代：

```typescript
// fast-check 配置
fc.assert(
  fc.property(fc.integer(), (n) => {
    // 属性检查
  }),
  { numRuns: 100 }
);
```

### 种子和重现

保存失败的种子以便重现：

```typescript
// 使用固定种子重现失败
fc.assert(property, { seed: 12345 });
```

## 属性测试标注

每个属性测试**必须**标注对应的正确性属性：

```typescript
/**
 * **Feature: user-auth, Property 1: Password hashing is consistent**
 * **Validates: Requirements 2.3**
 */
test.prop([fc.string({ minLength: 8 })])
('password hashing produces verifiable hashes', (password) => {
  const hash = hashPassword(password);
  expect(verifyPassword(password, hash)).toBe(true);
});
```

## 常见框架

### TypeScript/JavaScript: fast-check

```typescript
import fc from 'fast-check';

test.prop([fc.integer(), fc.integer()])('addition is commutative', (a, b) => {
  expect(a + b).toBe(b + a);
});
```

### Python: Hypothesis

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a
```

### Rust: proptest

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn addition_commutative(a: i32, b: i32) {
        prop_assert_eq!(a.wrapping_add(b), b.wrapping_add(a));
    }
}
```

## 调试失败的属性测试

### 1. 检查收缩后的反例

属性测试库会自动收缩失败的输入到最小反例：

```
Property failed after 42 tests.
Counterexample: [0, -1]
Shrunk from: [123456, -789012]
```

### 2. 分析反例

- 这是有效输入吗？→ 可能需要调整生成器
- 属性正确吗？→ 可能需要修正属性
- 代码有 bug 吗？→ 修复代码

### 3. 添加回归测试

将发现的反例添加为单元测试：

```typescript
test('regression: handles zero and negative', () => {
  expect(myFunction(0, -1)).toBe(expectedResult);
});
```

## 属性测试 vs 单元测试

两者是**互补**的，不是替代关系：

| 单元测试 | 属性测试 |
|----------|----------|
| 验证特定示例 | 验证通用属性 |
| 捕获具体 bug | 发现未知 bug |
| 文档化预期行为 | 验证形式化规范 |
| 快速执行 | 需要更多时间 |

**最佳实践**: 两者都写！

## 检查清单

编写属性测试时，确认：

- [ ] 属性包含全称量化 ("对于所有...")
- [ ] 生成器约束到有意义的输入空间
- [ ] 生成器覆盖边界情况
- [ ] 配置足够的迭代次数 (≥100)
- [ ] 标注对应的正确性属性和需求
- [ ] 解析器/序列化器有往返测试
- [ ] 失败的反例被分析和处理
