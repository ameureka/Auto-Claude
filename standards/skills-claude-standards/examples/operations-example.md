# Operations 子目录示例

这个示例展示如何使用 operations 子目录组织复杂 Skill 的详细内容。

## 使用场景

当 Skill 满足以下条件时，应该使用 operations 子目录：

- 主文档超过 300 行
- 包含多个复杂的子流程
- 需要详细的故障排查指南
- 有高级用法或特殊场景
- 需要大量的参考资料

## 文件组织示例

```
.claude/skills/
└── database-migration/
    ├── SKILL.md
    └── operations/
        ├── workflow.md          # 详细工作流程
        ├── scenarios.md         # 使用场景
        ├── reference.md         # 参考资料
        ├── troubleshooting.md   # 故障排查
        └── advanced.md          # 高级用法
```

## operations/workflow.md 示例

```markdown
# 数据库迁移详细工作流程

## 概述

本文档提供数据库迁移的详细步骤和最佳实践。

## 迁移前准备

### 1. 环境检查

**检查数据库连接**:
```bash
psql -h localhost -U postgres -d mydb -c "SELECT version();"
```

**检查磁盘空间**:
```bash
df -h /var/lib/postgresql
```

至少需要当前数据库大小的 2 倍空间

**检查数据库大小**:
```sql
SELECT pg_size_pretty(pg_database_size('mydb'));
```

### 2. 备份数据库

**创建完整备份**:
```bash
pg_dump -h localhost -U postgres -d mydb -F c -f backup_$(date +%Y%m%d_%H%M%S).dump
```

**验证备份**:
```bash
pg_restore --list backup_20241220_120000.dump | head -20
```

**测试恢复**（在测试环境）:
```bash
createdb mydb_test
pg_restore -h localhost -U postgres -d mydb_test backup_20241220_120000.dump
```

### 3. 准备迁移脚本

**创建迁移目录**:
```bash
mkdir -p migrations/$(date +%Y%m%d)
```

**编写迁移脚本**:
```sql
-- migrations/20241220/001_add_user_table.sql
BEGIN;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

**编写回滚脚本**:
```sql
-- migrations/20241220/001_add_user_table_rollback.sql
BEGIN;

DROP INDEX IF EXISTS idx_users_email;
DROP TABLE IF EXISTS users;

COMMIT;
```

## 执行迁移

### 1. 在测试环境验证

**应用迁移**:
```bash
psql -h localhost -U postgres -d mydb_test -f migrations/20241220/001_add_user_table.sql
```

**验证结果**:
```sql
\d users
SELECT * FROM users LIMIT 1;
```

**测试回滚**:
```bash
psql -h localhost -U postgres -d mydb_test -f migrations/20241220/001_add_user_table_rollback.sql
```

**验证回滚**:
```sql
\d users  -- 应该显示 "Did not find any relation named users"
```

### 2. 在生产环境执行

**设置维护模式**（如果需要）:
```bash
# 停止应用服务器
systemctl stop myapp

# 或者设置只读模式
psql -h localhost -U postgres -d mydb -c "ALTER DATABASE mydb SET default_transaction_read_only = on;"
```

**执行迁移**:
```bash
psql -h localhost -U postgres -d mydb -f migrations/20241220/001_add_user_table.sql
```

**验证迁移**:
```sql
-- 检查表结构
\d users

-- 检查索引
\di users*

-- 检查约束
\d+ users
```

**取消维护模式**:
```bash
# 启动应用服务器
systemctl start myapp

# 或者取消只读模式
psql -h localhost -U postgres -d mydb -c "ALTER DATABASE mydb SET default_transaction_read_only = off;"
```

### 3. 监控和验证

