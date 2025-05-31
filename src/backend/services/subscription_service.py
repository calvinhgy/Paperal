from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from models import models, schemas

def get_subscription(db: Session, subscription_id: uuid.UUID):
    """获取订阅"""
    return db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()

def get_active_subscription(db: Session, user_id: uuid.UUID):
    """获取用户的活跃订阅"""
    now = datetime.utcnow()
    return db.query(models.Subscription).filter(
        models.Subscription.user_id == user_id,
        models.Subscription.status == "active",
        (models.Subscription.end_date.is_(None) | (models.Subscription.end_date > now))
    ).first()

def get_user_subscriptions(db: Session, user_id: uuid.UUID):
    """获取用户的所有订阅"""
    return db.query(models.Subscription).filter(
        models.Subscription.user_id == user_id
    ).order_by(models.Subscription.start_date.desc()).all()

def create_subscription(db: Session, subscription_create: schemas.SubscriptionCreate):
    """创建订阅"""
    db_subscription = models.Subscription(
        user_id=subscription_create.user_id,
        plan_type=subscription_create.plan_type,
        start_date=subscription_create.start_date,
        end_date=subscription_create.end_date,
        status=subscription_create.status,
        payment_info=subscription_create.payment_info,
        created_at=datetime.utcnow()
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

def update_subscription(db: Session, subscription_id: uuid.UUID, subscription_update: schemas.SubscriptionUpdate):
    """更新订阅"""
    db_subscription = get_subscription(db, subscription_id)
    
    if not db_subscription:
        return None
    
    # 更新订阅信息
    update_data = subscription_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subscription, key, value)
    
    db_subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

def cancel_subscription(db: Session, subscription_id: uuid.UUID):
    """取消订阅"""
    db_subscription = get_subscription(db, subscription_id)
    
    if not db_subscription:
        return None
    
    db_subscription.status = "cancelled"
    db_subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription