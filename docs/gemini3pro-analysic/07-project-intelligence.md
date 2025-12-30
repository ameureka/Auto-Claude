# 07. 项目智能与深度分析引擎 (Project Intelligence)

## 1. 概述
Auto-Claude 的核心优势不仅在于执行代码，更在于其对复杂工程的**深度理解能力**。系统通过结合“确定性静态分析”与“概率性 AI 语义分析”，构建了一套完整的项目情报体系。

## 2. 静态分析层 (`Project Analyzer`)

位于 `apps/backend/project/`，它是系统的“数字雷达”。

### 2.1 技术栈自动探测 (`FrameworkDetector`)
- **原理**: 扫描 `package.json`, `pyproject.toml`, `Gemfile` 等 10+ 种依赖文件。
- **深度**: 能够识别从 Web 框架（Next.js, FastAPI）到测试工具（Vitest, Pytest）乃至 ORM（Drizzle, Prisma）的每一个细节。
- **作用**: 探测结果直接映射到 `SecurityProfile`，决定了哪些 shell 命令是“合法”的。

### 2.2 结构化索引 (`project_index.json`)
- **功能**: 生成项目的“数字孪生”地图。
- **内容**: 包含服务列表、入口点、API 路由映射及数据库模型摘要。
- **优化**: 具备智能缓存（Hash-based），仅在依赖文件变动时重构。

## 3. AI 辅助分析层 (`AI Analyzer`)

位于 `runners/ai_analyzer/`，这是系统进行架构级决策的基础。

### 3.1 模块化分析插件
系统通过 `AnalyzerFactory` 调度多个专用的 AI 分析器：
- **Code Relationships**: 追踪复杂的跨服务调用链路。
- **Business Logic**: 识别核心业务流程（如支付、注册）。
- **Architecture**: 评估代码是否符合 SOLID 原则或特定的设计模式。
- **Security & Performance**: 识别潜在的漏洞和 N+1 查询等瓶颈。

### 3.2 成本控制与缓存
- **Cost Estimator**: 在运行 AI 分析前预估 Token 消耗，防止意外支出。
- **Result Caching**: 深度分析结果被序列化存储，避免对未变动代码重复分析。

## 4. 预测性防错 (`Prediction Engine`)

位于 `prediction/`，旨在实现“测试左移”：
- **逻辑**: 在 Subtask 执行前，分析目标文件的历史模式。
- **产出**: 生成 `subtask_checklist.md`，预判该改动可能导致的副作用（如：修改了 Auth 逻辑，需同步更新 Session 校验器）。

## 5. 总结
Auto-Claude 的情报系统实现了从“看文件”到“懂工程”的跨越。静态分析保证了**执行的安全性**，AI 分析保证了**架构的合理性**，而预测引擎则保证了**开发的韧性**。
