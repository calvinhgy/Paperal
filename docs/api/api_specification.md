# Paperal API 规范

## 1. 概述

Paperal API 是一个RESTful API，提供对论文上传、分析和报告生成等功能的编程访问。API使用JSON作为数据交换格式，并使用标准HTTP方法和状态码。

### 1.1 基本URL

```
https://api.paperal.com/v1
```

### 1.2 认证

API使用Bearer Token认证。在每个请求的头部包含以下字段：

```
Authorization: Bearer {your_api_key}
```

### 1.3 请求格式

- 内容类型: `application/json`
- 字符编码: UTF-8

### 1.4 响应格式

所有API响应都使用JSON格式，并包含以下基本结构：

```json
{
  "success": true,
  "data": {},
  "meta": {
    "pagination": {}
  }
}
```

或者在出错时：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {}
  }
}
```

### 1.5 分页

列表类API支持分页，使用以下查询参数：

- `page`: 页码，默认为1
- `limit`: 每页项目数，默认为20，最大为100

分页信息在响应的`meta.pagination`字段中返回：

```json
{
  "meta": {
    "pagination": {
      "total": 100,
      "count": 20,
      "per_page": 20,
      "current_page": 1,
      "total_pages": 5,
      "links": {
        "next": "https://api.paperal.com/v1/papers?page=2",
        "prev": null
      }
    }
  }
}
```

## 2. API端点

### 2.1 认证API

#### 2.1.1 获取访问令牌

```
POST /auth/token
```

请求体：

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

#### 2.1.2 刷新访问令牌

```
POST /auth/refresh
```

请求头：

```
Authorization: Bearer {refresh_token}
```

响应：

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### 2.2 用户API

#### 2.2.1 获取当前用户信息

```
GET /users/me
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "organization": "Acme Inc",
    "created_at": "2023-01-01T00:00:00Z",
    "subscription": {
      "plan": "premium",
      "status": "active",
      "expires_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### 2.2.2 更新用户信息

```
PATCH /users/me
```

请求体：

```json
{
  "name": "John Smith",
  "organization": "New Company"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Smith",
    "organization": "New Company",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### 2.3 论文API

#### 2.3.1 上传论文

```
POST /papers
```

请求体（multipart/form-data）：

```
file: [PDF文件]
title: 论文标题 (可选)
authors: 作者1, 作者2 (可选)
tags: 标签1, 标签2 (可选)
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "paper-uuid",
    "title": "检测到的标题或提供的标题",
    "authors": ["作者1", "作者2"],
    "upload_date": "2023-06-01T12:34:56Z",
    "file_size": 1234567,
    "status": "uploaded",
    "tags": ["标签1", "标签2"]
  }
}
```

#### 2.3.2 获取论文列表

```
GET /papers
```

查询参数：

- `page`: 页码
- `limit`: 每页数量
- `status`: 状态过滤（uploaded, analyzing, completed）
- `tags`: 标签过滤（逗号分隔）
- `search`: 搜索关键词

响应：

```json
{
  "success": true,
  "data": [
    {
      "id": "paper-uuid-1",
      "title": "论文标题1",
      "authors": ["作者1", "作者2"],
      "upload_date": "2023-06-01T12:34:56Z",
      "status": "completed",
      "tags": ["AI", "机器学习"]
    },
    {
      "id": "paper-uuid-2",
      "title": "论文标题2",
      "authors": ["作者3"],
      "upload_date": "2023-06-02T10:11:12Z",
      "status": "analyzing",
      "tags": ["生物技术"]
    }
  ],
  "meta": {
    "pagination": {
      "total": 42,
      "count": 2,
      "per_page": 2,
      "current_page": 1,
      "total_pages": 21
    }
  }
}
```

#### 2.3.3 获取论文详情

```
GET /papers/{paper_id}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "paper-uuid",
    "title": "论文标题",
    "authors": ["作者1", "作者2"],
    "upload_date": "2023-06-01T12:34:56Z",
    "file_size": 1234567,
    "status": "completed",
    "tags": ["标签1", "标签2"],
    "metadata": {
      "doi": "10.1234/abcd.5678",
      "publication": "期刊名称",
      "publication_date": "2023-01-15",
      "abstract": "论文摘要..."
    },
    "file_url": "https://storage.paperal.com/papers/paper-uuid.pdf"
  }
}
```

#### 2.3.4 更新论文信息

```
PATCH /papers/{paper_id}
```

请求体：

```json
{
  "title": "更新的标题",
  "tags": ["新标签1", "新标签2"]
}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "paper-uuid",
    "title": "更新的标题",
    "authors": ["作者1", "作者2"],
    "upload_date": "2023-06-01T12:34:56Z",
    "status": "completed",
    "tags": ["新标签1", "新标签2"]
  }
}
```

#### 2.3.5 删除论文

```
DELETE /papers/{paper_id}
```

响应：

```json
{
  "success": true,
  "data": {
    "message": "论文已成功删除"
  }
}
```

### 2.4 分析API

#### 2.4.1 开始论文分析

```
POST /papers/{paper_id}/analysis
```

请求体：

```json
{
  "analysis_type": "standard",
  "parameters": {
    "focus_areas": ["技术可行性", "市场机会", "商业模式"],
    "industry_context": "医疗健康"
  }
}
```

响应：

```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "pending",
    "created_at": "2023-06-05T09:10:11Z",
    "estimated_completion_time": "2023-06-05T09:20:11Z"
  }
}
```

#### 2.4.2 获取分析状态

```
GET /analysis/{analysis_id}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "processing",
    "progress": 65,
    "created_at": "2023-06-05T09:10:11Z",
    "started_at": "2023-06-05T09:10:15Z",
    "estimated_completion_time": "2023-06-05T09:20:11Z",
    "current_stage": "商业模式分析"
  }
}
```

#### 2.4.3 获取分析结果

```
GET /analysis/{analysis_id}/results
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "completed",
    "created_at": "2023-06-05T09:10:11Z",
    "completed_at": "2023-06-05T09:18:30Z",
    "results": {
      "technical_feasibility": {
        "score": 8.5,
        "maturity_level": "TRL 4",
        "strengths": ["创新性高", "技术原理已验证"],
        "challenges": ["规模化生产难度大", "成本较高"],
        "details": "..."
      },
      "market_opportunities": {
        "potential_applications": [
          {
            "name": "应用场景1",
            "market_size": "$5B",
            "growth_rate": "15% CAGR",
            "target_customers": ["医院", "诊所"],
            "details": "..."
          },
          {
            "name": "应用场景2",
            "market_size": "$2B",
            "growth_rate": "22% CAGR",
            "target_customers": ["制药公司"],
            "details": "..."
          }
        ]
      },
      "business_model": {
        "recommended_models": [
          {
            "type": "SaaS",
            "revenue_streams": ["订阅", "专业服务"],
            "key_partners": ["云服务提供商", "数据提供商"],
            "details": "..."
          }
        ]
      },
      "implementation_path": {
        "timeline": {
          "phase1": {
            "duration": "6个月",
            "key_activities": ["概念验证", "市场验证"],
            "resources": "..."
          },
          "phase2": {
            "duration": "12个月",
            "key_activities": ["产品开发", "初始客户"],
            "resources": "..."
          }
        }
      },
      "resource_requirements": {
        "funding": {
          "seed": "$500K",
          "series_a": "$3M"
        },
        "team": ["技术专家", "产品经理", "市场营销"],
        "details": "..."
      }
    }
  }
}
```

### 2.5 报告API

#### 2.5.1 生成报告

```
POST /analysis/{analysis_id}/reports
```

请求体：

```json
{
  "title": "商业化分析报告：论文标题",
  "format": "pdf",
  "template": "standard",
  "sections": ["executive_summary", "technical_overview", "market_analysis", "business_model", "implementation", "resources", "risks", "conclusion"]
}
```

响应：

```json
{
  "success": true,
  "data": {
    "report_id": "report-uuid",
    "analysis_id": "analysis-uuid",
    "status": "generating",
    "created_at": "2023-06-05T10:15:00Z",
    "estimated_completion_time": "2023-06-05T10:16:30Z"
  }
}
```

#### 2.5.2 获取报告状态

```
GET /reports/{report_id}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "report-uuid",
    "analysis_id": "analysis-uuid",
    "title": "商业化分析报告：论文标题",
    "status": "completed",
    "format": "pdf",
    "created_at": "2023-06-05T10:15:00Z",
    "completed_at": "2023-06-05T10:16:25Z",
    "file_url": "https://storage.paperal.com/reports/report-uuid.pdf"
  }
}
```

#### 2.5.3 获取报告列表

```
GET /reports
```

查询参数：

- `page`: 页码
- `limit`: 每页数量
- `paper_id`: 按论文ID过滤

响应：

```json
{
  "success": true,
  "data": [
    {
      "id": "report-uuid-1",
      "analysis_id": "analysis-uuid-1",
      "paper_id": "paper-uuid-1",
      "title": "商业化分析报告：论文标题1",
      "format": "pdf",
      "created_at": "2023-06-05T10:15:00Z",
      "status": "completed"
    },
    {
      "id": "report-uuid-2",
      "analysis_id": "analysis-uuid-2",
      "paper_id": "paper-uuid-2",
      "title": "商业化分析报告：论文标题2",
      "format": "docx",
      "created_at": "2023-06-06T11:22:33Z",
      "status": "completed"
    }
  ],
  "meta": {
    "pagination": {
      "total": 15,
      "count": 2,
      "per_page": 2,
      "current_page": 1,
      "total_pages": 8
    }
  }
}
```

#### 2.5.4 分享报告

```
POST /reports/{report_id}/share
```

请求体：

```json
{
  "access_type": "link",
  "expires_at": "2023-07-05T00:00:00Z",
  "recipients": ["colleague@example.com"]
}
```

响应：

```json
{
  "success": true,
  "data": {
    "share_id": "share-uuid",
    "share_url": "https://paperal.com/s/abcdef123456",
    "access_type": "link",
    "expires_at": "2023-07-05T00:00:00Z"
  }
}
```

## 3. 错误码

| 错误码 | 描述 |
|--------|------|
| `AUTH_INVALID_CREDENTIALS` | 无效的认证凭据 |
| `AUTH_TOKEN_EXPIRED` | 认证令牌已过期 |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 权限不足 |
| `RESOURCE_NOT_FOUND` | 请求的资源不存在 |
| `RESOURCE_ALREADY_EXISTS` | 资源已存在 |
| `VALIDATION_ERROR` | 请求数据验证失败 |
| `RATE_LIMIT_EXCEEDED` | 超出API请求限制 |
| `SUBSCRIPTION_REQUIRED` | 需要有效订阅 |
| `QUOTA_EXCEEDED` | 超出使用配额 |
| `SERVER_ERROR` | 服务器内部错误 |

## 4. 速率限制

API实施以下速率限制：

- 基本计划: 60次请求/分钟
- 专业计划: 300次请求/分钟
- 企业计划: 1000次请求/分钟

超出限制时，API将返回`429 Too Many Requests`状态码，并在响应头中包含以下信息：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1623456789
```

