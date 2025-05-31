from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging

from database import get_db, init_db
from models import models, schemas
from api import auth, users, papers, analysis, reports
from core import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Paperal API",
    description="API for Paperal - 学术论文商业化分析平台",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")

# 健康检查端点
@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "healthy"}

# 包含路由器
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(papers.router, prefix="/api/papers", tags=["论文"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["分析"])
app.include_router(reports.router, prefix="/api/reports", tags=["报告"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)