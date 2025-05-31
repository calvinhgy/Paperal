from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    profile_data = Column(JSON)
    settings = Column(JSON)
    api_key = Column(String(255))
    is_active = Column(Boolean, default=True)

    # 关系
    papers = relationship("Paper", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Subscription(Base):
    """订阅模型"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(50), nullable=False)
    payment_info = Column(JSON)
    features = Column(JSON)
    usage_limits = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="subscriptions")

class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500))
    authors = Column(JSON)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_hash = Column(String(255))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metadata = Column(JSON)
    status = Column(String(50), default="uploaded")
    tags = Column(ARRAY(String))
    doi = Column(String(255))
    publication_info = Column(JSON)
    extracted_text = Column(Text)
    embedding_id = Column(String(255))
    is_public = Column(Boolean, default=False)

    # 关系
    user = relationship("User", back_populates="papers")
    analyses = relationship("Analysis", back_populates="paper")

class Analysis(Base):
    """分析模型"""
    __tablename__ = "analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result_data = Column(JSON)
    error_message = Column(Text)
    analysis_type = Column(String(50), default="standard")
    parameters = Column(JSON)
    feedback = Column(JSON)
    processing_time = Column(Integer)
    version = Column(String(50))

    # 关系
    paper = relationship("Paper", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis")

class Report(Base):
    """报告模型"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    format = Column(String(50), default="pdf")
    file_path = Column(String(500))
    shared_with = Column(JSON)
    is_public = Column(Boolean, default=False)
    access_count = Column(Integer, default=0)
    template_id = Column(String(255))
    custom_sections = Column(JSON)

    # 关系
    analysis = relationship("Analysis", back_populates="reports")
    comments = relationship("Comment", back_populates="report")

class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    is_resolved = Column(Boolean, default=False)

    # 关系
    report = relationship("Report", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref=ForeignKey("parent_id"))

class APIKey(Base):
    """API密钥模型"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)

    # 关系
    user = relationship("User", back_populates="api_keys")

class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(255), nullable=False)
    entity_type = Column(String(255), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    details = Column(JSON)