  核心思路：将 ameureka 知识沉淀为 Auto-Claude 可消费的格式

  Auto-Claude 的 Agent 是无状态的，它们完全依赖文件来获取上下文。所以关键是：把你的知识转化为 Auto-Claude 能读取的文件格式。

  ---
  你需要准备的文件

  1. 项目级配置文件

  project_index.json - 项目结构索引

  {
    "project_type": "monorepo",
    "framework": "ameureka",
    "services": {
      "frontend": {
        "path": "./",
        "tech_stack": ["next.js", "react", "typescript", "tailwindcss", "shadcn/ui"],
        "port": 3000,
        "dev_command": "pnpm dev",
        "test_command": "pnpm test",
        "build_command": "pnpm build"
      },
      "backend": {
        "path": "./",
        "tech_stack": ["next.js-api-routes", "supabase", "drizzle-orm"],
        "port": 3000,
        "database": "supabase-postgres"
      }
    },
    "infrastructure": {
      "database": "supabase",
      "auth": "supabase-auth",
      "storage": "supabase-storage",
      "deployment": "vercel"
    },
    "conventions": {
      "styling": "tailwindcss + shadcn/ui",
      "state_management": "zustand",
      "data_fetching": "server-components + server-actions",
      "i18n": "next-intl",
      "testing": "vitest"
    }
  }

  context.json - ameureka 模式上下文

  {
    "framework_patterns": {
      "component_pattern": "所有 UI 组件使用 shadcn/ui，放在 components/ui/",
      "page_pattern": "使用 App Router，页面在 app/[locale]/",
      "api_pattern": "使用 Server Actions，放在 actions/",
      "database_pattern": "使用 Drizzle ORM，schema 在 db/schema/",
      "auth_pattern": "使用 Supabase Auth，中间件在 middleware.ts"
    },
    "files_to_reference": {
      "component_example": "components/ui/button.tsx",
      "page_example": "app/[locale]/page.tsx",
      "action_example": "actions/user-actions.ts",
      "schema_example": "db/schema/users.ts",
      "api_route_example": "app/api/example/route.ts"
    },
    "existing_implementations": {
      "auth": "已实现 Supabase Auth 登录/注册",
      "i18n": "已实现多语言支持 (next-intl)",
      "theme": "已实现暗色/亮色主题切换",
      "layout": "已实现响应式布局"
    }
  }

  2. 知识沉淀文件（放在 .auto-claude/knowledge/）

  patterns.md - 代码模式文档

  # ameureka 代码模式

  ## 1. 组件模式

  ### UI 组件
  - 位置: `components/ui/`
  - 使用 shadcn/ui 组件库
  - 示例: `components/ui/button.tsx`

  ### 业务组件
  - 位置: `components/[feature]/`
  - 命名: PascalCase
  - 示例: `components/dashboard/stats-card.tsx`

  ## 2. 页面模式

  ### App Router 结构
  app/
  ├── [locale]/
  │   ├── (marketing)/     # 营销页面组
  │   │   ├── page.tsx     # 首页
  │   │   └── pricing/
  │   ├── (dashboard)/     # 仪表盘组
  │   │   ├── layout.tsx   # 需要认证
  │   │   └── dashboard/
  │   └── (auth)/          # 认证页面组
  │       ├── login/
  │       └── register/

  ## 3. 数据库模式

  ### Drizzle Schema
  - 位置: `db/schema/`
  - 命名: 单数形式 (user.ts, post.ts)
  - 导出: `db/schema/index.ts`

  ### Server Actions
  - 位置: `actions/`
  - 命名: `[entity]-actions.ts`
  - 使用 `"use server"` 指令

  ## 4. API 模式

  ### Route Handlers
  - 位置: `app/api/`
  - 使用 Next.js Route Handlers
  - 返回 NextResponse.json()

  ## 5. 样式模式

  ### Tailwind CSS
  - 使用 `cn()` 合并类名
  - 响应式: `sm:`, `md:`, `lg:`
  - 暗色模式: `dark:`

  gotchas.md - 已知陷阱

  # ameureka 开发陷阱

  ## 1. Server Components vs Client Components

  **问题**: 在 Server Component 中使用 hooks 会报错
  **解决**: 需要 hooks 的组件必须添加 `"use client"`

  ## 2. Supabase Auth

  **问题**: 客户端和服务端使用不同的 Supabase 客户端
  **解决**:
  - 客户端: `createBrowserClient()`
  - 服务端: `createServerClient()`
  - Server Actions: `createServerActionClient()`

  ## 3. next-intl 路由

  **问题**: 链接必须包含 locale
  **解决**: 使用 `useRouter()` from `@/navigation` 而非 `next/navigation`

  ## 4. Drizzle 迁移

  **问题**: 修改 schema 后需要生成迁移
  **解决**:
  ```bash
  pnpm db:generate  # 生成迁移
  pnpm db:push      # 推送到数据库

  5. 环境变量

  问题: 客户端无法访问服务端环境变量
  解决: 客户端变量必须以 NEXT_PUBLIC_ 开头

  6. Vercel 部署

  问题: 构建时数据库连接失败
  解决: 使用 POSTGRES_URL_NON_POOLING 用于迁移

  #### `codebase_map.json` - 代码库地图

  ```json
  {
    "_metadata": {
      "framework": "ameureka",
      "last_updated": "2025-12-23"
    },
    "app/[locale]/page.tsx": "首页，营销落地页",
    "app/[locale]/(dashboard)/dashboard/page.tsx": "用户仪表盘主页",
    "app/[locale]/(auth)/login/page.tsx": "登录页面",
    "app/api/webhooks/stripe/route.ts": "Stripe webhook 处理",
    "components/ui/": "shadcn/ui 组件库",
    "components/layout/header.tsx": "全局导航头部",
    "components/layout/footer.tsx": "全局页脚",
    "actions/auth-actions.ts": "认证相关 Server Actions",
    "actions/user-actions.ts": "用户相关 Server Actions",
    "db/schema/users.ts": "用户表 schema",
    "db/schema/subscriptions.ts": "订阅表 schema",
    "lib/supabase/client.ts": "Supabase 客户端配置",
    "lib/supabase/server.ts": "Supabase 服务端配置",
    "middleware.ts": "认证中间件 + i18n 中间件"
  }

  3. Spec 模板（用于新功能开发）

  spec-template.md - 功能规格模板

  # [功能名称]

  ## 概述
  [一句话描述这个功能]

  ## 用户故事
  作为 [用户角色]，我想要 [功能]，以便 [价值]

  ## 技术要求

  ### 前端
  - [ ] 页面: [页面路径]
  - [ ] 组件: [组件列表]
  - [ ] 状态管理: [需要的 store]

  ### 后端
  - [ ] API/Actions: [接口列表]
  - [ ] 数据库: [表/字段变更]

  ### 集成
  - [ ] 第三方服务: [如有]

  ## 文件变更

  ### 新建文件
  - `app/[locale]/[feature]/page.tsx`
  - `components/[feature]/[component].tsx`
  - `actions/[feature]-actions.ts`
  - `db/schema/[entity].ts`

  ### 修改文件
  - `db/schema/index.ts` - 导出新 schema
  - `lib/navigation.ts` - 添加新路由

  ## 参考模式
  - 组件模式: `components/dashboard/stats-card.tsx`
  - 页面模式: `app/[locale]/(dashboard)/dashboard/page.tsx`
  - Action 模式: `actions/user-actions.ts`

  ## 验收标准
  1. [ ] 页面正常渲染，无控制台错误
  2. [ ] 数据正确保存到数据库
  3. [ ] 响应式布局正常
  4. [ ] 暗色模式正常
  5. [ ] 多语言支持正常

  ## QA 检查点
  - 单元测试: `pnpm test`
  - 类型检查: `pnpm typecheck`
  - Lint: `pnpm lint`
  - 构建: `pnpm build`

  4. 自定义 Agent 提示词（可选但推荐）

  prompts/ameureka-coder.md - ameureka 专用 Coder 提示词

  在 coder.md 基础上添加 ameureka 特定指令：

  ## AMEUREKA 框架特定规则

  ### 必须遵守
  1. **组件**: 使用 shadcn/ui，不要自己写基础组件
  2. **样式**: 使用 Tailwind CSS，使用 `cn()` 合并类名
  3. **数据**: 优先使用 Server Actions，不要用 API Routes
  4. **认证**: 使用 Supabase Auth，检查 middleware.ts
  5. **国际化**: 所有文本使用 `useTranslations()`

  ### 文件命名
  - 组件: `kebab-case.tsx`
  - 页面: `page.tsx` (App Router)
  - Actions: `[entity]-actions.ts`
  - Schema: `[entity].ts`

  ### 导入顺序
  1. React/Next.js
  2. 第三方库
  3. @/ 别名导入
  4. 相对路径导入

  ### 提交前检查
  ```bash
  pnpm typecheck && pnpm lint && pnpm build

  ---

  ## 推荐的目录结构

  your-project/
  ├── .auto-claude/
  │   ├── knowledge/              # 知识沉淀
  │   │   ├── patterns.md         # 代码模式
  │   │   ├── gotchas.md          # 已知陷阱
  │   │   ├── codebase_map.json   # 代码库地图
  │   │   └── decisions.md        # 架构决策记录
  │   │
  │   ├── templates/              # Spec 模板
  │   │   ├── feature-spec.md     # 功能 spec 模板
  │   │   ├── bugfix-spec.md      # Bug 修复 spec 模板
  │   │   └── refactor-spec.md    # 重构 spec 模板
  │   │
  │   ├── prompts/                # 自定义提示词（可选）
  │   │   └── ameureka-coder.md   # ameureka 专用提示词
  │   │
  │   └── specs/                  # 具体功能 specs
  │       ├── 001-user-profile/
  │       ├── 002-payment-integration/
  │       └── ...
  │
  ├── project_index.json          # 项目结构索引
  ├── context.json                # 项目上下文
  └── ... (项目代码)

  ---

  ## 使用流程建议

  ### 第一步：准备知识库（一次性）

  1. 创建 `project_index.json` - 描述项目结构
  2. 创建 `context.json` - 描述 ameureka 模式
  3. 创建 `patterns.md` - 记录代码模式
  4. 创建 `gotchas.md` - 记录已知陷阱
  5. 创建 `codebase_map.json` - 映射关键文件

  ### 第二步：为新功能创建 Spec

  ```bash
  # 创建新 spec 目录
  mkdir -p .auto-claude/specs/003-new-feature

  # 复制模板
  cp .auto-claude/templates/feature-spec.md .auto-claude/specs/003-new-feature/spec.md

  # 编辑 spec.md，填写具体需求

  第三步：运行 Auto-Claude

  # 激活环境
  source auto-claude/.venv/bin/activate

  # 运行规划
  python auto-claude/run.py --spec 003-new-feature

  # Auto-Claude 会:
  # 1. Planner Agent 读取 spec.md + 知识库
  # 2. 创建 implementation_plan.json
  # 3. Coder Agent 逐个实现 subtask
  # 4. QA Agent 验证

  ---
  关键建议

  1. 知识库是核心: 花时间把 ameureka 的模式、陷阱、决策记录下来，这是 Agent 的"大脑"
  2. Spec 要具体: 不要写模糊的需求，要明确：
    - 具体要创建/修改哪些文件
    - 参考哪些现有文件的模式
    - 验收标准是什么
  3. 迭代优化知识库: 每次开发后，把新发现的模式和陷阱补充到知识库
  4. 利用 Context7: 在 spec 中指明使用的第三方库，Agent 会自动查询最新文档
  5. 小步快跑: 一个 spec 不要太大，拆分成多个小功能更容易成功

  你想让我帮你创建这些文件的初始版本吗？或者针对某个具体功能创建一个示例 spec？


  ✦ 《知识沉淀 auto-claude 模式》深度拆解与建议分析

  这份文档非常有价值，它实际上是在为 Auto-Claude 这个“执行引擎”构建一套“领域特定知识库 (Domain Knowledge Base)”。

  由于 Auto-Claude 的 Agent 是无状态且依赖文件的，这份文档的核心思路是：将 AMEUREKA 的“隐性规范”显性化为 Agent 可识别的“物理文件”。

  以下是针对 AMEUREKA 开发场景的深度拆解分析：

  1. 项目索引与上下文的“定制化” (project_index.json & context.json)
   * 分析：原生的 Auto-Claude 探测技术栈比较通用。这份建议通过手动编写这两个文件，强行将 framework: ameureka 注入系统。
   * 关键点：在 conventions 中明确 next-intl (i18n)、zustand (状态管理) 和 vitest (测试)。这相当于给 Agent 划定了“技术边界”，防止它引入 AMEUREKA 之外的第三方库。

  2. 知识沉淀层：Agent 的“记忆外挂” (patterns.md & gotchas.md)
  这是解决 AI “面条代码”和“低级错误”的核心。
   * `patterns.md` (模式文档)：
       * 作用：它不仅仅是注释，它是 Agent 的“视觉模板”。例如明确 App Router 的 [locale] 结构。当 Coder Agent 犹豫文件该放哪时，这个文件会告诉它：“必须在 app/[locale]/ 下”。
   * `gotchas.md` (陷阱文档)：
       * 作用：预判失败。文档中列出的 Server vs Client Components 报错、Supabase Auth 客户端区分等，都是开发者在 Next.js 实战中最高频踩的坑。
       * 价值：将这些写入文件，配合我们之前分析的 Recovery Hints 机制，能让 Agent 在第一次尝试时就避开这些“坑”。

  3. 代码库地图：突破 Context 限制 (codebase_map.json)
   * 分析：AI 面对大型项目往往会“迷路”。这个文件提供了一个语义化的导航。
   * 建议：在 AMEUREKA 开发中，这个文件应该包含核心 Hook 和 Lib 的职责说明（如：middleware.ts 负责认证+i18n）。

  4. 规格书标准化：Spec 模板化 (spec-template.md)
   * 分析：这是“指令质量”的保障。
   * AMEUREKA 适配：模板中应包含 AMEUREKA 特有的“Acceptance Criteria”，强制要求通过 pnpm typecheck。这与 QA Reviewer Agent 的逻辑完美闭环。

  5. 专用 Coder 指令：ameureka-coder.md
   * 分析：这是对原生 coder.md 的“补丁”。
   * 核心逻辑：“优先使用 Server Actions，不要用 API Routes”。这行指令能瞬间改变 AI 的开发范式，使其符合现代 Next.js 的最佳实践。

  ---

  综合建议与实施思路

  基于以上分析，我建议我们在 AMEUREKA 框架协作时，采取以下“知识冷启动”步骤：

   1. 物理目录构建：
      在项目中创建 .auto-claude/knowledge/ 目录，作为 AMEUREKA 的“法典仓库”。
   2. 知识双向同步：
       * 前置：将 AMEUREKA 的 code-specs-standards 浓缩进 patterns.md。
       * 后置：利用 Auto-Claude 的 insight_extractor，在每次成功开发后，自动将新发现的 AMEUREKA 模式补充到 knowledge/ 目录中。
   3. Prompt 级别劫持：
      不修改 Auto-Claude 的 Python 源码，而是修改 auto-claude/prompts/coder.md 的头部，增加一行：
      "Read .auto-claude/knowledge/patterns.md and follow AMEUREKA conventions strictly."

  讨论思考：
  你觉得我们是否应该编写一个“AMEUREKA 知识初始化脚本”？一键生成这些符合规范的 JSON 和 MD 文件，这样任何一个新拉取的 v0 项目，只要运行一下脚本，立刻就能被 Auto-Claude 蜂群以“资深 AMEUREKA 工程师”的身份进行重构。



