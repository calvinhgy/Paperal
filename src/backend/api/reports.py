from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import get_db
from models import models, schemas
from core import security
from services import report_service

router = APIRouter()

@router.get("", response_model=schemas.DataResponse)
async def list_reports(
    page: int = 1,
    limit: int = 20,
    analysis_id: Optional[uuid.UUID] = None,
    paper_id: Optional[uuid.UUID] = None,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    reports, total = report_service.get_reports(
        db, 
        user_id=current_user.id, 
        page=page, 
        limit=limit, 
        analysis_id=analysis_id,
        paper_id=paper_id
    )
    
    # 构建分页元数据
    pagination = {
        "total": total,
        "count": len(reports),
        "per_page": limit,
        "current_page": page,
        "total_pages": (total + limit - 1) // limit
    }
    
    return {
        "success": True,
        "data": reports,
        "meta": {"pagination": pagination}
    }

@router.get("/{report_id}", response_model=schemas.DataResponse)
async def get_report(
    report_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取报告详情"""
    report = report_service.get_report(db, report_id, current_user.id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": report
    }

@router.patch("/{report_id}", response_model=schemas.DataResponse)
async def update_report(
    report_id: uuid.UUID,
    report_update: schemas.ReportUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新报告信息"""
    report = report_service.update_report(db, report_id, current_user.id, report_update)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": report
    }

@router.post("/{report_id}/share", response_model=schemas.DataResponse)
async def share_report(
    report_id: uuid.UUID,
    share_create: schemas.ShareCreate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """分享报告"""
    # 检查报告是否存在且属于当前用户
    report = report_service.get_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    # 创建分享链接
    share = report_service.share_report(db, report_id, share_create)
    
    return {
        "success": True,
        "data": share
    }

@router.post("/{report_id}/comments", response_model=schemas.DataResponse)
async def add_comment(
    report_id: uuid.UUID,
    comment_create: schemas.CommentBase,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加评论"""
    # 检查报告是否存在且当前用户有权访问
    report = report_service.get_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    # 创建评论
    comment = report_service.add_comment(
        db, 
        report_id=report_id, 
        user_id=current_user.id, 
        content=comment_create.content
    )
    
    return {
        "success": True,
        "data": comment
    }

@router.get("/{report_id}/comments", response_model=schemas.DataResponse)
async def get_comments(
    report_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取报告评论"""
    # 检查报告是否存在且当前用户有权访问
    report = report_service.get_report(db, report_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    # 获取评论
    comments = report_service.get_comments(db, report_id)
    
    return {
        "success": True,
        "data": comments
    }