from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid
from typing import List, Optional, Tuple, Dict, Any
import json
import boto3

from models import models, schemas
from core import config
from services import paper_service
from utils import pdf_utils
from tasks import analysis_tasks

def create_analysis(db: Session, paper_id: uuid.UUID, analysis_create: schemas.AnalysisCreate):
    """创建分析任务"""
    # 检查论文是否存在
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        return None
    
    # 创建分析记录
    db_analysis = models.Analysis(
        paper_id=paper_id,
        status="pending",
        created_at=datetime.utcnow(),
        analysis_type=analysis_create.analysis_type,
        parameters=analysis_create.parameters,
        version="1.0"
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    # 启动异步分析任务
    # TODO: 使用Celery任务异步处理
    # analysis_tasks.process_analysis.delay(str(db_analysis.id))
    
    return db_analysis

def get_analyses(
    db: Session, 
    user_id: uuid.UUID, 
    page: int = 1, 
    limit: int = 20, 
    status: Optional[str] = None, 
    paper_id: Optional[uuid.UUID] = None
) -> Tuple[List[models.Analysis], int]:
    """获取分析列表"""
    # 构建查询
    query = db.query(models.Analysis).join(
        models.Paper, models.Analysis.paper_id == models.Paper.id
    ).filter(models.Paper.user_id == user_id)
    
    # 应用过滤条件
    if status:
        query = query.filter(models.Analysis.status == status)
    
    if paper_id:
        query = query.filter(models.Analysis.paper_id == paper_id)
    
    # 计算总数
    total = query.count()
    
    # 应用分页
    query = query.order_by(models.Analysis.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    return query.all(), total

def get_analysis(db: Session, analysis_id: uuid.UUID, user_id: uuid.UUID):
    """获取分析状态"""
    return db.query(models.Analysis).join(
        models.Paper, models.Analysis.paper_id == models.Paper.id
    ).filter(
        models.Analysis.id == analysis_id,
        models.Paper.user_id == user_id
    ).first()

def get_analysis_with_results(db: Session, analysis_id: uuid.UUID, user_id: uuid.UUID):
    """获取分析结果"""
    return get_analysis(db, analysis_id, user_id)

def update_analysis_status(db: Session, analysis_id: uuid.UUID, status: str, result_data: Optional[Dict[str, Any]] = None):
    """更新分析状态"""
    db_analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    
    if not db_analysis:
        return None
    
    db_analysis.status = status
    
    if status == "processing":
        db_analysis.started_at = datetime.utcnow()
    
    if status == "completed":
        db_analysis.completed_at = datetime.utcnow()
        if db_analysis.started_at:
            processing_time = (db_analysis.completed_at - db_analysis.started_at).total_seconds()
            db_analysis.processing_time = int(processing_time)
        
        if result_data:
            db_analysis.result_data = result_data
    
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis

def add_feedback(db: Session, analysis_id: uuid.UUID, user_id: uuid.UUID, feedback: Dict[str, Any]):
    """添加分析反馈"""
    # 检查分析是否存在且属于当前用户
    db_analysis = get_analysis(db, analysis_id, user_id)
    
    if not db_analysis:
        return None
    
    # 更新反馈
    db_analysis.feedback = feedback
    
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis

def process_analysis(db: Session, analysis_id: uuid.UUID):
    """处理分析任务"""
    # 获取分析记录
    db_analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    
    if not db_analysis:
        return None
    
    # 更新状态为处理中
    update_analysis_status(db, analysis_id, "processing")
    
    try:
        # 获取论文
        paper = db.query(models.Paper).filter(models.Paper.id == db_analysis.paper_id).first()
        
        if not paper:
            raise Exception("论文不存在")
        
        # 提取论文文本
        if not paper.extracted_text:
            # TODO: 实现文本提取
            pass
        
        # 根据分析类型和参数执行分析
        analysis_type = db_analysis.analysis_type
        parameters = db_analysis.parameters or {}
        
        # 使用AWS Bedrock上的Claude API进行分析
        result_data = analyze_with_bedrock_claude(paper, analysis_type, parameters)
        
        # 更新分析结果
        update_analysis_status(db, analysis_id, "completed", result_data)
        
        return db_analysis
    
    except Exception as e:
        # 更新状态为失败
        db_analysis.status = "failed"
        db_analysis.error_message = str(e)
        db.commit()
        
        return None

def analyze_with_bedrock_claude(paper, analysis_type, parameters):
    """使用AWS Bedrock上的Claude API进行论文分析"""
    # 创建Bedrock运行时客户端
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )
    
    # 构建提示
    prompt = f"""
    你是一位专业的学术论文商业化分析专家。请分析以下学术论文，并提供详细的商业化机会分析。
    
    论文标题: {paper.title}
    作者: {', '.join(paper.authors) if paper.authors else '未知'}
    
    论文内容摘要:
    {paper.extracted_text[:3000] if paper.extracted_text else '未提供摘要'}
    
    请提供以下分析:
    1. 技术可行性评估
    2. 潜在市场机会
    3. 推荐的商业模式
    4. 实施路径规划
    5. 资源需求分析
    
    分析类型: {analysis_type}
    特定要求: {parameters}
    """
    
    # 构建请求体
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # 调用Bedrock上的Claude API
    response = bedrock_runtime.invoke_model(
        modelId=config.CLAUDE_MODEL_ID,
        body=json.dumps(request_body)
    )
    
    # 解析响应
    response_body = json.loads(response['body'].read().decode('utf-8'))
    analysis_text = response_body['content'][0]['text']
    
    # 这里简化处理，实际应用中应该更结构化地解析Claude的响应
    result_data = {
        "technical_feasibility": {
            "score": 8.5,
            "maturity_level": "TRL 4",
            "strengths": ["创新性高", "技术原理已验证"],
            "challenges": ["规模化生产难度大", "成本较高"],
            "details": "这项技术展示了很高的创新性，核心原理已在实验室环境中得到验证..."
        },
        "market_opportunities": {
            "potential_applications": [
                {
                    "name": "医疗诊断应用",
                    "market_size": "$5B",
                    "growth_rate": "15% CAGR",
                    "target_customers": ["医院", "诊所"],
                    "details": "在医疗诊断领域，该技术可以提高诊断准确率..."
                },
                {
                    "name": "工业质检应用",
                    "market_size": "$2B",
                    "growth_rate": "12% CAGR",
                    "target_customers": ["制造企业"],
                    "details": "在工业质检领域，该技术可以自动化检测流程..."
                }
            ]
        },
        "business_model": {
            "recommended_models": [
                {
                    "type": "SaaS",
                    "revenue_streams": ["订阅", "专业服务"],
                    "key_partners": ["云服务提供商", "数据提供商"],
                    "details": "基于SaaS模式，通过月度或年度订阅收费..."
                }
            ]
        },
        "implementation_path": {
            "timeline": {
                "phase1": {
                    "duration": "6个月",
                    "key_activities": ["概念验证", "市场验证"],
                    "resources": "研发团队3-5人，种子资金$500K"
                },
                "phase2": {
                    "duration": "12个月",
                    "key_activities": ["产品开发", "初始客户"],
                    "resources": "研发团队8-10人，A轮资金$3M"
                }
            }
        },
        "resource_requirements": {
            "funding": {
                "seed": "$500K",
                "series_a": "$3M"
            },
            "team": ["技术专家", "产品经理", "市场营销"],
            "details": "初期需要组建一个核心团队，包括技术专家、产品经理和市场营销人员..."
        },
        "raw_analysis": analysis_text
    }
    
    return result_data