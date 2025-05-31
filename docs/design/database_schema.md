# Paperal 数据库设计

## 1. 概述

Paperal系统使用PostgreSQL作为主要关系型数据库，用于存储用户数据、论文元数据、分析结果等结构化数据。同时，系统还使用向量数据库来支持语义搜索和相似度匹配功能。本文档详细说明了数据库架构设计，包括表结构、关系、索引和查询优化策略。

## 2. 实体关系图 (ERD)

```
+---------------+       +---------------+       +---------------+
|     Users     |       |    Papers     |       |   Analysis    |
+---------------+       +---------------+       +---------------+
| PK: id        |<----->| PK: id        |<----->| PK: id        |
| email         |       | title         |       | paper_id      |
| password_hash |       | authors       |       | status        |
| name          |       | upload_date   |       | created_at    |
| organization  |       | file_path     |       | completed_at  |
| role          |       | user_id       |       | result_data   |
| created_at    |       | metadata      |       | feedback      |
| updated_at    |       | status        |       +---------------+
| subscription  |       | tags          |             |
+---------------+       +---------------+             |
       |                                              |
       |                                              |
       v                                              v
+---------------+                           +---------------+
| Subscriptions |                           |    Reports    |
+---------------+                           +---------------+
| PK: id        |                           | PK: id        |
| user_id       |                           | analysis_id   |
| plan_type     |                           | title         |
| start_date    |                           | created_at    |
| end_date      |                           | format        |
| status        |                           | file_path     |
| payment_info  |                           | shared_with   |
+---------------+                           +---------------+
                                                   |
                                                   |
                                                   v
                                           +---------------+
                                           |   Comments    |
                                           +---------------+
                                           | PK: id        |
                                           | report_id     |
                                           | user_id       |
                                           | content       |
                                           | created_at    |
                                           +---------------+
```

## 3. 表结构定义

### 3.1 Users 表

存储用户账户信息。

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    profile_data JSONB,
    settings JSONB,
    api_key VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### 3.2 Subscriptions 表

存储用户订阅计划信息。

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    payment_info JSONB,
    features JSONB,
    usage_limits JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 3.3 Papers 表

存储上传的论文元数据。

```sql
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500),
    authors JSONB,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_hash VARCHAR(255),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB,
    status VARCHAR(50) DEFAULT 'uploaded',
    tags TEXT[],
    doi VARCHAR(255),
    publication_info JSONB,
    extracted_text TEXT,
    embedding_id VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_papers_user_id ON papers(user_id);
CREATE INDEX idx_papers_status ON papers(status);
CREATE INDEX idx_papers_upload_date ON papers(upload_date);
CREATE INDEX idx_papers_tags ON papers USING GIN(tags);
CREATE INDEX idx_papers_metadata ON papers USING GIN(metadata);
```

### 3.4 Analysis 表

存储论文分析任务和结果。

```sql
CREATE TABLE analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    result_data JSONB,
    error_message TEXT,
    analysis_type VARCHAR(50) DEFAULT 'standard',
    parameters JSONB,
    feedback JSONB,
    processing_time INTEGER,
    version VARCHAR(50)
);

CREATE INDEX idx_analysis_paper_id ON analysis(paper_id);
CREATE INDEX idx_analysis_status ON analysis(status);
CREATE INDEX idx_analysis_created_at ON analysis(created_at);
CREATE INDEX idx_analysis_result_data ON analysis USING GIN(result_data);
```

### 3.5 Reports 表

存储生成的报告信息。

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    format VARCHAR(50) DEFAULT 'pdf',
    file_path VARCHAR(500),
    shared_with JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    access_count INTEGER DEFAULT 0,
    template_id VARCHAR(255),
    custom_sections JSONB
);

CREATE INDEX idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX idx_reports_created_at ON reports(created_at);
```

### 3.6 Comments 表

存储报告评论和反馈。

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    is_resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_comments_report_id ON comments(report_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
```

### 3.7 API_Keys 表

存储API访问密钥。

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    permissions JSONB,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

### 3.8 Audit_Logs 表

存储系统审计日志。

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(255) NOT NULL,
    entity_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    details JSONB
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_entity_type_id ON audit_logs(entity_type, entity_id);
```

## 4. 向量数据库设计

### 4.1 论文嵌入向量

使用Pinecone或类似向量数据库存储论文的嵌入向量，用于语义搜索和相似度匹配。

```
索引名称: paper_embeddings
维度: 1536 (基于OpenAI嵌入模型)
元数据字段:
  - paper_id: UUID (关联到Papers表)
  - title: String
  - authors: String
  - upload_date: Timestamp
  - tags: Array<String>