## 5. 版本控制

API使用URL路径中的版本号进行版本控制。当前版本为`v1`。

重大更改将通过新版本号发布，而不会破坏现有API。旧版本将在新版本发布后至少维护12个月。

## 6. Webhook

Paperal API支持Webhook，用于接收事件通知。

### 6.1 配置Webhook

```
POST /webhooks
```

请求体：

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["paper.uploaded", "analysis.completed", "report.generated"],
  "secret": "your_webhook_secret"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "webhook-uuid",
    "url": "https://your-server.com/webhook",
    "events": ["paper.uploaded", "analysis.completed", "report.generated"],
    "created_at": "2023-06-10T12:00:00Z",
    "status": "active"
  }
}
```

### 6.2 Webhook事件格式

```json
{
  "id": "event-uuid",
  "type": "analysis.completed",
  "created_at": "2023-06-05T09:18:30Z",
  "data": {
    "analysis_id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "completed"
  }
}
```

### 6.3 支持的事件类型

| 事件类型 | 描述 |
|---------|------|
| `user.created` | 新用户创建 |
| `paper.uploaded` | 论文上传完成 |
| `paper.deleted` | 论文被删除 |
| `analysis.started` | 分析开始 |
| `analysis.completed` | 分析完成 |
| `analysis.failed` | 分析失败 |
| `report.generated` | 报告生成完成 |
| `report.shared` | 报告被分享 |

## 7. SDK

Paperal提供以下编程语言的官方SDK：

- Python: `pip install paperal-sdk`
- JavaScript: `npm install paperal-sdk`

SDK文档和示例可在以下位置找到：

- [Python SDK文档](https://docs.paperal.com/sdk/python)
- [JavaScript SDK文档](https://docs.paperal.com/sdk/javascript)

## 8. 示例

### 8.1 上传论文并分析

```python
import paperal