✦ 003-流水线ameureka-v0 目录下的材料是 AMEUREKA 框架的“灵魂”，它们比 001 目录的原始素材更具工程化和结构化。

  通过分析 Ameureka Vibe Coding 核心方法论 和 设计原则与标准，我为你设计了一套将这些流水线材料沉淀为 Auto-Claude 消费文件的“全栈自动化方案”：

  1. 核心转换设计：建立 AMEUREKA “四层架构” 约束

  你的方法论中明确了 L1-L4 的架构分层。我们要把这个设计成 Coder Agent 的“执行律法”。

   * 沉淀文件: .auto-claude/knowledge/architecture.md
   * 设计样子:
       * 明确定义每一层的物理路径（如 L2 必须在 src/actions/）。
       * 定义 “三段式” Action 的标准代码模板。
       * 硬性约束: “严禁在 UI 组件中直接调用 Server Action，必须经过 L3 Hooks 桥接”。这行指令将直接终结 AI 写出混乱代码的可能。

  2. 数据库设计标准：转化为“静态验证算子”

  你的材料对数据库命名（单数、下划线、UUID 主键）有极细致的要求。

   * 沉淀文件: .auto-claude/knowledge/db_standards.md
   * 设计样子:
       * 列出字段映射表（如：updatedAt -> updated_at）。
       * 集成逻辑: 将这些规则注入到 Spec Validator 中。当 AI 生成 implementation_plan.json 时，系统自动检查新建的表名是否为复数，如果是（如 users），直接报错打回。

  3. Vibe Coding Flow：转化为“SOP 任务模板”

  你定义的 Step 1-4（定义模型 -> 编写动作 -> 封装钩子 -> 构建视图）是完美的 Subtask 拆解逻辑。

   * 沉淀文件: .auto-claude/templates/ameureka-feature.md
   * 设计样子:
       * 一个预填好的 Spec 模板，要求用户只需填写业务描述。
       * 自动化设计: 当 Planner Agent 识别到这是一个 AMEUREKA 任务时，它被强制要求生成的 implementation_plan.json 必须包含这四个 Phase，且每个 Phase 的 verification 命令必须包含 pnpm db:generate 或 pnpm typecheck。

  4. “Vibecoding 基础设施”：转化为 Agent 的工具包 (Skills)

  目录中的 002-skill-agent-example 规范 是最有潜力的部分。

   * 设计方案:
       * Skill 沉淀: 将 AMEUREKA 特有的常用代码片段（如 Shadcn UI 的各种变体、Better-Auth 的配置）转化为 MCP Tools 或 Reference Patterns。
       * 样子: 创建 .auto-claude/knowledge/skills/ 目录，存放“如何处理 Stripe Webhook”、“如何配置 next-intl”的黄金代码案例。Coder Agent 在处理相关任务时，会被强制“挂载”这些参考文件。

  ---

  5. 最终形态：AMEUREKA 开发“数字中枢”

  如果我们完成这些沉淀，你的 .auto-claude 目录将变成这样：

    1 .auto-claude/
    2 ├── knowledge/
    3 │   ├── architecture.md      # 源自：核心方法论 (L1-L4 约束)
    4 │   ├── db_standards.md      # 源自：设计原则 (命名、索引、外键)
    5 │   ├── coding_sop.md        # 源自：Vibe Coding Flow (Step 1-4)
    6 │   └── gotchas.md           # 源自：常见陷阱 (Better-Auth, RSC 报错)
    7 ├── templates/
    8 │   └── ameureka-spec.md     # 源自：001-需求设计模板 (EARS 格式)
    9 └── prompts/
   10     └── ameureka-coder.md    # 源自：对原生 coder.md 的“架构补丁”

  接下来建议的工作重点：

   1. “架构劫持”: 优先将 ameureka Vibe Coding 核心方法论.md 中的 L1-L4 分层逻辑 提炼成一个精简的 Markdown 列表，放入 knowledge/architecture.md。这是 Agent 蜂群协作时不“打架”的根基。
   2. “命令赋能”: 修改 auto-claude/project/framework_detector.py（参照我们之前的分析），让它能自动识别 AMEUREKA 标志性的 better-auth 或 next-safe-action 依赖，从而自动激活上述所有约束。

  讨论思考：
  你觉得我们是否需要把 Biome 这种“替代 ESLint/Prettier”的决策也写进 Security Validator？这样 Agent 尝试运行 npm run lint 时，系统会纠正它使用 pnpm biome check。这能极大提升“蜂群”在处理代码质量时的统一感