**监控数据库性能**:
```sql
-- 检查慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 检查表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**检查应用日志**:
```bash
tail -f /var/log/myapp/app.log | grep ERROR
```

**运行健康检查**:
```bash
curl http://localhost:3000/health
```

## 回滚流程

如果迁移后发现问题，立即执行回滚：

### 1. 快速回滚

**设置维护模式**:
```bash
systemctl stop myapp
```

**执行回滚脚本**:
```bash
psql -h localhost -U postgres -d mydb -f migrations/20241220/001_add_user_table_rollback.sql
```

**验证回滚**:
```sql
\d users  -- 确认表已删除
```

**恢复服务**:
```bash
systemctl start myapp
```

### 2. 从备份恢复（如果回滚脚本失败）

**停止数据库**:
```bash
systemctl stop postgresql
```

**恢复备份**:
```bash
dropdb mydb
createdb mydb
pg_restore -h localhost -U postgres -d mydb backup_20241220_120000.dump
```

**启动数据库**:
```bash
systemctl start postgresql
```

**验证恢复**:
```sql
SELECT COUNT(*) FROM users;  -- 应该显示迁移前的数据
```

## 性能优化

### 大表迁移优化

**使用并发索引创建**:
```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

**分批处理数据**:
```sql
-- 不要一次性更新所有行
UPDATE users SET status = 'active' WHERE id BETWEEN 1 AND 10000;
UPDATE users SET status = 'active' WHERE id BETWEEN 10001 AND 20000;
-- ...
```

**使用 VACUUM ANALYZE**:
```sql
VACUUM ANALYZE users;
```

## 最佳实践

1. **始终在事务中执行** - 使用 BEGIN/COMMIT
2. **编写可重入的迁移** - 使用 IF NOT EXISTS
3. **保持迁移原子性** - 一个迁移只做一件事
4. **测试回滚脚本** - 确保可以安全回滚
5. **记录迁移历史** - 在数据库中记录已执行的迁移

## 相关链接

- [返回主文档](../SKILL.md)
- [查看使用场景](./scenarios.md)
- [查看故障排查](./troubleshooting.md)
- [查看高级用法](./advanced.md)
```

## operations/scenarios.md 示例

```markdown
# 数据库迁移使用场景

## 场景 1: 添加新表

**背景**: 需要添加一个新的用户表

**前提条件**:
- 数据库已备份
- 在测试环境验证通过

**步骤**:

1. 创建迁移脚本
   ```sql
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL
   );
   ```

2. 创建回滚脚本
   ```sql
   DROP TABLE IF EXISTS users;
   ```

3. 在测试环境验证

4. 在生产环境执行

**预期结果**: 新表创建成功，应用可以正常使用

**注意事项**:
- 确保表名不冲突
- 考虑索引的性能影响

---

## 场景 2: 添加新列

**背景**: 需要在现有表中添加新列

**前提条件**:
- 表已存在
- 了解表的当前结构

**步骤**:

1. 创建迁移脚本
   ```sql
   ALTER TABLE users ADD COLUMN phone VARCHAR(20);
   ```

2. 创建回滚脚本
   ```sql
   ALTER TABLE users DROP COLUMN IF EXISTS phone;
   ```

3. 如果列有默认值
   ```sql
   ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
   ```

4. 如果需要填充现有数据
   ```sql
   UPDATE users SET phone = '' WHERE phone IS NULL;
   ```

**预期结果**: 新列添加成功，现有数据不受影响

**注意事项**:
- 大表添加列可能需要较长时间
- 考虑使用 NOT NULL 约束的影响
- 默认值可能导致表锁定

---

## 场景 3: 修改列类型

**背景**: 需要修改列的数据类型

**前提条件**:
- 了解数据兼容性
- 已备份数据

**步骤**:

1. 检查数据兼容性
   ```sql
   SELECT id, email FROM users WHERE email::INTEGER IS NULL;
   ```

2. 创建迁移脚本
   ```sql
   ALTER TABLE users ALTER COLUMN age TYPE INTEGER USING age::INTEGER;
   ```

3. 创建回滚脚本
   ```sql
   ALTER TABLE users ALTER COLUMN age TYPE VARCHAR(10) USING age::VARCHAR;
   ```

**预期结果**: 列类型修改成功，数据正确转换

**注意事项**:
- 类型转换可能失败
- 大表修改可能需要较长时间
- 考虑使用临时列进行转换

---

## 场景 4: 数据迁移

**背景**: 需要将数据从一个表迁移到另一个表

**前提条件**:
- 目标表已创建
- 了解数据映射关系

**步骤**:

1. 创建临时表（可选）
   ```sql
   CREATE TABLE users_new AS SELECT * FROM users WHERE 1=0;
   ```

