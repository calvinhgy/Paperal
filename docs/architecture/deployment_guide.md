# Paperal 部署指南

## 1. 概述

本文档提供了Paperal系统的部署指南，包括开发环境、测试环境和生产环境的部署步骤和最佳实践。Paperal采用容器化部署方式，使用Docker和Kubernetes来确保系统的可扩展性、可靠性和一致性。

## 2. 系统要求

### 2.1 开发环境

- **操作系统**: Linux, macOS, 或 Windows 10/11 (WSL2推荐)
- **CPU**: 4核心或更多
- **内存**: 至少8GB RAM
- **存储**: 至少20GB可用空间
- **软件**:
  - Docker Desktop 4.0+
  - Node.js 16+
  - Python 3.9+
  - Git

### 2.2 测试环境

- **基础设施**:
  - Kubernetes集群 (1-3节点)
  - 节点规格: 4vCPU, 16GB RAM
  - 存储: 100GB SSD
  - 网络: 内部负载均衡器

### 2.3 生产环境

- **基础设施**:
  - Kubernetes集群 (至少3节点，多可用区)
  - 节点规格: 8vCPU, 32GB RAM
  - 存储: 500GB SSD (分布式存储推荐)
  - 网络: 外部负载均衡器，CDN
  - 数据库: 托管PostgreSQL服务 (高可用配置)
  - 缓存: 托管Redis服务 (高可用配置)
  - 对象存储: S3兼容存储服务

## 3. 本地开发环境设置

### 3.1 前提条件安装

```bash
# 安装Node.js和npm (使用nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
nvm install 16
nvm use 16

# 安装Python和依赖
python -m venv venv
source venv/bin/activate
pip install -r src/backend/requirements.txt

# 安装Docker (根据操作系统不同，步骤可能有所不同)
# 参考: https://docs.docker.com/get-docker/
```

### 3.2 本地开发环境启动

```bash
# 克隆代码库
git clone https://github.com/your-org/paperal.git
cd paperal

# 启动本地开发环境
docker-compose -f docker-compose.dev.yml up -d

# 启动前端开发服务器
cd src/frontend
npm install
npm run dev

# 启动后端开发服务器
cd src/backend
uvicorn main:app --reload --port 8000
```

### 3.3 本地环境配置

创建`.env.local`文件，包含以下环境变量:

```
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=paperal
DB_USER=postgres
DB_PASSWORD=devpassword

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key

# 存储配置
STORAGE_TYPE=local
STORAGE_PATH=./storage
```

## 4. Docker容器化

### 4.1 Dockerfile - 前端

