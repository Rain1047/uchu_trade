from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
from typing import List

router = APIRouter()


class StrategyFile(BaseModel):
    name: str
    path: str
    modified: datetime
    size: int


@router.get("/files", response_model=List[StrategyFile])
async def get_strategy_files():
    try:
        # 获取项目根目录
        current_dir = os.getcwd()
        strategy_path = os.path.join(current_dir, "strategy_center", "atom_strategy")

        files = []

        # 遍历策略文件夹
        for folder in ['entry_strategy', 'exit_strategy', 'filter_strategy']:
            folder_path = os.path.join(strategy_path, folder)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        file_path = os.path.join(folder_path, filename)
                        stat = os.stat(file_path)
                        files.append(StrategyFile(
                            name=filename,
                            path=f"{folder}/{filename}",
                            modified=datetime.fromtimestamp(stat.st_mtime),
                            size=stat.st_size
                        ))

        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{folder}/{filename}")
async def get_strategy_file_content(folder: str, filename: str):
    try:
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "strategy_center", "atom_strategy", folder, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))