2. 迁移数据
   ```sql
   INSERT INTO users_new (id, email, name)
   SELECT id, email, CONCAT(first_name, ' ', last_name)
   FROM users;
   ```

3. 验证数据
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM users_new;
   ```

4. 切换表（如果使用临时表）
   ```sql
   BEGIN;
   ALTER TABLE users RENAME TO users_old;
   ALTER TABLE users_new RENAME TO users;
   COMMIT;
   ```

**预期结果**: 数据成功迁移，应用正常运行

**注意事项**:
- 大量数据迁移需要分批处理
- 考虑停机时间
- 保留旧表一段时间以便回滚

---

## 场景 5: 添加索引

**背景**: 需要添加索引以提高查询性能

**前提条件**:
- 了解查询模式
- 评估索引的影响

**步骤**:

1. 分析查询
   ```sql
   EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
   ```

2. 创建索引（并发模式，不锁表）
   ```sql
   CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
   ```

3. 验证索引
   ```sql
   \d users
   EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
   ```

4. 创建回滚脚本
   ```sql
   DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
   ```

**预期结果**: 索引创建成功，查询性能提升

**注意事项**:
- 使用 CONCURRENTLY 避免锁表
- 索引会增加写入开销
- 定期维护索引（REINDEX）

---

## 场景 6: 零停机迁移

**背景**: 需要在不停机的情况下进行迁移

**前提条件**:
- 应用支持多版本数据库结构
- 有完善的监控

**步骤**:

1. **阶段 1**: 添加新列（兼容旧代码）
   ```sql
   ALTER TABLE users ADD COLUMN new_email VARCHAR(255);
   ```

2. **阶段 2**: 部署支持双写的代码
   ```python
   # 同时写入旧列和新列
   user.email = email
   user.new_email = email
   ```

3. **阶段 3**: 迁移现有数据
   ```sql
   UPDATE users SET new_email = email WHERE new_email IS NULL;
   ```

4. **阶段 4**: 部署只使用新列的代码
   ```python
   # 只使用新列
   user.new_email = email
   ```

5. **阶段 5**: 删除旧列
   ```sql
   ALTER TABLE users DROP COLUMN email;
   ALTER TABLE users RENAME COLUMN new_email TO email;
   ```

**预期结果**: 迁移完成，应用无停机

**注意事项**:
- 需要多次部署
- 监控每个阶段的状态
- 准备好回滚计划

## 相关链接

- [返回主文档](../SKILL.md)
- [查看详细工作流程](./workflow.md)
- [查看故障排查](./troubleshooting.md)
```

## operations/troubleshooting.md 示例

