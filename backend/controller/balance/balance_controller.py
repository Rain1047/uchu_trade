from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging


# 创建路由器实例
router = APIRouter()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


