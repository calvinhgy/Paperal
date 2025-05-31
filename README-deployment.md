# Paperal 部署指南

本文档提供了将 Paperal 项目部署到 AWS 的详细步骤。

## 部署选项

Paperal 提供了两种部署选项：

1. **使用 CloudFormation 自动部署** - 适合完整的生产环境部署
2. **使用 Docker Compose 本地开发和测试** - 适合开发和测试环境

## 前提条件

- AWS 账户
- 已安装 AWS CLI 并配置凭证
- 已安装 Git
- 已安装 Docker 和 Docker Compose（用于本地开发）

## 选项 1: 使用 CloudFormation 自动部署

### 步骤 1: 配置 AWS 凭证

```bash
aws configure
```

输入您的 AWS Access Key ID、Secret Access Key、默认区域和输出格式。

### 步骤 2: 运行部署脚本

```bash
chmod +x deploy-paperal.sh
./deploy-paperal.sh --key-pair YOUR_KEY_PAIR_NAME --db-password YOUR_DB_PASSWORD --region YOUR_REGION --env dev
```

参数说明：
- `--key-pair`: EC2 密钥对名称，用于 SSH 访问
- `--db-password`: PostgreSQL 数据库密码
- `--region`: AWS 区域（可选，默认为 us-east-1）
- `--env`: 环境名称（可选，默认为 dev）
- `--stack-name`: CloudFormation 堆栈名称（可选，默认为 paperal）

### 步骤 3: 部署前端

脚本执行完成后，按照输出的说明部署前端：

```bash
cd Paperal/src/frontend
npm install
npm run build
aws s3 sync build/ s3://YOUR_FRONTEND_BUCKET
```

### 步骤 4: 访问应用

部署完成后，您可以通过以下 URL 访问应用：
- 后端 API: http://YOUR_EC2_INSTANCE_DNS:8000
- 前端应用: https://YOUR_CLOUDFRONT_DOMAIN

## 选项 2: 使用 Docker Compose 本地开发

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/Calvinhgy/Paperal.git
cd Paperal
```

### 步骤 2: 启动 Docker Compose

```bash
docker-compose up -d
```

这将启动以下服务：
- PostgreSQL 数据库
- Redis 缓存
- 后端 API 服务
- Celery 工作进程
- 前端应用

### 步骤 3: 访问应用

- 后端 API: http://localhost:8000
- 前端应用: http://localhost:3000

## 使用 GitHub Actions 自动部署

项目包含了 GitHub Actions 工作流配置，可以在推送到 main 分支时自动部署。

### 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `AWS_ACCESS_KEY_ID`: AWS 访问密钥 ID
- `AWS_SECRET_ACCESS_KEY`: AWS 访问密钥
- `AWS_REGION`: AWS 区域
- `AWS_ACCOUNT_ID`: AWS 账户 ID
- `FRONTEND_BUCKET`: 前端 S3 存储桶名称
- `CLOUDFRONT_DISTRIBUTION_ID`: CloudFront 分发 ID

## 架构概述

部署后的架构包括：

1. **前端**:
   - 托管在 S3 存储桶中
   - 通过 CloudFront 分发
   - 使用 React.js 和 TypeScript 构建

2. **后端**:
   - 运行在 EC2 实例上
   - 使用 FastAPI 构建 RESTful API
   - Celery 工作进程处理异步任务

3. **数据库**:
   - Amazon RDS PostgreSQL 数据库

4. **缓存**:
   - Amazon ElastiCache Redis 缓存

5. **存储**:
   - Amazon S3 存储桶用于存储上传的 PDF 文件

## 监控和日志

- EC2 实例日志位于 `/var/log/cloud-init-output.log`
- 应用程序日志可通过 CloudWatch 访问
- 数据库和缓存监控可通过 AWS 控制台访问

## 故障排除

1. **无法连接到后端 API**:
   - 检查 EC2 安全组是否允许端口 8000 的入站流量
   - 检查 EC2 实例是否正在运行
   - 查看 EC2 实例日志: `ssh ec2-user@YOUR_EC2_IP "cat /var/log/cloud-init-output.log"`

2. **数据库连接问题**:
   - 检查数据库安全组是否允许来自 EC2 实例的连接
   - 验证数据库凭证是否正确

3. **前端无法加载**:
   - 检查 S3 存储桶策略是否正确
   - 验证 CloudFront 分发是否正确配置
   - 检查前端构建是否已上传到 S3

## 扩展和优化

1. **自动扩展**:
   - 将 EC2 实例放入自动扩展组
   - 配置基于负载的扩展策略

2. **高可用性**:
   - 在多个可用区部署应用程序
   - 启用 RDS 多可用区部署

3. **安全性**:
   - 配置 WAF 以保护 API 端点
   - 实施 HTTPS 和 TLS 1.2+
   - 定期轮换数据库凭证

4. **性能优化**:
   - 配置 CloudFront 缓存策略
   - 优化数据库查询和索引
   - 实施 API 响应缓存
