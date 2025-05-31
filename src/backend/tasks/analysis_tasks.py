import uuid
from sqlalchemy.orm import Session

from tasks.celery_app import celery_app
from database import SessionLocal
from services import analysis_service

@celery_app.task(name="process_analysis")
def process_analysis(analysis_id: str):
    """
    处理分析任务
    """
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 处理分析
        analysis_service.process_analysis(db, uuid.UUID(analysis_id))
        
        # 关闭会话
        db.close()
        
        return {"status": "success", "analysis_id": analysis_id}
    
    except Exception as e:
        # 记录错误
        print(f"处理分析任务失败: {e}")
        
        # 尝试更新分析状态为失败
        try:
            db = SessionLocal()
            analysis = db.query(models.Analysis).filter(models.Analysis.id == uuid.UUID(analysis_id)).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                db.commit()
            db.close()
        except Exception:
            pass
        
        # 重新抛出异常，让Celery处理
        raise