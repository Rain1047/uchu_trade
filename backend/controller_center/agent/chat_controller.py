from fastapi import APIRouter, BackgroundTasks, HTTPException
from sse_starlette.sse import EventSourceResponse
import asyncio
from backend._utils import SSEManager, LogConfig
from backend.service_center.agent.chat_service import stream_llm
from pydantic import BaseModel
from pathlib import Path
import re, datetime
import uuid, time, threading

router = APIRouter(tags=["agent-chat"])
logger = LogConfig.get_logger(__name__)


def _format(data: str, event: str = "delta"):
    return {"event": event, "data": data}


@router.post("/chat/stream")
async def start_chat_stream(body: dict, background_tasks: BackgroundTasks):
    """创建 SSE 通道，立即返回 cid，然后后台模拟流式推送"""
    user_msg = body.get("message", "")
    messages = body.get("messages")  # 新增，支持多轮上下文
    cid, queue = SSEManager.create_channel()

    background_tasks.add_task(stream_llm, cid, user_msg, None, messages)
    return {"cid": cid}


@router.get("/chat/stream/{cid}")
async def chat_stream(cid: str):
    """SSE 订阅端口"""
    async def event_generator():
        async for msg in SSEManager.generator(cid):
            yield msg
    return EventSourceResponse(event_generator())


class AdoptSchema(BaseModel):
    cid: str
    content: str
    stype: str  # entry|exit|filter


def slugify(text: str):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return text[:40] or "strategy"


BASE_DIR = Path(__file__).resolve().parents[1] / "../strategy_center/atom_strategy"


@router.post("/adopt")
async def adopt(body: AdoptSchema):
    folder_map = {
        "entry": "entry_strategy",
        "exit": "exit_strategy",
        "filter": "filter_strategy",
    }
    sub = folder_map.get(body.stype, "entry_strategy")
    target_dir = BASE_DIR / sub
    target_dir.mkdir(parents=True, exist_ok=True)

    first_line = body.content.splitlines()[0] if body.content else "strategy"
    filename = slugify(first_line) + "_" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S") + ".py"
    path = target_dir / filename
    path.write_text(body.content, encoding="utf-8")
    return {"path": str(path)}


# -------------------- 评估任务 Mock --------------------
_eval_jobs = {}


def _run_mock_eval(job_id: str, path: str):
    _eval_jobs[job_id] = {"status": "running"}
    time.sleep(5)
    _eval_jobs[job_id] = {
        "status": "done",
        "score": round(50 + 50 * (hash(path) % 100) / 100, 2),
        "suggestions": "示例建议：尝试调整止盈止损参数。"
    }


@router.post("/evaluate")
async def start_evaluate(data: dict):
    path = data.get("path")
    if not path or not Path(path).exists():
        raise HTTPException(400, "path invalid")
    job_id = uuid.uuid4().hex[:12]
    _eval_jobs[job_id] = {"status": "pending"}
    threading.Thread(target=_run_mock_eval, args=(job_id, path), daemon=True).start()
    return {"job_id": job_id}


@router.get("/evaluate/{job_id}")
async def get_evaluate(job_id: str):
    info = _eval_jobs.get(job_id)
    if not info:
        raise HTTPException(404, "job not found")
    return info 