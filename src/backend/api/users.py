from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import models, schemas
from core import security
from services import user_service, subscription_service

router = APIRouter()

@router.get("/me", response_model=schemas.DataResponse)
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    """
    # 获取用户订阅信息
    subscription = subscription_service.get_active_subscription(db, current_user.id)
    
    # 构建用户信息响应
    user_data = schemas.User.from_orm(current_user).dict()
    user_data["subscription"] = subscription.dict() if subscription else None
    
    return {
        "success": True,
        "data": user_data
    }

@router.patch("/me", response_model=schemas.DataResponse)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    """
    updated_user = user_service.update_user(db, current_user.id, user_update)
    
    return {
        "success": True,
        "data": updated_user
    }

@router.get("/me/subscriptions", response_model=schemas.DataResponse)
async def read_user_subscriptions(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的订阅历史
    """
    subscriptions = subscription_service.get_user_subscriptions(db, current_user.id)
    
    return {
        "success": True,
        "data": subscriptions
    }

@router.post("/me/change-password", response_model=schemas.DataResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    """
    # 验证旧密码
    if not security.verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 更新密码
    user_service.update_password(db, current_user.id, new_password)
    
    return {
        "success": True,
        "data": {"message": "密码已成功更新"}
    }

@router.get("/me/api-keys", response_model=schemas.DataResponse)
async def read_user_api_keys(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的API密钥
    """
    api_keys = user_service.get_user_api_keys(db, current_user.id)
    
    return {
        "success": True,
        "data": api_keys
    }

@router.post("/me/api-keys", response_model=schemas.DataResponse)
async def create_api_key(
    api_key_create: schemas.APIKeyBase,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的API密钥
    """
    api_key = user_service.create_api_key(db, current_user.id, api_key_create)
    
    return {
        "success": True,
        "data": api_key
    }

@router.delete("/me/api-keys/{api_key_id}", response_model=schemas.DataResponse)
async def delete_api_key(
    api_key_id: str,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除API密钥
    """
    result = user_service.delete_api_key(db, current_user.id, api_key_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API密钥不存在或不属于当前用户"
        )
    
    return {
        "success": True,
        "data": {"message": "API密钥已成功删除"}
    }