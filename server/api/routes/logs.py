import json
import logging
from pathlib import Path

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["logs"])

LOG_PATH = Path("logs/eval.jsonl")


@router.get("/logs")
async def get_logs():
    if not LOG_PATH.exists():
        return []

    records = []
    try:
        with LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    except Exception as e:
        logger.exception("Failed to read eval logs")
        return []

    return records
