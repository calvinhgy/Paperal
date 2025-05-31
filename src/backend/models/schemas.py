from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import uuid
from enum import Enum

# 基础模型
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True

# 用户相关模型
class UserBase(BaseSchema):
    email: EmailStr
    name: str
    organization: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    name: Optional[str] = None
    organization: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class UserInDB(UserBase):
    id: uuid.UUID
    role: str
    created_at: datetime
    is_active: bool

class User(UserInDB):
    pass

# 认证相关模型
class Token(BaseSchema):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseSchema):
    user_id: Optional[str] = None

# 订阅相关模型
class SubscriptionBase(BaseSchema):
    plan_type: str
    status: str

class SubscriptionCreate(SubscriptionBase):
    user_id: uuid.UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    payment_info: Optional[Dict[str, Any]] = None

class SubscriptionUpdate(BaseSchema):
    status: Optional[str] = None
    end_date: Optional[datetime] = None
    payment_info: Optional[Dict[str, Any]] = None

class Subscription(SubscriptionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime

# 论文相关模型
class PaperBase(BaseSchema):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class PaperCreate(PaperBase):
    file_path: str
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    user_id: uuid.UUID
    metadata: Optional[Dict[str, Any]] = None

class PaperUpdate(BaseSchema):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

class Paper(PaperBase):
    id: uuid.UUID
    user_id: uuid.UUID
    upload_date: datetime
    file_path: str
    status: str
    is_public: bool

class PaperDetail(Paper):
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    doi: Optional[str] = None
    publication_info: Optional[Dict[str, Any]] = None

# 分析相关模型
class AnalysisType(str, Enum):
    standard = "standard"
    technical = "technical"
    market = "market"
    business = "business"
    custom = "custom"

class AnalysisBase(BaseSchema):
    analysis_type: AnalysisType = AnalysisType.standard
    parameters: Optional[Dict[str, Any]] = None

class AnalysisCreate(AnalysisBase):
    paper_id: uuid.UUID

class AnalysisUpdate(BaseSchema):
    status: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None

class Analysis(AnalysisBase):
    id: uuid.UUID
    paper_id: uuid.UUID
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AnalysisDetail(Analysis):
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[int] = None
    version: Optional[str] = None

# 报告相关模型
class ReportFormat(str, Enum):
    pdf = "pdf"
    docx = "docx"
    html = "html"

class ReportBase(BaseSchema):
    title: str
    format: ReportFormat = ReportFormat.pdf
    template: Optional[str] = "standard"
    sections: Optional[List[str]] = None

class ReportCreate(ReportBase):
    analysis_id: uuid.UUID

class ReportUpdate(BaseSchema):
    title: Optional[str] = None
    is_public: Optional[bool] = None
    custom_sections: Optional[Dict[str, Any]] = None

class Report(ReportBase):
    id: uuid.UUID
    analysis_id: uuid.UUID
    created_at: datetime
    status: str

class ReportDetail(Report):
    updated_at: datetime
    file_path: Optional[str] = None
    is_public: bool
    access_count: int
    custom_sections: Optional[Dict[str, Any]] = None

# 评论相关模型
class CommentBase(BaseSchema):
    content: str

class CommentCreate(CommentBase):
    report_id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None

class CommentUpdate(BaseSchema):
    content: Optional[str] = None
    is_resolved: Optional[bool] = None

class Comment(CommentBase):
    id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    parent_id: Optional[uuid.UUID] = None
    is_resolved: bool

# API密钥相关模型
class APIKeyBase(BaseSchema):
    key_name: str
    permissions: Optional[Dict[str, Any]] = None

class APIKeyCreate(APIKeyBase):
    user_id: uuid.UUID
    expires_at: Optional[datetime] = None

class APIKey(APIKeyBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

class APIKeyWithValue(APIKey):
    key_value: str

# 响应模型
class ResponseBase(BaseSchema):
    success: bool

class ErrorDetail(BaseSchema):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(ResponseBase):
    success: bool = False
    error: ErrorDetail

class PaginationMeta(BaseSchema):
    total: int
    count: int
    per_page: int
    current_page: int
    total_pages: int
    links: Optional[Dict[str, Optional[str]]] = None

class ResponseMeta(BaseSchema):
    pagination: Optional[PaginationMeta] = None

class DataResponse(ResponseBase):
    success: bool = True
    data: Any
    meta: Optional[ResponseMeta] = None

# 共享相关模型
class ShareType(str, Enum):
    link = "link"
    email = "email"

class ShareCreate(BaseSchema):
    access_type: ShareType = ShareType.link
    expires_at: Optional[datetime] = None
    recipients: Optional[List[EmailStr]] = None

class Share(BaseSchema):
    id: uuid.UUID
    share_url: str
    access_type: ShareType
    expires_at: Optional[datetime] = None