```dockerfile
# src/frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Dockerfile - 后端

```dockerfile
# src/backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./src/frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - paperal-network

  backend:
    build: ./src/backend
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=paperal
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STORAGE_TYPE=s3
      - S3_BUCKET=${S3_BUCKET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - paperal-network

  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=paperal
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - paperal-network

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - paperal-network

  worker:
    build: ./src/backend
    command: celery -A tasks worker --loglevel=info
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=paperal
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STORAGE_TYPE=s3
      - S3_BUCKET=${S3_BUCKET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - paperal-network

networks:
  paperal-network:

volumes:
  postgres-data:
  redis-data:
```

## 5. Kubernetes部署

### 5.1 Kubernetes资源定义

#### 5.1.1 命名空间

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: paperal
```

#### 5.1.2 ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: paperal-config
  namespace: paperal
data:
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "paperal"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  STORAGE_TYPE: "s3"
  S3_BUCKET: "paperal-storage"
  LOG_LEVEL: "info"
```

#### 5.1.3 Secret

```yaml
# k8s/secret.yaml (使用kubectl create secret替代)
apiVersion: v1
kind: Secret
metadata:
  name: paperal-secrets
  namespace: paperal
type: Opaque
data:
  DB_PASSWORD: base64_encoded_password
  OPENAI_API_KEY: base64_encoded_api_key
  AWS_ACCESS_KEY_ID: base64_encoded_access_key
  AWS_SECRET_ACCESS_KEY: base64_encoded_secret_key
```

#### 5.1.4 后端部署

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: paperal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/paperal-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: paperal-config
        - secretRef:
            name: paperal-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 5.1.5 前端部署

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: paperal
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/paperal-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 5.1.6 Worker部署

```yaml
# k8s/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: paperal
spec:
  replicas: 2
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
      - name: worker
        image: your-registry/paperal-backend:latest
        command: ["celery", "-A", "tasks", "worker", "--loglevel=info"]
        envFrom:
        - configMapRef:
            name: paperal-config
        - secretRef:
            name: paperal-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### 5.1.7 服务

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: paperal
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: paperal
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: paperal
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: paperal
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

#### 5.1.8 Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: paperal-ingress
  namespace: paperal
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - app.paperal.com
    - api.paperal.com
    secretName: paperal-tls
  rules:
  - host: app.paperal.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: api.paperal.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### 5.2 部署步骤

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 创建ConfigMap
kubectl apply -f k8s/configmap.yaml

# 创建Secret (替换实际值)
kubectl create secret generic paperal-secrets \
  --namespace=paperal \
  --from-literal=DB_PASSWORD=your_db_password \
  --from-literal=OPENAI_API_KEY=your_openai_api_key \
  --from-literal=AWS_ACCESS_KEY_ID=your_aws_access_key \
  --from-literal=AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# 部署数据库和Redis (使用StatefulSet或托管服务)
# 这里假设使用托管服务，所以不包括部署步骤

# 部署后端、前端和Worker
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml

# 创建服务
kubectl apply -f k8s/services.yaml

# 配置Ingress
kubectl apply -f k8s/ingress.yaml

# 验证部署
kubectl get pods -n paperal
kubectl get services -n paperal
kubectl get ingress -n paperal
```

## 6. CI/CD 流水线

### 6.1 GitHub Actions工作流

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r src/backend/requirements-dev.txt
    
    - name: Run tests
      run: |
        cd src/backend
        pytest
    
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install frontend dependencies
      run: |
        cd src/frontend
        npm ci
    
    - name: Run frontend tests
      run: |
        cd src/frontend
        npm test

  build-and-push:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1
    
    - name: Login to DockerHub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v2
      with:
        context: ./src/backend
        push: true
        tags: your-registry/paperal-backend:latest,your-registry/paperal-backend:${{ github.sha }}
    
    - name: Build and push frontend
      uses: docker/build-push-action@v2
      with:
        context: ./src/frontend
        push: true
        tags: your-registry/paperal-frontend:latest,your-registry/paperal-frontend:${{ github.sha }}

  deploy:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v1
    
    - name: Set Kubernetes context
      uses: azure/k8s-set-context@v1
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Update deployment images
      run: |
        kubectl set image deployment/backend backend=your-registry/paperal-backend:${{ github.sha }} -n paperal
        kubectl set image deployment/frontend frontend=your-registry/paperal-frontend:${{ github.sha }} -n paperal
        kubectl set image deployment/worker worker=your-registry/paperal-backend:${{ github.sha }} -n paperal
    
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/backend -n paperal
        kubectl rollout status deployment/frontend -n paperal
        kubectl rollout status deployment/worker -n paperal
```

## 7. 监控与日志

### 7.1 Prometheus配置

```yaml
# k8s/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
          action: replace
          regex: ([^:]+)(?::\d+)?;(\d+)
          replacement: $1:$2
          target_label: __address__
        - source_labels: [__meta_kubernetes_namespace]
          action: replace
          target_label: kubernetes_namespace
        - source_labels: [__meta_kubernetes_pod_name]
          action: replace
          target_label: kubernetes_pod_name
```

### 7.2 Grafana仪表板

创建以下Grafana仪表板:

1. 系统概览
   - API请求率
   - 错误率
   - 响应时间
   - 资源使用率

2. 业务指标
   - 活跃用户数
   - 论文上传数
   - 分析完成数
   - 报告生成数

3. 资源监控
   - CPU使用率
   - 内存使用率
   - 网络流量
   - 磁盘使用率

### 7.3 ELK堆栈配置

使用Filebeat收集容器日志，发送到Elasticsearch，并通过Kibana可视化:

```yaml
# k8s/filebeat-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: logging
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*.log
      processors:
        - add_kubernetes_metadata:
            host: ${NODE_NAME}
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
    
    output.elasticsearch:
      hosts: ["elasticsearch-service:9200"]
      index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"
```

## 8. 备份与恢复

### 8.1 数据库备份

```bash
# 创建定时备份的CronJob
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: paperal
spec:
  schedule: "0 1 * * *"  # 每天凌晨1点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:14
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres-service -U postgres -d paperal -F c -f /backup/paperal-\$(date +%Y%m%d).dump
              aws s3 cp /backup/paperal-\$(date +%Y%m%d).dump s3://paperal-backups/
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: paperal-secrets
                  key: DB_PASSWORD
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: paperal-secrets
                  key: AWS_ACCESS_KEY_ID
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: paperal-secrets
                  key: AWS_SECRET_ACCESS_KEY
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            emptyDir: {}
          restartPolicy: OnFailure
EOF
```

### 8.2 数据库恢复

```bash
# 从备份恢复数据库
kubectl run postgres-restore --rm -it --image=postgres:14 --namespace=paperal -- /bin/bash

# 在容器内执行
aws s3 cp s3://paperal-backups/paperal-20230601.dump /tmp/
pg_restore -h postgres-service -U postgres -d paperal -c /tmp/paperal-20230601.dump
```

## 9. 安全最佳实践

### 9.1 网络安全

1. 使用网络策略限制Pod间通信
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: paperal
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 9.2 Secret管理

1. 使用外部Secret管理系统 (如HashiCorp Vault)
2. 定期轮换Secret
3. 限制Secret访问权限

### 9.3 容器安全

1. 使用非root用户运行容器
2. 实施容器镜像扫描
3. 使用只读文件系统
4. 限制容器权限

## 10. 故障排除

### 10.1 常见问题

1. **Pod启动失败**
   - 检查日志: `kubectl logs <pod-name> -n paperal`
   - 检查事件: `kubectl describe pod <pod-name> -n paperal`
   - 检查资源限制: `kubectl top pods -n paperal`

2. **数据库连接问题**
   - 验证Secret: `kubectl get secret paperal-secrets -n paperal -o yaml`
   - 检查网络策略: `kubectl get networkpolicy -n paperal`
   - 测试连接: `kubectl exec -it <pod-name> -n paperal -- psql -h postgres-service -U postgres -d paperal`

3. **API响应缓慢**
   - 检查负载: `kubectl top pods -n paperal`
   - 检查日志中的慢查询
   - 考虑扩展副本数: `kubectl scale deployment backend --replicas=5 -n paperal`

### 10.2 日志收集

```bash
# 收集特定Pod的日志
kubectl logs <pod-name> -n paperal > pod.log

# 收集所有后端Pod的日志
kubectl logs -l app=backend -n paperal > backend.log

# 收集最近1小时的日志
kubectl logs --since=1h <pod-name> -n paperal > recent.log
```

## 11. 扩展策略

### 11.1 水平Pod自动扩展

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: paperal
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 11.2 垂直Pod自动扩展

使用Kubernetes Vertical Pod Autoscaler (VPA) 自动调整资源请求和限制。

## 12. 灾难恢复计划

### 12.1 灾难恢复策略

1. **数据备份**
   - 每日数据库完整备份
   - 每小时增量备份
   - 跨区域备份存储

2. **恢复流程**
   - 定义RTO (恢复时间目标) 和 RPO (恢复点目标)
   - 文档化恢复步骤
   - 定期测试恢复流程

3. **多区域部署**
   - 考虑在多个AWS区域部署
   - 使用Route 53进行故障转移

### 12.2 业务连续性计划

1. **高可用性设计**
   - 无单点故障
   - 自动故障转移
   - 负载均衡

2. **事件响应计划**
   - 定义严重性级别
   - 建立升级流程
   - 指定关键联系人

## 13. 结论

本部署指南提供了Paperal系统从开发到生产的完整部署流程。通过遵循这些最佳实践，可以确保系统的可靠性、安全性和可扩展性。随着系统的发展，应定期审查和更新部署策略，以适应不断变化的需求和技术环境。
