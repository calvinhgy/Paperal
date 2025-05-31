import os
from dotenv import load_dotenv
from typing import List

# 加载环境变量
load_dotenv()

# API配置
API_V1_STR = "/api/v1"
PROJECT_NAME = "Paperal"

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS配置
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://paperal.com",
]

# AWS Bedrock配置
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
CLAUDE_MODEL_ID = os.getenv("CLAUDE_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

# 存储配置
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
S3_BUCKET = os.getenv("S3_BUCKET", "paperal-storage")

# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Celery配置
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL