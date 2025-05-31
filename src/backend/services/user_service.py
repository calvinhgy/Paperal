from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import secrets
import string

from models import models, schemas
from core import security

def get_user(db: Session, user_id: uuid.UUID):
    """获取用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_create: schemas.UserCreate):
    """创建用户"""
    # 创建密码哈希
    hashed_password = security.get_password_hash(user_create.password)
    
    # 创建用户
    db_user = models.User(
        email=user_create.email,
        password_hash=hashed_password,
        name=user_create.name,
        organization=user_create.organization,
        role="user",
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: uuid.UUID, user_update: schemas.UserUpdate):
    """更新用户信息"""
    db_user = get_user(db, user_id)
    
    if not db_user:
        return None
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_password(db: Session, user_id: uuid.UUID, new_password: str):
    """更新用户密码"""
    db_user = get_user(db, user_id)
    
    if not db_user:
        return None
    
    # 更新密码哈希
    db_user.password_hash = security.get_password_hash(new_password)
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return True

def update_last_login(db: Session, user_id: uuid.UUID):
    """更新最后登录时间"""
    db_user = get_user(db, user_id)
    
    if not db_user:
        return None
    
    db_user.last_login_at = datetime.utcnow()
    
    db.commit()
    
    return True

def authenticate_user(db: Session, email: str, password: str):
    """验证用户"""
    user = get_user_by_email(db, email)
    
    if not user:
        return False
    
    if not security.verify_password(password, user.password_hash):
        return False
    
    return user

def get_user_api_keys(db: Session, user_id: uuid.UUID):
    """获取用户API密钥"""
    return db.query(models.APIKey).filter(models.APIKey.user_id == user_id).all()

def create_api_key(db: Session, user_id: uuid.UUID, api_key_create: schemas.APIKeyBase):
    """创建API密钥"""
    # 生成随机API密钥
    alphabet = string.ascii_letters + string.digits
    key_value = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # 创建密钥哈希
    key_hash = security.get_password_hash(key_value)
    
    # 创建API密钥
    db_api_key = models.APIKey(
        user_id=user_id,
        key_name=api_key_create.key_name,
        key_hash=key_hash,
        permissions=api_key_create.permissions,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    # 返回带有密钥值的响应
    api_key_response = schemas.APIKeyWithValue(
        id=db_api_key.id,
        user_id=db_api_key.user_id,
        key_name=db_api_key.key_name,
        permissions=db_api_key.permissions,
        created_at=db_api_key.created_at,
        expires_at=db_api_key.expires_at,
        is_active=db_api_key.is_active,
        key_value=key_value
    )
    
    return api_key_response

def delete_api_key(db: Session, user_id: uuid.UUID, api_key_id: str):
    """删除API密钥"""
    try:
        api_key_uuid = uuid.UUID(api_key_id)
    except ValueError:
        return False
    
    db_api_key = db.query(models.APIKey).filter(
        models.APIKey.id == api_key_uuid,
        models.APIKey.user_id == user_id
    ).first()
    
    if not db_api_key:
        return False
    
    db.delete(db_api_key)
    db.commit()
    
    return True