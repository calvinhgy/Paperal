from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import UploadFile
from datetime import datetime
import uuid
import os
import hashlib
import shutil
from typing import List, Optional, Tuple

from models import models, schemas
from core import config
from utils import pdf_utils

async def upload_paper(
    db: Session, 
    user_id: uuid.UUID, 
    file: UploadFile, 
    title: Optional[str] = None, 
    authors: Optional[List[str]] = None, 
    tags: Optional[List[str]] = None
):
    """上传论文"""
    # 创建存储目录
    storage_path = os.path.join(config.STORAGE_PATH, "papers", str(user_id))
    os.makedirs(storage_path, exist_ok=True)
    
    # 生成文件名
    file_uuid = uuid.uuid4()
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{file_uuid}{file_extension}"
    file_path = os.path.join(storage_path, file_name)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 计算文件哈希
    file_hash = calculate_file_hash(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 提取PDF信息
    pdf_info = pdf_utils.extract_pdf_info(file_path)
    
    # 如果未提供标题，使用提取的标题
    if not title and pdf_info.get("title"):
        title = pdf_info.get("title")
    
    # 如果未提供作者，使用提取的作者
    if not authors and pdf_info.get("authors"):
        authors = pdf_info.get("authors")
    
    # 创建论文记录
    db_paper = models.Paper(
        title=title,
        authors=authors,
        upload_date=datetime.utcnow(),
        file_path=file_path,
        file_size=file_size,
        file_hash=file_hash,
        user_id=user_id,
        metadata=pdf_info,
        status="uploaded",
        tags=tags,
        doi=pdf_info.get("doi"),
        publication_info=pdf_info.get("publication_info"),
        is_public=False
    )
    
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    
    # 异步提取文本内容
    # TODO: 使用Celery任务异步处理
    
    return db_paper

def get_papers(
    db: Session, 
    user_id: uuid.UUID, 
    page: int = 1, 
    limit: int = 20, 
    status: Optional[str] = None, 
    tags: Optional[List[str]] = None, 
    search: Optional[str] = None
) -> Tuple[List[models.Paper], int]:
    """获取论文列表"""
    query = db.query(models.Paper).filter(models.Paper.user_id == user_id)
    
    # 应用过滤条件
    if status:
        query = query.filter(models.Paper.status == status)
    
    if tags:
        for tag in tags:
            query = query.filter(models.Paper.tags.contains([tag]))
    
    if search:
        query = query.filter(or_(
            models.Paper.title.ilike(f"%{search}%"),
            func.array_to_string(models.Paper.tags, ',').ilike(f"%{search}%")
        ))
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    query = query.order_by(models.Paper.upload_date.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    return query.all(), total

def get_paper(db: Session, paper_id: uuid.UUID, user_id: uuid.UUID):
    """获取论文详情"""
    return db.query(models.Paper).filter(
        models.Paper.id == paper_id,
        models.Paper.user_id == user_id
    ).first()

def update_paper(db: Session, paper_id: uuid.UUID, user_id: uuid.UUID, paper_update: schemas.PaperUpdate):
    """更新论文信息"""
    db_paper = get_paper(db, paper_id, user_id)
    
    if not db_paper:
        return None
    
    # 更新论文信息
    update_data = paper_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_paper, key, value)
    
    db.commit()
    db.refresh(db_paper)
    
    return db_paper

def delete_paper(db: Session, paper_id: uuid.UUID, user_id: uuid.UUID):
    """删除论文"""
    db_paper = get_paper(db, paper_id, user_id)
    
    if not db_paper:
        return False
    
    # 删除文件
    try:
        if os.path.exists(db_paper.file_path):
            os.remove(db_paper.file_path)
    except Exception as e:
        print(f"删除文件失败: {e}")
    
    # 删除数据库记录
    db.delete(db_paper)
    db.commit()
    
    return True

def calculate_file_hash(file_path: str) -> str:
    """计算文件哈希"""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()