import logging

from fastapi import (
    APIRouter,
    HTTPException,
)
from scripts.process import main as run_build_graph

logger = logging.getLogger(__name__)

router = APIRouter(tags=["process"])


@router.post("/process")
def process_graph() -> dict:
    """
    Run the graph-building pipeline:
    - build_graph_and_export_to_csv_and_json()
    """
    try:
        logger.info("API: starting graph build via /process")
        run_build_graph()
        logger.info("API: graph built and exported")
        return {"message": "Graph built and exported to CSV and JSON successfully."}
    except Exception as e:
        logger.exception("Error during graph processing")
        raise HTTPException(status_code=500, detail=str(e))