```markdown
# 数据库迁移故障排查

## 常见问题

### 问题 1: 迁移脚本执行失败

**症状**:
```
ERROR: relation "users" already exists
```

**原因**: 表已经存在，可能是之前的迁移部分成功

**解决方法**:

1. 检查表是否存在
   ```sql
   \d users
   ```

2. 如果表存在但不完整，删除后重新创建
   ```sql
   DROP TABLE IF EXISTS users CASCADE;
   ```

3. 重新执行迁移脚本

**预防措施**:
- 使用 `CREATE TABLE IF NOT EXISTS`
- 在事务中执行迁移
- 保持迁移脚本的幂等性

---

### 问题 2: 锁等待超时

**症状**:
```
ERROR: canceling statement due to lock timeout
```

**原因**: 其他会话持有表锁

**解决方法**:

1. 查看当前锁
   ```sql
   SELECT * FROM pg_locks WHERE NOT granted;
   ```

2. 查看阻塞的查询
   ```sql
   SELECT pid, query, state
   FROM pg_stat_activity
   WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%';
   ```

3. 终止阻塞的查询（谨慎使用）
   ```sql
   SELECT pg_terminate_backend(pid);
   ```

4. 重新执行迁移

**预防措施**:
- 在低峰期执行迁移
- 使用 `LOCK TABLE` 显式获取锁
- 使用 `CONCURRENTLY` 选项（如创建索引）

---

### 问题 3: 磁盘空间不足

**症状**:
```
ERROR: could not extend file: No space left on device
```

**原因**: 磁盘空间不足

**解决方法**:

1. 检查磁盘空间
   ```bash
   df -h /var/lib/postgresql
   ```

2. 清理临时文件
   ```bash
   rm -rf /var/lib/postgresql/tmp/*
   ```

3. 清理旧的 WAL 文件
   ```sql
   SELECT pg_switch_wal();
   ```

4. 扩展磁盘空间或移动数据到更大的磁盘

**预防措施**:
- 迁移前检查磁盘空间
- 设置磁盘空间告警
- 定期清理不需要的数据

---

### 问题 4: 数据类型转换失败

**症状**:
```
ERROR: invalid input syntax for type integer: "abc"
```

**原因**: 数据不兼容目标类型

**解决方法**:

1. 查找不兼容的数据
   ```sql
   SELECT id, age FROM users WHERE age !~ '^[0-9]+$';
   ```

2. 清理或修正数据
   ```sql
   UPDATE users SET age = '0' WHERE age !~ '^[0-9]+$';
   ```

3. 重新执行类型转换

**预防措施**:
- 迁移前验证数据
- 使用 `USING` 子句处理转换
- 考虑使用临时列

---

### 问题 5: 外键约束冲突

**症状**:
```
ERROR: insert or update on table violates foreign key constraint
```

**原因**: 数据不满足外键约束

**解决方法**:

1. 临时禁用外键检查（谨慎使用）
   ```sql
   ALTER TABLE orders DISABLE TRIGGER ALL;
   -- 执行迁移
   ALTER TABLE orders ENABLE TRIGGER ALL;
   ```

2. 或者先删除外键，迁移后重新添加
   ```sql
   ALTER TABLE orders DROP CONSTRAINT fk_user_id;
   -- 执行迁移
   ALTER TABLE orders ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id);
   ```

**预防措施**:
- 按正确的顺序迁移表
- 先迁移父表，再迁移子表
- 使用 `DEFERRABLE` 约束

---

### 问题 6: 回滚失败

**症状**: 回滚脚本执行失败

**原因**: 回滚脚本不完整或数据已被修改

**解决方法**:

1. 从备份恢复
   ```bash
   pg_restore -h localhost -U postgres -d mydb backup.dump
   ```

2. 手动修复数据库状态

3. 重新执行迁移

**预防措施**:
- 测试回滚脚本
- 保持完整的备份
- 使用事务保护迁移

## 紧急恢复流程

如果迁移导致严重问题：

### 1. 立即停止应用

```bash
systemctl stop myapp
```

### 2. 评估损害

```sql
-- 检查数据完整性
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM orders;

-- 检查最近的变更
SELECT * FROM pg_stat_activity;
```

### 3. 决定恢复策略

**选项 A**: 执行回滚脚本
```bash
psql -f rollback.sql
```

**选项 B**: 从备份恢复
```bash
pg_restore backup.dump
```

**选项 C**: 手动修复
```sql
-- 根据具体情况手动修复
```

### 4. 验证恢复

```sql
-- 运行健康检查查询
SELECT COUNT(*) FROM users;
-- 检查关键数据
```

### 5. 恢复服务

```bash
systemctl start myapp
```

### 6. 监控

```bash
tail -f /var/log/myapp/app.log
```

## 预防性检查清单

迁移前执行以下检查：

- [ ] 数据库已完整备份
- [ ] 备份已验证可恢复
- [ ] 磁盘空间充足（至少 2 倍数据库大小）
- [ ] 迁移脚本在测试环境验证通过
- [ ] 回滚脚本已测试
- [ ] 团队成员已通知
- [ ] 监控已就绪
- [ ] 回滚计划已准备

## 相关链接

- [返回主文档](../SKILL.md)
- [查看详细工作流程](./workflow.md)
- [查看使用场景](./scenarios.md)
```

## 说明

这个示例展示了如何使用 operations 子目录：

1. **workflow.md** - 详细的分步骤工作流程
2. **scenarios.md** - 多个实际使用场景
3. **troubleshooting.md** - 完整的故障排查指南

**关键特点**:
- 每个文件专注于一个主题
- 文件之间相互链接
- 内容详细但组织清晰
- 易于维护和更新

**使用建议**:
- 主文档保持简洁，提供概览
- 详细内容放在 operations 中
- 使用清晰的文件命名
- 保持文档之间的链接
