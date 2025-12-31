# CLI 命令参考

Auto-Claude 后端 CLI 命令速查表。

---

## 基础命令

### 规格创建

```bash
cd apps/backend

# 交互式创建
python spec_runner.py --interactive

# 从描述创建
python spec_runner.py --task "添加用户登录功能"

# 指定复杂度
python spec_runner.py --task "修复按钮颜色" --complexity simple
```

### 构建执行

```bash
# 列出所有规格
python run.py --list

# 执行指定规格
python run.py --spec 001

# 限制迭代次数
python run.py --spec 001 --max-iterations 5
```

---

## QA 验证

```bash
# 运行 QA
python run.py --spec 001 --qa

# 跳过 QA
python run.py --spec 001 --skip-qa

# 查看 QA 状态
python run.py --spec 001 --qa-status
```

---

## 工作区管理

```bash
# 查看更改
python run.py --spec 001 --review

# 合并到主分支
python run.py --spec 001 --merge

# 丢弃更改
python run.py --spec 001 --discard
```

---

## 复杂度级别

| 级别 | 阶段数 | 适用场景 |
|------|--------|----------|
| `simple` | 3 | 1-2 个文件，简单修复 |
| `standard` | 6-7 | 3-10 个文件，新功能 |
| `complex` | 8 | 10+ 个文件，复杂架构 |

---

## 认证配置

```bash
# 获取 OAuth Token
claude setup-token

# 配置 .env
cd apps/backend
cp .env.example .env
# 编辑 .env 添加认证信息
```
