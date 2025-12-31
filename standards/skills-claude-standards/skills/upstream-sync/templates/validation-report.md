# 合并验证报告

> **生成时间**: {{TIMESTAMP}}
> **合并提交**: {{MERGE_COMMIT}}

---

## 测试结果

### 后端测试

```
{{BACKEND_TEST_OUTPUT}}
```

**状态**: {{BACKEND_TEST_STATUS}}

### 前端构建

```
{{FRONTEND_BUILD_OUTPUT}}
```

**状态**: {{FRONTEND_BUILD_STATUS}}

---

## 核心功能验证

### {{CORE_FEATURE_1_NAME}}

| 检查项 | 结果 |
|--------|------|
{{CORE_FEATURE_1_CHECKS}}

### {{CORE_FEATURE_2_NAME}}

| 检查项 | 结果 |
|--------|------|
{{CORE_FEATURE_2_CHECKS}}

### 配置文件

| 检查项 | 结果 |
|--------|------|
{{CONFIG_CHECKS}}

---

## 上游新功能验证

| 功能 | 来源提交 | 验证结果 |
|------|---------|---------|
{{UPSTREAM_FEATURES}}

---

## 验证结论

| 类别 | 状态 | 说明 |
|------|------|------|
| 测试 | {{TEST_STATUS}} | {{TEST_SUMMARY}} |
| 构建 | {{BUILD_STATUS}} | {{BUILD_SUMMARY}} |
| 核心功能 | {{CORE_STATUS}} | {{CORE_SUMMARY}} |
| 上游功能 | {{UPSTREAM_STATUS}} | {{UPSTREAM_SUMMARY}} |

---

## 总体结论

{{OVERALL_CONCLUSION}}

---

## 下一步

进入 **Phase 6: Publish** 推送到远程仓库。
