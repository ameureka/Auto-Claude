# Kiro Specs 方法论与标准

本目录包含 Kiro Specs 驱动开发的完整方法论、标准规范和参考示例。

## 目录结构

```
kiro-specs-标准/
├── README.md                    # 本文件 - 概述
├── 01-methodology.md            # 方法论详解
├── 02-requirements-standard.md  # 需求文档标准 (EARS + INCOSE)
├── 03-design-standard.md        # 设计文档标准
├── 04-tasks-standard.md         # 任务清单标准
├── 05-property-based-testing.md # 属性测试方法论
└── examples/                    # 参考示例
    ├── requirements-example.md
    ├── design-example.md
    └── tasks-example.md
```

## 核心理念

Kiro Specs 是一种**规范驱动开发 (Spec-Driven Development)** 方法论，通过三个阶段将模糊的想法转化为可执行的实现计划：

1. **Requirements (需求)** - 使用 EARS 模式和 INCOSE 质量规则定义清晰的需求
2. **Design (设计)** - 基于需求创建详细的技术设计，包含正确性属性
3. **Tasks (任务)** - 将设计转化为可执行的编码任务清单

## 关键特性

- **形式化正确性** - 通过属性测试 (Property-Based Testing) 验证软件正确性
- **迭代式开发** - 每个阶段都需要用户明确批准后才能进入下一阶段
- **可追溯性** - 从需求到设计到任务，每一步都有明确的引用关系
- **增量实现** - 任务按顺序执行，每个任务都建立在前一个任务的基础上

## 快速开始

1. 阅读 [方法论详解](./01-methodology.md) 了解整体流程
2. 学习 [需求文档标准](./02-requirements-standard.md) 掌握 EARS 模式
3. 参考 [设计文档标准](./03-design-standard.md) 理解正确性属性
4. 查看 [任务清单标准](./04-tasks-standard.md) 了解任务格式
5. 研究 [examples/](./examples/) 目录中的完整示例
