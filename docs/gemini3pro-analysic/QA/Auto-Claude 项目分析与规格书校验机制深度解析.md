# Auto-Claude 项目分析与规格书校验机制深度解析

**日期**: 2025-12-22
**分析对象**: Project Analysis & Spec Validation (`auto-claude/project/`, `auto-claude/spec/validate_pkg/`)

---

## 1. 核心理念：质量准入与结构化对齐

Auto-Claude 的工程成功秘诀之一在于其**“不盲目动工”**。在 Coder Agent 写下第一行代码前，系统必须通过多层探测和校验，确保 AI 对项目的理解与物理代码库完全对齐。

---

## 2. 项目全景探测器 (`FrameworkDetector`)

位于 `auto-claude/project/`，它是系统的“数字眼睛”。

### 2.1 跨语言识别能力
- **Node.js**: 识别从 React/Vue 到 NestJS/Express 的全技术栈，甚至包含 Biome/Oxlint 等新兴工具。
- **Python**: 识别 Django/FastAPI 等框架及 Pytest/Ruff 等工程化工具。
- **Ruby & PHP**: 支持基础的 Rails 和 Laravel 环境探测。

### 2.2 数据流向
`FrameworkDetector` -> `project_index.json` -> `Security/Context Engine`。
探测结果被持久化在索引中，作为整个蜂群运行的“基础常识”。

---

## 3. 规格书多维校验体系 (`SpecValidator`)

系统实现了一套严格的 Checkpoint 机制，确保 Spec 生成阶段产出的每一份文档都是高质量的。

| 校验阶段 | 目标文件 | 关键校验点 |
| :--- | :--- | :--- |
| **Prereqs** | 环境配置 | 检查 Token、API 路径及基础目录结构。 |
| **Context** | `context.json` | 确保 AI 已经“读过”了相关的模式文件（Pattern Files）。 |
| **Document**| `spec.md` | 验证文档的 Markdown 格式及核心章节完整性。 |
| **Plan** | `plan.json` | 校验 JSON Schema，重点检查 Subtask 是否具备验证逻辑。 |

---

## 4. 智能自愈：计划自动修复 (`Auto-Fix`)

这是 Auto-Claude 处理 AI 随机性的关键逻辑：
- **逻辑**: 如果 `Implementation Plan` JSON 格式合法但内容不全，`auto_fix_plan()` 函数会自动运行。
- **动作**:
    - 为缺失名字的子任务分配 `Unnamed Feature`。
    - 自动为没有 ID 的任务生成层级 ID（例如 `subtask-2-3`）。
    - 强制注入 `status: pending`。
- **意义**: 保证了即使 AI 产出的计划略有瑕疵，流水线依然能“带病坚持工作”，无需人类手动修改 JSON。

---

## 5. 对 AMEUREKA 协作的启示

1.  **扩展框架探测**: 可以新增 `detect_ameureka_framework` 方法，通过识别 `.kiro` 目录来激活特定的 AMEUREKA 开发模式。
2.  **强制 Spec 约束**: 在 `SpecDocumentValidator` 中加入 AMEUREKA 的“设计属性”必填项检查，如果不满足 EARS 模式要求的章节，强制打回重写。

---

## 6. 总结

Auto-Claude 的分析与校验模块构成了一个**“工程过滤器”**。它将模糊的自然语言需求，经过项目画像探测、Spec 结构化校验、Plan 自动补全三道工序，过滤并强化为 100% 确定性的工程指令。
