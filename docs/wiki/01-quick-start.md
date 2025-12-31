# 快速入门

> ⏱️ 预计时间: 5 分钟

---

## 第一步：启动应用

### 方式 A：使用预编译版本（推荐）

从 [GitHub Releases](https://github.com/ameureka/Auto-Claude/releases) 下载适合您系统的安装包：

| 系统 | 文件 |
|------|------|
| macOS | `Auto-Claude-x.x.x.dmg` |
| Windows | `Auto-Claude-x.x.x.exe` |
| Linux | `Auto-Claude-x.x.x.AppImage` |

### 方式 B：从源码运行

```bash
git clone https://github.com/ameureka/Auto-Claude.git
cd Auto-Claude
npm run install:all
npm run dev
```

---

## 第二步：配置认证

首次启动时，应用会引导您完成认证配置。

### 三种认证方式

| 方式 | 适用场景 | 配置方法 |
|------|----------|----------|
| **OAuth Token** | 个人使用（推荐） | 运行 `claude setup-token` |
| **API Key** | 直接计费 | 输入 `sk-ant-api...` |
| **Proxy** | 企业/ProxyCast | 配置代理地址 |

> 💡 **提示**: OAuth Token 会自动保存到系统钥匙串

---

## 第三步：打开项目

1. 点击 **"Open Project"** 或 **"New Project"**
2. 选择一个 Git 仓库目录
3. 等待项目加载完成

> ⚠️ **要求**: 目录必须是 Git 仓库（有 `.git` 文件夹）

---

## 第四步：创建第一个任务

1. 点击侧边栏的 **"+ New Task"**
2. 描述您想要构建的功能，例如：
   ```
   添加一个用户登录页面，包含邮箱和密码输入框
   ```
3. 点击 **"Create"**

---

## 第五步：观察 AI 工作

任务创建后，Auto-Claude 会：

```
1. 分析您的代码库 → 理解项目结构
2. 创建规格文档 → 明确实现计划
3. 编写代码 → 在隔离分支中工作
4. QA 验证 → 自动检查质量
5. 等待审查 → 请您确认合并
```

您可以在 **Agent Terminals** 页面实时观察 AI 的工作过程。

---

## 第六步：审查与合并

当任务完成后：

1. 进入 **Worktrees** 页面
2. 查看 AI 的代码更改
3. 选择 **Merge**（合并）或 **Discard**（丢弃）

---

## 🎉 恭喜！

您已完成 Auto-Claude 快速入门。接下来：

- 📖 阅读 [界面指南](03-ui-guide/welcome-screen.md) 了解更多功能
- 🔧 查看 [设置页面](03-ui-guide/settings.md) 自定义配置
- 💬 进入 [Insights](05-features/insights.md) 与 AI 对话
