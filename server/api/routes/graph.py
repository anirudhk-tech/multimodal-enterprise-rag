import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(tags=["graph"])

GRAPH_DIR = Path("graph")
GRAPH_JSON = GRAPH_DIR / "graph.json"


@router.get("/graph")
async def get_graph():
    if not GRAPH_JSON.exists():
        raise HTTPException(status_code=404, detail="Graph not built yet")

    try:
        graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.exception("Failed to read graph.json")
        raise HTTPException(status_code=500, detail=str(e))
    return graph
