import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile as FastUploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import inspect, text

from backend._utils import LogConfig
from backend.service_center.agent.agent_service import AgentService
from backend.data_object_center.agent.system_prompt import SystemPrompt
from backend.data_object_center.agent.upload_file import UploadFile as UploadFileORM
from backend.data_object_center.agent.strategy_job import StrategyJob
from backend._utils import DatabaseUtils
from backend.data_object_center.base import Base, engine

logger = LogConfig.get_logger(__name__)

router = APIRouter(tags=["agent"])

agent_service = AgentService()

def ensure_table_exists(table_name: str):
    """确保表存在，如果不存在则创建"""
    session = DatabaseUtils.get_db_session()
    try:
        bind_engine = session.bind
        inspector = inspect(bind_engine)
        if not inspector.has_table(table_name):
            logger.info(f"创建 {table_name} 表")
            # 获取表的元数据
            table = Base.metadata.tables.get(table_name)
            if table is None:
                logger.error(f"表 {table_name} 的元数据不存在")
                return False
            # 创建表
            table.create(bind_engine)
            logger.info(f"表 {table_name} 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建表 {table_name} 时出错: {e}")
        return False
    finally:
        session.close()

# ----------------------------- Schemas -----------------------------
class SystemPromptSchema(BaseModel):
    id: int | None = None
    name: str
    content: str

    class Config:
        orm_mode = True
        from_attributes = True


class UploadFileSchema(BaseModel):
    id: int
    filename: str
    file_type: str
    size: int
    status: str
    # 前端可根据 id 构造下载/预览链接

    class Config:
        orm_mode = True


class StrategyJobSchema(BaseModel):
    id: str
    progress: int
    status: str
    message: str | None = None

    class Config:
        orm_mode = True

# ----------------------- SystemPrompt CRUD -------------------------
@router.get("/prompts", response_model=List[SystemPromptSchema])
async def list_prompts():
    if not ensure_table_exists("system_prompt"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        prompts = db_session.query(SystemPrompt).all()
        return [SystemPromptSchema.from_orm(p) for p in prompts]
    finally:
        db_session.close()


@router.post("/prompts", response_model=SystemPromptSchema)
async def create_prompt(prompt: SystemPromptSchema):
    if not ensure_table_exists("system_prompt"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        p = SystemPrompt(name=prompt.name, content=prompt.content)
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)
        return SystemPromptSchema.from_orm(p)
    finally:
        db_session.close()


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: int, prompt: SystemPromptSchema):
    if not ensure_table_exists("system_prompt"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        db_p = db_session.query(SystemPrompt).get(prompt_id)
        if not db_p:
            raise HTTPException(404, "Prompt not found")
        db_p.name = prompt.name
        db_p.content = prompt.content
        db_session.commit()
        return {"success": True}
    finally:
        db_session.close()


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int):
    if not ensure_table_exists("system_prompt"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        db_p = db_session.query(SystemPrompt).get(prompt_id)
        if not db_p:
            raise HTTPException(404, "Prompt not found")
        db_session.delete(db_p)
        db_session.commit()
        return {"success": True}
    finally:
        db_session.close()

# --------------------------- 文件上传 ------------------------------
@router.post("/files", response_model=UploadFileSchema)
async def upload_file(file: FastUploadFile = File(...)):
    if not ensure_table_exists("upload_file"):
        raise HTTPException(500, "数据库表创建失败")
    if file.content_type not in ["application/pdf", "application/epub+zip"]:
        raise HTTPException(status_code=400, detail="仅支持 PDF/EPUB")
    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小超过 20MB")
    upload = agent_service.save_upload(file.filename, data)
    return upload

# --------------------------- 文件列表/下载 -------------------------

@router.get("/files", response_model=List[UploadFileSchema])
async def list_files():
    if not ensure_table_exists("upload_file"):
        raise HTTPException(500, "数据库表创建失败")
    session = DatabaseUtils.get_db_session()
    try:
        # 1. 目录同步
        base_dir = Path(__file__).resolve().parents[2] / "strategy_center/strategy_materials/raw_books"
        base_dir.mkdir(parents=True, exist_ok=True)

        existing_paths = {u.stored_path for u in session.query(UploadFileORM.stored_path).all()}

        new_files = []
        for f in base_dir.iterdir():
            if not f.is_file():
                continue
            if f.suffix.lower() not in [".pdf", ".epub"]:
                continue
            if str(f) not in existing_paths:
                upload = UploadFileORM(
                    filename=f.name,
                    stored_path=str(f),
                    file_type=f.suffix.lstrip('.'),
                    size=f.stat().st_size,
                    status="saved"
                )
                session.add(upload)
                new_files.append(upload)

        if new_files:
            session.commit()

        return session.query(UploadFileORM).order_by(UploadFileORM.created_at.desc()).all()
    finally:
        session.close()


@router.get("/files/{file_id}/raw")
async def download_raw_file(file_id: int):
    if not ensure_table_exists("upload_file"):
        raise HTTPException(500, "数据库表创建失败")
    session = DatabaseUtils.get_db_session()
    try:
        upload = session.query(UploadFileORM).get(file_id)
        if not upload:
            raise HTTPException(404, "File not found")
        path = Path(upload.stored_path)
        if not path.exists():
            raise HTTPException(404, "文件不存在")
        return FileResponse(path, filename=upload.filename)
    finally:
        session.close()

# --------------------------- 任务处理 ------------------------------
@router.post("/jobs", response_model=StrategyJobSchema)
async def start_job(background_tasks: BackgroundTasks, file_id: int, prompt_id: int):
    if not ensure_table_exists("strategy_job"):
        raise HTTPException(500, "数据库表创建失败")
    job = agent_service.create_job(file_id, prompt_id)
    # 异步执行
    background_tasks.add_task(agent_service.process_job, job.id)
    return job


@router.get("/jobs/{job_id}", response_model=StrategyJobSchema)
async def job_status(job_id: str):
    if not ensure_table_exists("strategy_job"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        job = db_session.query(StrategyJob).get(job_id)
        if not job:
            raise HTTPException(404, "Job not found")
        return job
    finally:
        db_session.close()


@router.get("/jobs/{job_id}/code")
async def download_code(job_id: str):
    if not ensure_table_exists("strategy_job"):
        raise HTTPException(500, "数据库表创建失败")
    db_session = DatabaseUtils.get_db_session()
    try:
        job = db_session.query(StrategyJob).get(job_id)
        if not job or not job.output_py:
            raise HTTPException(404, "代码未生成")
        path = Path(job.output_py)
        if not path.exists():
            raise HTTPException(404, "文件不存在")
        return FileResponse(path)
    finally:
        db_session.close() 