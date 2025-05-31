from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid
import os
from typing import List, Optional, Tuple, Dict, Any

from models import models, schemas
from core import config
from services import analysis_service

def create_report(db: Session, analysis_id: uuid.UUID, report_create: schemas.ReportCreate):
    """创建报告"""
    # 检查分析是否存在
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        return None
    
    # 检查分析是否已完成
    if analysis.status != "completed":
        return None
    
    # 创建报告记录
    db_report = models.Report(
        analysis_id=analysis_id,
        title=report_create.title,
        created_at=datetime.utcnow(),
        format=report_create.format,
        status="generating",
        template_id=report_create.template,
        custom_sections=report_create.sections
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # 启动异步报告生成任务
    # TODO: 使用Celery任务异步处理
    # report_tasks.generate_report.delay(str(db_report.id))
    
    # 临时模拟报告生成
    generate_report(db, db_report.id)
    
    return db_report

def get_reports(
    db: Session, 
    user_id: uuid.UUID, 
    page: int = 1, 
    limit: int = 20, 
    analysis_id: Optional[uuid.UUID] = None,
    paper_id: Optional[uuid.UUID] = None
) -> Tuple[List[models.Report], int]:
    """获取报告列表"""
    # 构建查询
    query = db.query(models.Report).join(
        models.Analysis, models.Report.analysis_id == models.Analysis.id
    ).join(
        models.Paper, models.Analysis.paper_id == models.Paper.id
    ).filter(models.Paper.user_id == user_id)
    
    # 应用过滤条件
    if analysis_id:
        query = query.filter(models.Report.analysis_id == analysis_id)
    
    if paper_id:
        query = query.filter(models.Analysis.paper_id == paper_id)
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    query = query.order_by(models.Report.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    return query.all(), total

def get_report(db: Session, report_id: uuid.UUID, user_id: uuid.UUID):
    """获取报告详情"""
    return db.query(models.Report).join(
        models.Analysis, models.Report.analysis_id == models.Analysis.id
    ).join(
        models.Paper, models.Analysis.paper_id == models.Paper.id
    ).filter(
        models.Report.id == report_id,
        models.Paper.user_id == user_id
    ).first()

def update_report(db: Session, report_id: uuid.UUID, user_id: uuid.UUID, report_update: schemas.ReportUpdate):
    """更新报告信息"""
    db_report = get_report(db, report_id, user_id)
    
    if not db_report:
        return None
    
    # 更新报告信息
    update_data = report_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_report, key, value)
    
    db_report.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_report)
    
    return db_report

def share_report(db: Session, report_id: uuid.UUID, share_create: schemas.ShareCreate):
    """分享报告"""
    # 获取报告
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not db_report:
        return None
    
    # 更新分享信息
    share_id = uuid.uuid4()
    share_code = str(share_id)[:8]
    share_url = f"https://paperal.com/s/{share_code}"
    
    # 更新报告的分享信息
    if not db_report.shared_with:
        db_report.shared_with = []
    
    db_report.shared_with.append({
        "id": str(share_id),
        "type": share_create.access_type,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": share_create.expires_at.isoformat() if share_create.expires_at else None,
        "recipients": share_create.recipients,
        "url": share_url
    })
    
    db.commit()
    
    # 返回分享信息
    return schemas.Share(
        id=share_id,
        share_url=share_url,
        access_type=share_create.access_type,
        expires_at=share_create.expires_at
    )

def add_comment(db: Session, report_id: uuid.UUID, user_id: uuid.UUID, content: str):
    """添加评论"""
    # 创建评论
    db_comment = models.Comment(
        report_id=report_id,
        user_id=user_id,
        content=content,
        created_at=datetime.utcnow(),
        is_resolved=False
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

def get_comments(db: Session, report_id: uuid.UUID):
    """获取报告评论"""
    return db.query(models.Comment).filter(
        models.Comment.report_id == report_id
    ).order_by(models.Comment.created_at).all()

def generate_report(db: Session, report_id: uuid.UUID):
    """生成报告"""
    # 获取报告记录
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    
    if not db_report:
        return None
    
    try:
        # 获取分析结果
        analysis = db.query(models.Analysis).filter(models.Analysis.id == db_report.analysis_id).first()
        
        if not analysis or not analysis.result_data:
            raise Exception("分析结果不存在")
        
        # 获取论文信息
        paper = db.query(models.Paper).filter(models.Paper.id == analysis.paper_id).first()
        
        if not paper:
            raise Exception("论文不存在")
        
        # 创建存储目录
        storage_path = os.path.join(config.STORAGE_PATH, "reports")
        os.makedirs(storage_path, exist_ok=True)
        
        # 生成文件名
        file_name = f"{report_id}.{db_report.format}"
        file_path = os.path.join(storage_path, file_name)
        
        # TODO: 实际生成报告文件
        # 这里只是模拟生成报告
        with open(file_path, "w") as f:
            f.write(f"# {db_report.title}\n\n")
            f.write(f"## 论文信息\n\n")
            f.write(f"标题: {paper.title}\n")
            f.write(f"作者: {', '.join(paper.authors) if paper.authors else '未知'}\n\n")
            f.write(f"## 分析结果\n\n")
            f.write(f"技术可行性评分: {analysis.result_data.get('technical_feasibility', {}).get('score', 'N/A')}\n")
            f.write(f"主要优势: {', '.join(analysis.result_data.get('technical_feasibility', {}).get('strengths', []))}\n")
            f.write(f"主要挑战: {', '.join(analysis.result_data.get('technical_feasibility', {}).get('challenges', []))}\n\n")
            f.write(f"## 潜在应用场景\n\n")
            for app in analysis.result_data.get('market_opportunities', {}).get('potential_applications', []):
                f.write(f"- {app.get('name')}: 市场规模 {app.get('market_size')}, 增长率 {app.get('growth_rate')}\n")
        
        # 更新报告状态
        db_report.status = "completed"
        db_report.file_path = file_path
        db_report.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_report)
        
        return db_report
    
    except Exception as e:
        # 更新状态为失败
        db_report.status = "failed"
        db.commit()
        
        return None