```

### 4.2 段落嵌入向量

存储论文中各段落的嵌入向量，用于更精细的搜索和问答功能。

```
索引名称: paragraph_embeddings
维度: 1536 (基于OpenAI嵌入模型)
元数据字段:
  - paper_id: UUID (关联到Papers表)
  - paragraph_index: Integer
  - section: String
  - content: String (段落内容的前100个字符)
```

## 5. 数据迁移与版本控制

使用Alembic进行数据库迁移管理，确保数据库结构变更可追踪且可回滚。

```
migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_embedding_id_to_papers.py
│   └── ...
├── env.py
├── README
└── script.py.mako
```

## 6. 数据访问模式

### 6.1 常见查询模式

1. 获取用户上传的所有论文
```sql
SELECT * FROM papers WHERE user_id = :user_id ORDER BY upload_date DESC;
```

2. 获取论文的分析结果
```sql
SELECT a.* FROM analysis a
JOIN papers p ON a.paper_id = p.id
WHERE p.id = :paper_id AND a.status = 'completed'
ORDER BY a.completed_at DESC;
```

3. 搜索论文（基于标题和标签）
```sql
SELECT * FROM papers
WHERE (title ILIKE :search_term OR :search_term = ANY(tags))
AND (user_id = :user_id OR is_public = TRUE)
ORDER BY upload_date DESC;
```

### 6.2 数据访问层设计

使用SQLAlchemy ORM进行数据访问，实现以下模式：

1. 仓储模式 (Repository Pattern)
   - 为每个主要实体创建仓储类
   - 封装CRUD操作和常见查询

2. 单元工作模式 (Unit of Work Pattern)
   - 管理事务边界
   - 确保数据一致性

3. 数据传输对象 (DTO)
   - 在API层和数据库层之间转换数据

## 7. 性能优化策略

### 7.1 索引策略

1. 为常用查询条件创建索引
2. 使用GIN索引支持JSONB和数组字段查询
3. 定期分析查询性能，调整索引

### 7.2 分区策略

对大型表（如audit_logs）实施表分区：

```sql
CREATE TABLE audit_logs (
    id UUID NOT NULL,
    user_id UUID,
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    -- 其他字段
) PARTITION BY RANGE (timestamp);

CREATE TABLE audit_logs_y2023m01 PARTITION OF audit_logs
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE audit_logs_y2023m02 PARTITION OF audit_logs
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- 以此类推
```

### 7.3 缓存策略

1. 使用Redis缓存频繁访问的数据
   - 用户配置文件
   - 论文元数据
   - 分析结果摘要

2. 缓存失效策略
   - 基于时间的过期
   - 写操作触发的缓存更新

## 8. 数据安全

### 8.1 敏感数据加密

1. 密码使用bcrypt或Argon2算法哈希存储
2. API密钥使用单向哈希存储
3. 敏感用户数据使用应用层加密

### 8.2 数据访问控制

1. 行级安全策略
```sql
ALTER TABLE papers ENABLE ROW LEVEL SECURITY;

CREATE POLICY papers_user_access ON papers
    USING (user_id = current_user_id() OR is_public = TRUE);
```

2. 数据库角色分离
   - 应用服务角色（有限权限）
   - 管理员角色（完全权限）
   - 只读角色（用于报表和分析）

### 8.3 审计和合规

1. 使用触发器自动记录数据变更
```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs(
        user_id, action, entity_type, entity_id, details
    ) VALUES (
        current_user_id(),
        TG_OP,
        TG_TABLE_NAME,
        NEW.id,
        jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER papers_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON papers
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

## 9. 备份和恢复策略

### 9.1 备份计划

1. 每日完整备份
2. 每小时增量备份
3. 持续归档WAL日志

### 9.2 恢复流程

1. 时间点恢复 (PITR) 能力
2. 灾难恢复测试计划
3. 备份验证流程

## 10. 未来扩展考虑

1. 分布式数据库架构
   - 读写分离
   - 分片策略

2. 多租户支持
   - 架构选项：
     - 共享数据库，共享架构
     - 共享数据库，独立架构
     - 独立数据库

3. 数据仓库集成
   - 定期ETL到分析数据仓库
   - 商业智能和报表功能
