# CLI 修改后端测试方案

> 日期: 2025-12-31
> 版本: 1.0

---

## 一、验证修改（无需打包）

### 方法 A: 后端 Python 属性测试

```bash
cd /Users/ameureka/Desktop/ai_infra_ameureka/Auto-Claude

# 运行属性测试验证 auth 模块 (31 个测试)
python -m pytest tests/test_auth_properties.py -v

# 预期结果: 31 passed
```

**测试覆盖范围：**
- Token 分类正确性 (OAuth/API Key/Proxy/Unknown)
- 类型特定环境注入
- 冲突变量清理
- 优先级解析确定性
- Proxy 配置验证完整性
- 向后兼容性
- OAuth/API Key/Proxy 模式集成测试

### 方法 B: 快速验证认证逻辑

```bash
cd /Users/ameureka/Desktop/ai_infra_ameureka/Auto-Claude/apps/backend

python -c "
from core.auth import get_auth_token, get_token_type, get_auth_token_source, validate_proxy_config

token = get_auth_token()
if token:
    source = get_auth_token_source()
    token_type = get_token_type(token)
    print(f'✅ Auth: {source}')
    print(f'✅ Mode: {token_type.upper()}')
    print(f'✅ Token prefix: {token[:20]}...')
    
    is_valid, error = validate_proxy_config()
    print(f'✅ Proxy validation: {\"PASS\" if is_valid else \"FAIL - \" + error}')
else:
    print('⚠️ No token found - please configure authentication')
"
```

### 方法 C: Electron 开发模式（推荐完整验证）

```bash
# 1. 先修复 npm 缓存权限（如有权限问题）
sudo chown -R $(whoami) ~/.npm

# 2. 进入前端目录
cd /Users/ameureka/Desktop/ai_infra_ameureka/Auto-Claude/apps/frontend

# 3. 安装依赖
npm install

# 4. 开发模式运行（不打包，直接测试）
npm run dev
```

---

## 二、打包 Mac 安装包 (DMG)

### 2.1 一键打包

```bash
cd /Users/ameureka/Desktop/ai_infra_ameureka/Auto-Claude/apps/frontend

# 打包 Mac 版本 (Intel + Apple Silicon)
npm run package:mac
```

**打包流程：**
1. 下载 Python 运行时 (`npm run python:download`)
2. 构建前端 (`electron-vite build`)
3. 使用 `electron-builder` 创建 DMG 和 ZIP

### 2.2 输出位置

```
apps/frontend/dist/
├── Auto-Claude-X.Y.Z-darwin-arm64.dmg   # Apple Silicon
├── Auto-Claude-X.Y.Z-darwin-arm64.zip
├── Auto-Claude-X.Y.Z-darwin-x64.dmg     # Intel
└── Auto-Claude-X.Y.Z-darwin-x64.zip
```

### 2.3 快速测试打包应用

```bash
# 打开打包好的应用
npm run start:packaged:mac
```

---

## 三、其他平台打包命令

| 平台 | 命令 |
|------|------|
| macOS | `npm run package:mac` |
| Windows | `npm run package:win` |
| Linux | `npm run package:linux` |
| Linux Flatpak | `npm run package:flatpak` |

---

## 四、版本号更新

如需正式发布，需更新版本号：

```bash
cd /Users/ameureka/Desktop/ai_infra_ameureka/Auto-Claude

# 更新版本号（会同时更新 frontend/package.json 和 backend/__init__.py）
node scripts/bump-version.js patch  # 2.7.2 -> 2.7.3
node scripts/bump-version.js minor  # 2.7.2 -> 2.8.0
node scripts/bump-version.js major  # 2.7.2 -> 3.0.0
```

---

## 五、验证结果示例

### 属性测试输出

```
============================= test session starts ==============================
collected 31 items

tests/test_auth_properties.py::TestTokenClassificationProperty::test_token_classification_exhaustive PASSED
tests/test_auth_properties.py::TestTokenClassificationProperty::test_oauth_token_classification PASSED
tests/test_auth_properties.py::TestTokenClassificationProperty::test_api_key_classification PASSED
...
tests/test_auth_properties.py::TestProxyModeIntegration::test_proxy_flow_complete PASSED
tests/test_auth_properties.py::TestProxyModeIntegration::test_proxy_without_base_url_fails PASSED

============================== 31 passed in 0.33s ==============================
```

### 认证验证输出

```
✅ Auth: ANTHROPIC_AUTH_TOKEN
✅ Mode: PROXY
✅ Token prefix: pc_V2DwytiHa8mbbHxDB...
✅ Proxy validation: PASS
```

---

## 六、修改的文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `apps/backend/core/auth.py` | 验证已存在 | Token 检测、环境注入、Proxy 验证 |
| `apps/backend/core/client.py` | 验证已存在 | ClientFactory 认证集成 |
| `apps/backend/core/simple_client.py` | 验证已存在 | SimpleClientFactory 认证集成 |
| `apps/backend/cli/utils.py` | **修改** | 早期 Proxy 校验、认证模式显示、API Key 警告框 |
| `apps/backend/.env.example` | **修改** | 三种认证方法配置示例 |
| `tests/requirements-test.txt` | **修改** | 添加 hypothesis>=6.0.0 |
| `tests/test_auth_properties.py` | **新增** | 31 个属性测试和集成测试 |

---

## 七、三种认证方式配置

### 方法 1: OAuth Token (推荐)

```bash
# 运行设置命令
claude setup-token

# 或在 .env 中配置
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxxxx
```

### 方法 2: API Key (直接计费)

```bash
# 在 .env 中配置
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# ⚠️ 警告: 费用直接计入你的 Anthropic 账户
```

### 方法 3: Proxy/Enterprise (ProxyCast)

```bash
# 在 .env 中配置
ANTHROPIC_AUTH_TOKEN=pc_xxxxx
ANTHROPIC_BASE_URL=http://127.0.0.1:8999
```
