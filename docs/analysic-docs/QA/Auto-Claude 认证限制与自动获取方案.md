根据我对前端和后端代码的深度分析，以下是完整的发现：

  ---
  1. 认证限制的完整拦截点

  后端 Python 层 (3 个拦截点)

  | 文件                 | 位置                 | 限制内容                                   |
  |----------------------|----------------------|--------------------------------------------|
  | core/auth.py:18-21   | AUTH_TOKEN_ENV_VARS  | 只包含 OAuth Token，排除 ANTHROPIC_API_KEY |
  | core/auth.py:25-32   | SDK_ENV_VARS         | 明确排除 ANTHROPIC_API_KEY                 |
  | core/auth.py:139-142 | require_auth_token() | 错误消息明确拒绝 API Key                   |

  前端 Electron 层 (4 个拦截点)

  | 文件                              | 位置                  | 限制内容                             |
  |-----------------------------------|-----------------------|--------------------------------------|
  | claude-profile-manager.ts:344-364 | getActiveProfileEnv() | 只设置 CLAUDE_CODE_OAUTH_TOKEN       |
  | claude-integration-handler.ts:255 | invokeClaude()        | 写入临时文件时只用 OAuth Token       |
  | ClaudeOAuthFlow.tsx:178           | UI 提示               | 明确显示 Token 格式 sk-ant-oat01-... |
  | output-parser.ts                  | Token 检测            | 只识别 OAuth Token 格式              |

  ---
  2. Claude Code 配置文件位置（已确认）

  macOS:
  ├── ~/.claude/                          # 默认配置目录
  │   ├── credentials                     # 凭证文件
  │   ├── credentials.json
  │   ├── settings.json                   # 可能包含 Token
  │   └── projects/                       # 项目会话数据
  │
  ├── ~/.claude-profiles/                 # 多账户配置目录
  │   └── {profile-name}/                 # 每个 Profile 独立目录
  │
  └── macOS Keychain                      # 系统钥匙串
      └── "Claude Code-credentials"       # 服务名
          └── JSON: { claudeAiOauth: { accessToken: "sk-ant-oat01-..." } }

  关键发现：core/auth.py:35-88 中的 get_token_from_keychain() 函数已经实现了从 macOS Keychain 自动读取 Token 的功能！

  ---
  3. 自动获取认证的优化方案

  基于现有代码，Auto-Claude 已经支持从以下来源自动获取认证：

  1. 环境变量 CLAUDE_CODE_OAUTH_TOKEN
  2. 环境变量 ANTHROPIC_AUTH_TOKEN (企业代理)
  3. macOS Keychain (自动回退)

  问题：如果你的 Claude Code CLI 已经认证成功，Token 应该已经在 Keychain 中。但如果你使用的是 API Key 而非 OAuth Token，则无法自动获取。

  ---
  4. 完整魔改方案（支持 API Key）

  步骤 1: 修改 apps/backend/core/auth.py

  # 第 18-32 行 - 添加 API Key 支持
  AUTH_TOKEN_ENV_VARS = [
      "CLAUDE_CODE_OAUTH_TOKEN",
      "ANTHROPIC_AUTH_TOKEN",
      "ANTHROPIC_API_KEY",  # <--- 新增
  ]

  SDK_ENV_VARS = [
      "ANTHROPIC_BASE_URL",
      "ANTHROPIC_AUTH_TOKEN",
      "ANTHROPIC_API_KEY",  # <--- 新增
      "NO_PROXY",
      "DISABLE_TELEMETRY",
      "DISABLE_COST_WARNINGS",
      "API_TIMEOUT_MS",
  ]

  步骤 2: 修改 apps/backend/core/client.py

  在 create_client() 函数中添加智能 Token 类型检测：

  def create_client(...):
      token = require_auth_token()

      # 智能检测 Token 类型
      if token.startswith("sk-ant-api"):
          # API Key - 设置到正确的环境变量
          os.environ["ANTHROPIC_API_KEY"] = token
          # 清除 OAuth 变量防止冲突
          os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
      else:
          # OAuth Token - 保持原有逻辑
          os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token

      # ... 后续代码不变

  步骤 3: 修改 apps/backend/cli/utils.py

  更新 validate_environment() 函数的错误消息：

  def validate_environment(spec_dir: Path) -> bool:
      valid = True

      if not get_auth_token():
          print("Error: No authentication token found")
          print("\nPlease set one of the following:")
          print("  - ANTHROPIC_API_KEY (API Key)")
          print("  - CLAUDE_CODE_OAUTH_TOKEN (OAuth Token)")
          print("  - Or run 'claude setup-token'")
          valid = False
      else:
          source = get_auth_token_source()
          if source:
              print(f"Auth Source: {source}")

      # ... 后续代码不变

  步骤 4: 前端修改（可选）

  如果需要在 UI 中也支持 API Key，修改以下文件：

  apps/frontend/src/main/claude-profile-manager.ts:344-364

  getActiveProfileEnv(): Record<string, string> {
    const profile = this.getActiveProfile();
    const env: Record<string, string> = {};

    if (profile?.oauthToken) {
      const decryptedToken = decryptToken(profile.oauthToken);
      if (decryptedToken) {
        // 智能检测 Token 类型
        if (decryptedToken.startsWith('sk-ant-api')) {
          env.ANTHROPIC_API_KEY = decryptedToken;
        } else {
          env.CLAUDE_CODE_OAUTH_TOKEN = decryptedToken;
        }
      }
    }
    // ... 后续代码
    return env;
  }

  ---
  5. 自动获取 Claude Code 认证的优化建议

  如果你希望 Auto-Claude 能自动读取 Claude Code CLI 的认证配置，可以增强 get_token_from_keychain() 函数：

  def get_token_from_claude_config() -> str | None:
      """
      从 Claude Code 配置目录读取 Token
      """
      import os
      from pathlib import Path

      config_dir = Path.home() / ".claude"

      # 尝试读取 credentials.json
      creds_file = config_dir / "credentials.json"
      if creds_file.exists():
          try:
              import json
              data = json.loads(creds_file.read_text())
              # 尝试多种可能的 key
              for key in ["accessToken", "token", "api_key", "oauth_token"]:
                  if key in data:
                      return data[key]
          except:
              pass

      # 尝试读取 settings.json
      settings_file = config_dir / "settings.json"
      if settings_file.exists():
          try:
              import json
              data = json.loads(settings_file.read_text())
              if "token" in data:
                  return data["token"]
          except:
              pass

      return None

  然后在 get_auth_token() 中添加这个来源：

  def get_auth_token() -> str | None:
      # 1. 检查环境变量
      for var in AUTH_TOKEN_ENV_VARS:
          token = os.environ.get(var)
          if token:
              return token

      # 2. 检查 macOS Keychain
      token = get_token_from_keychain()
      if token:
          return token

      # 3. 检查 Claude Code 配置目录 (新增)
      token = get_token_from_claude_config()
      if token:
          return token

      return None

  ---
  6. 风险提示

  | 风险       | 说明                           | 缓解措施                          |
  |------------|--------------------------------|-----------------------------------|
  | 计费风险   | API Key 直接扣费，无免费额度   | 在 Anthropic Console 设置预算上限 |
  | Token 泄露 | 配置文件可能被读取             | 确保文件权限为 600                |
  | SDK 兼容性 | 未来 SDK 可能移除 API Key 支持 | 保留 OAuth 作为主要方式           |

  ---
  7. 总结

  现状：
  - Auto-Claude 已经支持从 macOS Keychain 自动获取 OAuth Token
  - 如果你的 Claude Code CLI 已认证，Token 应该已在 Keychain 中
  - 限制 API Key 是有意为之，防止意外计费

  如果你需要使用 API Key：
  - 按照上述步骤 1-3 修改后端代码
  - 可选修改步骤 4 的前端代码
  - 在 .env 中设置 ANTHROPIC_API_KEY=sk-ant-api03-...

  如果你想自动获取已有认证：
  - 检查 ~/.claude/ 目录下的配置文件格式
  - 增强 get_auth_token() 函数读取这些文件