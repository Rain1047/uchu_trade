from pathlib import Path
from uuid import uuid4
from datetime import datetime

from backend._utils import LogConfig, DatabaseUtils
from backend.strategy_center.strategy_materials.tools.pdf_processor import PDFProcessor
from backend.strategy_center.strategy_materials.tools.ai_rule_enhancer import AIRuleEnhancer
from backend.strategy_center.strategy_materials.tools.strategy_generator import StrategyGenerator
from backend.data_object_center.agent.upload_file import UploadFile
from backend.data_object_center.agent.strategy_job import StrategyJob
from backend.data_object_center.agent.system_prompt import SystemPrompt

logger = LogConfig.get_logger(__name__)

db_session = DatabaseUtils.get_db_session()


class AgentService:
    """封装文件上传、任务调度、进度更新逻辑"""

    def __init__(self):
        base_dir = Path(__file__).resolve().parents[3] / "strategy_center/strategy_materials"
        self.raw_books_dir = base_dir / "raw_books"
        self.extracted_text_dir = base_dir / "extracted_text"
        self.processed_rules_dir = base_dir / "processed_rules"
        self.final_strategies_dir = base_dir / "final_strategies"

        # 确保目录存在
        for p in [self.raw_books_dir, self.extracted_text_dir, self.processed_rules_dir, self.final_strategies_dir]:
            p.mkdir(parents=True, exist_ok=True)

        # 初始化工具
        self.pdf_processor = PDFProcessor(str(self.raw_books_dir), str(self.extracted_text_dir))
        self.ai_enhancer = AIRuleEnhancer(str(self.extracted_text_dir), str(self.processed_rules_dir))
        self.strategy_generator = StrategyGenerator(str(self.processed_rules_dir), str(self.final_strategies_dir))

    # ---------------------------- 文件相关 ----------------------------
    @staticmethod
    def save_upload(file_name: str, file_bytes: bytes) -> UploadFile:
        """保存文件到 raw_books 并持久化元数据"""
        stored_path = Path(__file__).resolve().parents[3] / "strategy_center/strategy_materials/raw_books" / file_name
        stored_path.write_bytes(file_bytes)
        upload = UploadFile(
            filename=file_name,
            stored_path=str(stored_path),
            file_type=stored_path.suffix.lstrip('.'),
            size=len(file_bytes),
            status="saved",
            created_at=datetime.utcnow()
        )
        db_session.add(upload)
        db_session.commit()
        return upload

    # ---------------------------- Job 执行 ----------------------------
    def create_job(self, file_id: int, prompt_id: int) -> StrategyJob:
        job = StrategyJob(
            id=uuid4().hex[:12],
            file_id=file_id,
            prompt_id=prompt_id,
            progress=0,
            status="pending",
            created_at=datetime.utcnow()
        )
        db_session.add(job)
        db_session.commit()
        return job

    def update_progress(self, job: StrategyJob, progress: int, message: str | None = None):
        job.progress = progress
        if message:
            job.message = message
        db_session.commit()
        # TODO: 推送 WS / Redis 发布

    def process_job(self, job_id: str):
        """同步处理任务（可由 BackgroundTasks 或 Celery 异步调用）"""
        job: StrategyJob = db_session.query(StrategyJob).get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        job.status = "running"
        db_session.commit()

        try:
            upload: UploadFile = db_session.query(UploadFile).get(job.file_id)
            prompt: SystemPrompt = db_session.query(SystemPrompt).get(job.prompt_id)

            # 1. PDF -> Text
            self.update_progress(job, 10, "提取文本")
            self.pdf_processor.process_pdf(Path(upload.stored_path).name)

            # 2. AI 提取规则（使用 prompt.content 作为 System Prompt）
            self.update_progress(job, 40, "AI分析&规则提取")
            text_filename = Path(upload.stored_path).stem + ".txt"
            self.ai_enhancer.process_text_file(text_filename)

            # 3. 生成策略代码
            self.update_progress(job, 80, "生成策略代码")
            self.strategy_generator.process_all_rules()

            # 假设生成的 .py 命名带 job.stem
            strategy_py = next(self.final_strategies_dir.glob("strategy_*" + Path(upload.stored_path).stem + "*.py"), None)
            if strategy_py:
                job.output_py = str(strategy_py)

            self.update_progress(job, 100, "完成")
            job.status = "success"
            job.finished_at = datetime.utcnow()
            db_session.commit()
        except Exception as e:
            logger.error(f"Job {job_id} error: {e}")
            job.status = "error"
            job.message = str(e)
            db_session.commit() 