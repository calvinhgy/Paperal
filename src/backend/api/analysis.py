from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import get_db
from models import models, schemas
from core import security
from services import analysis_service, paper_service

router = APIRouter()

@router.get("", response_model=schemas.DataResponse)
async def list_analyses(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    paper_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分析列表"""
    analyses, total = analysis_service.get_analyses(
        db, 
        user_id=current_user.id, 
        page=page, 
        limit=limit, 
        status=status, 
        paper_id=paper_id
    )
    
    # 构建分页元数据
    pagination = {
        "total": total,
        "count": len(analyses),
        "per_page": limit,
        "current_page": page,
        "total_pages": (total + limit - 1) // limit
    }
    
    return {
        "success": True,
        "data": analyses,
        "meta": {"pagination": pagination}
    }

@router.get("/{analysis_id}", response_model=schemas.DataResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分析状态"""
    analysis = analysis_service.get_analysis(db, analysis_id, current_user.id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": analysis
    }

@router.get("/{analysis_id}/results", response_model=schemas.DataResponse)
async def get_analysis_results(
    analysis_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分析结果"""
    analysis = analysis_service.get_analysis_with_results(db, analysis_id, current_user.id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析不存在或无权访问"
        )
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分析尚未完成，当前状态: {analysis.status}"
        )
    
    return {
        "success": True,
        "data": analysis
    }

@router.post("/{analysis_id}/feedback", response_model=schemas.DataResponse)
async def provide_analysis_feedback(
    analysis_id: uuid.UUID,
    feedback: dict,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """提供分析反馈"""
    analysis = analysis_service.add_feedback(db, analysis_id, current_user.id, feedback)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": {"message": "反馈已成功提交"}
    }

@router.post("/{analysis_id}/reports", response_model=schemas.DataResponse)
async def generate_report(
    analysis_id: uuid.UUID,
    report_create: schemas.ReportCreate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """生成报告"""
    # 检查分析是否存在且属于当前用户
    analysis = analysis_service.get_analysis(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析不存在或无权访问"
        )
    
    # 检查分析是否已完成
    if analysis.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分析尚未完成，当前状态: {analysis.status}"
        )
    
    # 创建报告
    from services import report_service
    report = report_service.create_report(db, analysis_id, report_create)
    
    return {
        "success": True,
        "data": report
    }