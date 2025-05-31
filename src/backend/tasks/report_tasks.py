import uuid
from sqlalchemy.orm import Session

from tasks.celery_app import celery_app
from database import SessionLocal
from services import report_service

@celery_app.task(name="generate_report")
def generate_report(report_id: str):
    """
    生成报告任务
    """
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 生成报告
        report_service.generate_report(db, uuid.UUID(report_id))
        
        # 关闭会话
        db.close()
        
        return {"status": "success", "report_id": report_id}
    
    except Exception as e:
        # 记录错误
        print(f"生成报告任务失败: {e}")
        
        # 尝试更新报告状态为失败
        try:
            db = SessionLocal()
            report = db.query(models.Report).filter(models.Report.id == uuid.UUID(report_id)).first()
            if report:
                report.status = "failed"
                db.commit()
            db.close()
        except Exception:
            pass
        
        # 重新抛出异常，让Celery处理
        raise