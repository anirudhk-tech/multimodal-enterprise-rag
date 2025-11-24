import json
import logging
from pathlib import Path

from fastapi import APIRouter  # type: ignore (safe to ignore, local editor quirk)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["graph"])

GRAPH_DIR = Path("graph")


@router.get("/graph")
async def get_graph():
    target = GRAPH_DIR / "graph.json"
    graph = json.loads(target.read_text())
    return graph
