# Paperal 部署文件

本目录包含了 Paperal 项目的所有部署相关文件。

## 文件说明

- `paperal-cloudformation.yaml` - AWS CloudFormation 模板，用于自动创建所有必要的 AWS 资源
- `deploy-paperal.sh` - 部署脚本，简化 CloudFormation 部署过程
- `Dockerfile.backend` - 后端 Docker 镜像构建文件
- `Dockerfile.frontend` - 前端 Docker 镜像构建文件
- `nginx.conf` - Nginx 配置文件，用于前端服务
- `docker-compose.yml` - Docker Compose 配置，用于本地开发和测试
- `README-deployment.md` - 详细的部署指南

## 部署方法

请参考 `README-deployment.md` 文件获取详细的部署说明。

### 快速开始

#### 使用 CloudFormation 部署到 AWS

```bash
# 配置 AWS 凭证
aws configure

# 运行部署脚本
./deploy-paperal.sh --key-pair YOUR_KEY_PAIR_NAME --db-password YOUR_DB_PASSWORD
```

#### 使用 Docker Compose 本地开发

```bash
# 启动所有服务
docker-compose up -d

# 访问应用
# 后端 API: http://localhost:8000
# 前端应用: http://localhost:3000
```

## CI/CD 配置

项目根目录下的 `.github/workflows/deploy.yml` 文件包含了 GitHub Actions 工作流配置，用于自动部署。
