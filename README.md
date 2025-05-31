# Paperal

## 项目概述
Paperal是一个Web应用程序，旨在将学术论文转化为商业化应用机会。用户可以上传PDF格式的学术论文，系统将分析论文内容，并生成详细的商业化分析报告，包括潜在的商业应用场景、实施路径、所需资源以及可能的变现策略。

## 核心功能
- PDF学术论文上传与解析
- 论文内容的智能分析
- 商业化机会识别与评估
- 实施路径规划
- 资源需求分析
- 变现策略建议
- 报告生成与导出

## 技术栈
- 前端: React.js, TypeScript, Tailwind CSS
- 后端: Python, FastAPI
- AI模型: OpenAI GPT-4, LangChain
- PDF处理: PyPDF2, pdf.js
- 数据库: PostgreSQL
- 部署: Docker, AWS

## 项目结构
```
Paperal/
├── docs/                  # 项目文档
│   ├── requirements/      # 需求文档
│   ├── design/            # 设计文档
│   ├── architecture/      # 架构文档
│   └── api/               # API文档
├── src/                   # 源代码
│   ├── frontend/          # 前端代码
│   ├── backend/           # 后端代码
│   ├── models/            # AI模型和处理逻辑
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── e2e/               # 端到端测试
├── config/                # 配置文件
└── README.md              # 项目说明
```

## 安装与运行

### 后端

1. 安装依赖
```bash
cd src/backend
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

3. 运行开发服务器
```bash
uvicorn main:app --reload
```

### 前端

1. 安装依赖
```bash
cd src/frontend
npm install
```

2. 运行开发服务器
```bash
npm start
```

## 开发指南

### 后端开发

- API端点定义在`src/backend/api/`目录下
- 业务逻辑在`src/backend/services/`目录下
- 数据库模型在`src/backend/models/models.py`中定义
- 数据验证模型在`src/backend/models/schemas.py`中定义

### 前端开发

- 页面组件在`src/frontend/src/pages/`目录下
- 可复用组件在`src/frontend/src/components/`目录下
- API调用在`src/frontend/src/services/`目录下
- 全局状态管理在`src/frontend/src/contexts/`目录下

## 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License