# 初始化客户端
client = paperal.Client(api_key="your_api_key")

# 上传论文
paper = client.papers.upload("path/to/paper.pdf", tags=["AI", "机器学习"])

# 开始分析
analysis = client.analysis.create(
    paper_id=paper.id,
    analysis_type="standard",
    parameters={
        "focus_areas": ["技术可行性", "市场机会", "商业模式"],
        "industry_context": "医疗健康"
    }
)

# 等待分析完成
analysis = analysis.wait_for_completion()

# 生成报告
report = client.reports.create(
    analysis_id=analysis.id,
    title="商业化分析报告：" + paper.title,
    format="pdf"
)

# 获取报告URL
report = report.wait_for_completion()
print(f"报告已生成: {report.file_url}")
```

### 8.2 获取所有已完成的分析

```javascript
const Paperal = require('paperal-sdk');

// 初始化客户端
const client = new Paperal.Client('your_api_key');

// 获取所有已完成的分析
async function getCompletedAnalyses() {
  let page = 1;
  const allAnalyses = [];
  
  while (true) {
    const response = await client.analysis.list({
      status: 'completed',
      page: page,
      limit: 50
    });
    
    allAnalyses.push(...response.data);
    
    if (page >= response.meta.pagination.total_pages) {
      break;
    }
    
    page++;
  }
  
  return allAnalyses;
}

getCompletedAnalyses()
  .then(analyses => console.log(`找到 ${analyses.length} 个已完成的分析`))
  .catch(error => console.error('错误:', error));
```
