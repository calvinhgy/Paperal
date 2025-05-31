from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import get_db
from models import models, schemas
from core import security
from services import paper_service

router = APIRouter()

@router.post("", response_model=schemas.DataResponse)
async def upload_paper(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传论文"""
    # 处理可选参数
    authors_list = authors.split(",") if authors else None
    tags_list = tags.split(",") if tags else None
    
    # 上传论文
    paper = await paper_service.upload_paper(
        db, 
        current_user.id, 
        file, 
        title=title, 
        authors=authors_list, 
        tags=tags_list
    )
    
    return {
        "success": True,
        "data": paper
    }

@router.get("", response_model=schemas.DataResponse)
async def list_papers(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取论文列表"""
    # 处理标签过滤
    tags_list = tags.split(",") if tags else None
    
    # 获取论文列表
    papers, total = paper_service.get_papers(
        db, 
        user_id=current_user.id, 
        page=page, 
        limit=limit, 
        status=status, 
        tags=tags_list, 
        search=search
    )
    
    # 构建分页元数据
    pagination = {
        "total": total,
        "count": len(papers),
        "per_page": limit,
        "current_page": page,
        "total_pages": (total + limit - 1) // limit
    }
    
    return {
        "success": True,
        "data": papers,
        "meta": {"pagination": pagination}
    }

@router.get("/{paper_id}", response_model=schemas.DataResponse)
async def get_paper(
    paper_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取论文详情"""
    paper = paper_service.get_paper(db, paper_id, current_user.id)
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": paper
    }

@router.patch("/{paper_id}", response_model=schemas.DataResponse)
async def update_paper(
    paper_id: uuid.UUID,
    paper_update: schemas.PaperUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新论文信息"""
    paper = paper_service.update_paper(db, paper_id, current_user.id, paper_update)
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": paper
    }

@router.delete("/{paper_id}", response_model=schemas.DataResponse)
async def delete_paper(
    paper_id: uuid.UUID,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除论文"""
    result = paper_service.delete_paper(db, paper_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    return {
        "success": True,
        "data": {"message": "论文已成功删除"}
    }

@router.post("/{paper_id}/analysis", response_model=schemas.DataResponse)
async def start_analysis(
    paper_id: uuid.UUID,
    analysis_create: schemas.AnalysisCreate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """开始论文分析"""
    # 检查论文是否存在且属于当前用户
    paper = paper_service.get_paper(db, paper_id, current_user.id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="论文不存在或无权访问"
        )
    
    # 创建分析任务
    from services import analysis_service
    analysis = analysis_service.create_analysis(db, paper_id, analysis_create)
    
    return {
        "success": True,
        "data": analysis
    }