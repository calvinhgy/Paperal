# Paperal API 集成指南

## 1. 概述

本文档提供了如何与Paperal API集成的详细指南，帮助开发者将Paperal的论文分析和商业化评估功能集成到自己的应用程序中。

## 2. 入门指南

### 2.1 注册开发者账户

1. 访问 [Paperal开发者门户](https://developers.paperal.com)
2. 创建一个开发者账户
3. 登录后，导航至"API密钥"部分
4. 创建一个新的API密钥
5. 保存生成的API密钥（仅显示一次）

### 2.2 API基础信息

- **基本URL**: `https://api.paperal.com/v1`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 2.3 认证

所有API请求都需要在HTTP头部包含认证信息：

```
Authorization: Bearer YOUR_API_KEY
```

示例（使用curl）：

```bash
curl -X GET "https://api.paperal.com/v1/papers" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json"
```

## 3. 快速开始

### 3.1 上传论文并获取分析

以下是一个完整的工作流程示例，展示如何上传论文、启动分析并获取结果：

#### 步骤1：上传论文

```bash
curl -X POST "https://api.paperal.com/v1/papers" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -F "file=@path/to/paper.pdf" \
     -F "title=Optional Paper Title" \
     -F "tags=AI,Healthcare"
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "paper-uuid",
    "title": "Detected or Provided Title",
    "upload_date": "2023-06-01T12:34:56Z",
    "status": "uploaded"
  }
}
```

#### 步骤2：开始分析

```bash
curl -X POST "https://api.paperal.com/v1/papers/paper-uuid/analysis" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_type": "standard",
       "parameters": {
         "focus_areas": ["技术可行性", "市场机会", "商业模式"]
       }
     }'
```

响应：

```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "pending",
    "created_at": "2023-06-01T12:35:00Z"
  }
}
```

#### 步骤3：检查分析状态

```bash
curl -X GET "https://api.paperal.com/v1/analysis/analysis-uuid" \
     -H "Authorization: Bearer YOUR_API_KEY"
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
    "current_stage": "商业模式分析"
  }
}
```

#### 步骤4：获取分析结果

```bash
curl -X GET "https://api.paperal.com/v1/analysis/analysis-uuid/results" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "analysis-uuid",
    "paper_id": "paper-uuid",
    "status": "completed",
    "results": {
      "technical_feasibility": {
        "score": 8.5,
        "strengths": ["创新性高", "技术原理已验证"],
        "challenges": ["规模化生产难度大"]
      },
      "market_opportunities": [
        {
          "name": "医疗诊断应用",
          "market_size": "$5B",
          "growth_rate": "15% CAGR"
        }
      ],
      "business_model": {
        "recommended_models": [
          {
            "type": "SaaS",
            "revenue_streams": ["订阅", "专业服务"]
          }
        ]
      }
    }
  }
}
```

#### 步骤5：生成报告

```bash
curl -X POST "https://api.paperal.com/v1/analysis/analysis-uuid/reports" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "商业化分析报告",
       "format": "pdf"
     }'
```

响应：

```json
{
  "success": true,
  "data": {
    "report_id": "report-uuid",
    "analysis_id": "analysis-uuid",
    "status": "generating"
  }
}
```

#### 步骤6：获取报告

```bash
curl -X GET "https://api.paperal.com/v1/reports/report-uuid" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

响应：

```json
{
  "success": true,
  "data": {
    "id": "report-uuid",
    "analysis_id": "analysis-uuid",
    "title": "商业化分析报告",
    "status": "completed",
    "file_url": "https://storage.paperal.com/reports/report-uuid.pdf"
  }
}
```

## 4. SDK使用指南

### 4.1 Python SDK

#### 安装

```bash
pip install paperal-sdk
```

#### 基本用法

```python
import paperal

# 初始化客户端
client = paperal.Client(api_key="YOUR_API_KEY")

# 上传论文
paper = client.papers.upload("path/to/paper.pdf", tags=["AI", "Healthcare"])

# 开始分析
analysis = client.analysis.create(
    paper_id=paper.id,
    analysis_type="standard",
    parameters={
        "focus_areas": ["技术可行性", "市场机会", "商业模式"]
    }
)

# 等待分析完成
analysis = analysis.wait_for_completion()

# 生成报告
report = client.reports.create(
    analysis_id=analysis.id,
    title="商业化分析报告",
    format="pdf"
)

# 获取报告URL
report = report.wait_for_completion()
print(f"报告已生成: {report.file_url}")
```

### 4.2 JavaScript SDK

#### 安装

```bash
npm install paperal-sdk
```

#### 基本用法

```javascript
const Paperal = require('paperal-sdk');

// 初始化客户端
const client = new Paperal.Client('YOUR_API_KEY');

// 上传论文
async function analyzePaper() {
  try {
    // 上传论文
    const paper = await client.papers.upload({
      file: './path/to/paper.pdf',
      tags: ['AI', 'Healthcare']
    });
    
    // 开始分析
    const analysis = await client.analysis.create({
      paper_id: paper.id,
      analysis_type: 'standard',
      parameters: {
        focus_areas: ['技术可行性', '市场机会', '商业模式']
      }
    });
    
    // 等待分析完成
    const completedAnalysis = await client.analysis.waitForCompletion(analysis.id);
    
    // 生成报告
    const report = await client.reports.create({
      analysis_id: completedAnalysis.id,
      title: '商业化分析报告',
      format: 'pdf'
    });
    
    // 等待报告生成
    const completedReport = await client.reports.waitForCompletion(report.id);
    console.log(`报告已生成: ${completedReport.file_url}`);
    
  } catch (error) {
    console.error('错误:', error);
  }
}

analyzePaper();
```

## 5. API资源

### 5.1 论文 (Papers)

#### 上传论文

```
POST /papers
```

请求体（multipart/form-data）：
- `file`: PDF文件（必需）
- `title`: 论文标题（可选）
- `authors`: 作者列表，逗号分隔（可选）
- `tags`: 标签列表，逗号分隔（可选）

#### 获取论文列表

```
GET /papers
```

查询参数：
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `status`: 状态过滤
- `tags`: 标签过滤（逗号分隔）
- `search`: 搜索关键词

#### 获取论文详情

```
GET /papers/{paper_id}
```

#### 更新论文信息

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

#### 删除论文

```
DELETE /papers/{paper_id}
```

### 5.2 分析 (Analysis)

#### 开始分析

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

#### 获取分析状态

```
GET /analysis/{analysis_id}
```

#### 获取分析结果

```
GET /analysis/{analysis_id}/results
```

#### 获取用户的分析列表

```
GET /analysis
```

查询参数：
- `page`: 页码
- `limit`: 每页数量
- `status`: 状态过滤
- `paper_id`: 按论文ID过滤

### 5.3 报告 (Reports)

#### 生成报告

```
POST /analysis/{analysis_id}/reports
```

请求体：
```json
{
  "title": "报告标题",
  "format": "pdf",
  "template": "standard",
  "sections": ["executive_summary", "technical_overview", "market_analysis"]
}
```

#### 获取报告状态

```
GET /reports/{report_id}
```

#### 获取报告列表

```
GET /reports
```

查询参数：
- `page`: 页码
- `limit`: 每页数量
- `analysis_id`: 按分析ID过滤

#### 分享报告

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

## 6. 高级功能

### 6.1 批量处理

#### 批量上传论文

```
POST /papers/batch
```

请求体（multipart/form-data）：
- `files[]`: 多个PDF文件
- `metadata`: JSON字符串，包含每个文件的元数据

```json
{
  "metadata": [
    {
      "filename": "paper1.pdf",
      "title": "论文1标题",
      "tags": ["AI", "Healthcare"]
    },
    {
      "filename": "paper2.pdf",
      "title": "论文2标题",
      "tags": ["Robotics"]
    }
  ]
}
```

#### 批量分析

```
POST /analysis/batch
```

请求体：
```json
{
  "paper_ids": ["paper-id-1", "paper-id-2", "paper-id-3"],
  "analysis_type": "standard",
  "parameters": {
    "focus_areas": ["技术可行性", "市场机会"]
  }
}
```

### 6.2 自定义分析参数

分析API支持以下自定义参数：

```json
{
  "analysis_type": "custom",
  "parameters": {
    "focus_areas": ["技术可行性", "市场机会", "商业模式", "实施路径", "资源需求"],
    "industry_context": "医疗健康",
    "market_regions": ["北美", "欧洲", "亚太"],
    "time_horizon": "5年",
    "risk_tolerance": "中等",
    "investment_scale": "A轮",
    "custom_questions": [
      "这项技术如何应对行业监管挑战？",
      "与现有市场领导者相比有何竞争优势？"
    ]
  }
}
```

### 6.3 Webhook集成

#### 配置Webhook

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

#### Webhook事件格式

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

#### 验证Webhook请求

每个Webhook请求都包含一个签名头：

```
X-Paperal-Signature: sha256=...
```

使用以下代码验证签名（Python示例）：

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## 7. 错误处理

### 7.1 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      "field": "错误的字段",
      "reason": "具体原因"
    }
  }
}
```

### 7.2 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 无效的认证凭据 |
| `AUTH_TOKEN_EXPIRED` | 401 | 认证令牌已过期 |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | 权限不足 |
| `RESOURCE_NOT_FOUND` | 404 | 请求的资源不存在 |
| `VALIDATION_ERROR` | 400 | 请求数据验证失败 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出API请求限制 |
| `QUOTA_EXCEEDED` | 403 | 超出使用配额 |
| `SERVER_ERROR` | 500 | 服务器内部错误 |

### 7.3 错误处理最佳实践

1. **检查HTTP状态码**：首先检查响应的HTTP状态码
2. **解析错误信息**：从响应体中提取详细错误信息
3. **实现重试逻辑**：对于临时错误（如速率限制、服务器错误），实现指数退避重试
4. **记录详细错误**：记录完整的错误信息，便于调试
5. **优雅降级**：在API不可用时提供备用功能

示例（Python）：

```python
import time
import requests

def api_request_with_retry(url, method="GET", data=None, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            
            if response.status_code == 429:  # 速率限制
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Rate limited. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                retries += 1
                continue
                
            if response.status_code >= 500:  # 服务器错误
                wait_time = 2 ** retries
                print(f"Server error. Retrying after {wait_time} seconds")
                time.sleep(wait_time)
                retries += 1
                continue
                
            # 解析响应
            data = response.json()
            if not data.get("success", False):
                error = data.get("error", {})
                print(f"API Error: {error.get('code')} - {error.get('message')}")
                # 处理特定错误...
                return None
                
            return data.get("data")
            
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** retries
            print(f"Request failed: {e}. Retrying after {wait_time} seconds")
            time.sleep(wait_time)
            retries += 1
    
    print("Max retries reached")
    return None
```

## 8. 速率限制与配额

### 8.1 速率限制

API实施以下速率限制：

| 计划 | 限制 |
|------|------|
| 基本计划 | 60次请求/分钟 |
| 专业计划 | 300次请求/分钟 |
| 企业计划 | 1000次请求/分钟 |

超出限制时，API将返回`429 Too Many Requests`状态码，并在响应头中包含以下信息：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1623456789
```

### 8.2 使用配额

各计划的月度使用配额：

| 计划 | 论文分析数 | 报告生成数 |
|------|-----------|-----------|
| 基本计划 | 50 | 20 |
| 专业计划 | 500 | 200 |
| 企业计划 | 无限 | 无限 |

超出配额时，API将返回`403 Forbidden`状态码，错误码为`QUOTA_EXCEEDED`。

### 8.3 监控使用情况

```
GET /usage
```

响应：

```json
{
  "success": true,
  "data": {
    "plan": "professional",
    "period_start": "2023-06-01T00:00:00Z",
    "period_end": "2023-06-30T23:59:59Z",
    "quotas": {
      "paper_analysis": {
        "limit": 500,
        "used": 123,
        "remaining": 377
      },
      "report_generation": {
        "limit": 200,
        "used": 45,
        "remaining": 155
      }
    },
    "rate_limits": {
      "requests_per_minute": 300
    }
  }
}
```

## 9. 安全最佳实践

### 9.1 API密钥管理

1. **安全存储**：不要在客户端代码或版本控制系统中硬编码API密钥
2. **环境变量**：使用环境变量或安全的密钥管理服务存储API密钥
3. **最小权限**：为不同用途创建不同的API密钥，限制权限
4. **定期轮换**：定期更换API密钥
5. **监控使用**：监控API密钥的使用情况，发现异常及时处理

### 9.2 数据安全

1. **HTTPS**：始终使用HTTPS进行API通信
2. **数据最小化**：只传输必要的数据
3. **敏感数据处理**：考虑在上传前对敏感信息进行脱敏
4. **本地处理**：如果可能，考虑在本地处理敏感数据

### 9.3 用户数据处理

当处理最终用户数据时：

1. **透明度**：告知用户数据如何被使用
2. **同意**：获取用户同意
3. **访问控制**：实施适当的访问控制
4. **数据删除**：提供数据删除机制

## 10. 集成场景示例

### 10.1 研究管理系统集成

```python
# 定期分析新上传的论文
def process_new_papers(research_system_api, paperal_client):
    # 获取最近上传的论文
    new_papers = research_system_api.get_recent_papers()
    
    for paper in new_papers:
        # 下载PDF
        pdf_path = research_system_api.download_paper(paper.id)
        
        # 上传到Paperal
        paperal_paper = paperal_client.papers.upload(pdf_path)
        
        # 开始分析
        analysis = paperal_client.analysis.create(
            paper_id=paperal_paper.id,
            analysis_type="standard"
        )
        
        # 存储分析ID以便后续查询
        research_system_api.update_paper_metadata(
            paper.id, 
            {"paperal_analysis_id": analysis.id}
        )
```

### 10.2 投资筛选平台集成

```javascript
// 批量分析多篇论文并比较商业潜力
async function analyzeInvestmentOpportunities(paperIds) {
  const results = [];
  
  // 并行启动分析
  const analysisPromises = paperIds.map(paperId => 
    client.analysis.create({
      paper_id: paperId,
      analysis_type: "investment_focus",
      parameters: {
        focus_areas: ["市场机会", "技术可行性", "投资回报"],
        investment_stage: "种子轮"
      }
    })
  );
  
  const analyses = await Promise.all(analysisPromises);
  
  // 等待所有分析完成
  for (const analysis of analyses) {
    const result = await client.analysis.waitForCompletion(analysis.id);
    results.push(result);
  }
  
  // 按商业潜力评分排序
  results.sort((a, b) => 
    b.results.investment_potential.score - a.results.investment_potential.score
  );
  
  return results;
}
```

### 10.3 研究成果商业化平台

```python
# 为机构研究成果生成商业化路线图
def generate_commercialization_roadmap(paper_id, industry_focus):
    # 上传论文
    paper = client.papers.upload(f"papers/{paper_id}.pdf")
    
    # 进行深度商业化分析
    analysis = client.analysis.create(
        paper_id=paper.id,
        analysis_type="commercialization",
        parameters={
            "focus_areas": ["实施路径", "资源需求", "市场进入策略"],
            "industry_context": industry_focus,
            "time_horizon": "3年"
        }
    )
    
    # 等待分析完成
    analysis = analysis.wait_for_completion()
    
    # 生成详细报告
    report = client.reports.create(
        analysis_id=analysis.id,
        title=f"{paper.title} - 商业化路线图",
        format="pdf",
        template="roadmap"
    )
    
    report = report.wait_for_completion()
    
    # 返回报告和关键里程碑
    return {
        "report_url": report.file_url,
        "key_milestones": analysis.results.implementation_path.milestones,
        "estimated_timeline": analysis.results.implementation_path.timeline,
        "resource_requirements": analysis.results.resource_requirements
    }
```

## 11. 故障排除

### 11.1 常见问题

1. **认证失败**
   - 检查API密钥是否正确
   - 确认API密钥未过期
   - 验证请求头格式是否正确

2. **上传失败**
   - 检查文件格式（必须是PDF）
   - 验证文件大小（最大50MB）
   - 确认请求使用了正确的Content-Type

3. **分析超时**
   - 大型论文可能需要更长处理时间
   - 实现轮询机制，而不是单次等待
   - 使用Webhook接收完成通知

4. **结果不符合预期**
   - 尝试调整分析参数
   - 确保PDF质量良好，文本可提取
   - 考虑提供更具体的行业上下文

### 11.2 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查请求ID**
   每个API响应都包含一个请求ID，用于故障排除：
   ```
   X-Request-ID: req_123456789
   ```

3. **测试模式**
   添加`test=true`查询参数进行测试，不消耗配额：
   ```
   POST /papers?test=true
   ```

## 12. 支持资源

- **开发者文档**：[https://developers.paperal.com/docs](https://developers.paperal.com/docs)
- **API参考**：[https://developers.paperal.com/api-reference](https://developers.paperal.com/api-reference)
- **示例代码**：[https://github.com/paperal/api-examples](https://github.com/paperal/api-examples)
- **支持邮箱**：api-support@paperal.com
- **状态页面**：[https://status.paperal.com](https://status.paperal.com)
