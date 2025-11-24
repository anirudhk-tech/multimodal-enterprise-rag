import logging
from pathlib import Path

from fastapi import (  # type: ignore (local editor interpreter issue)
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)
from scripts.ingest import main as run_full_ingest
from scripts.ingest_audio_corpus import add_audio as run_add_audio
from scripts.ingest_images_corpus import add_image as run_add_image
from scripts.ingest_text_corpus import add_text as run_add_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])

RAW_AUDIO_DIR = Path("data/raw/audio")
RAW_IMAGE_DIR = Path("data/raw/images")
RAW_TEXT_DIR = Path("data/raw/text")


@router.post("/add/audio")
async def add_audio(file: UploadFile = File(...)) -> dict:
    try:
        logger.info("API: starting ingestion of audio file")
        RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        target_path = RAW_AUDIO_DIR / file.filename

        contents = await file.read()
        target_path.write_bytes(contents)
        await file.close()

        record = run_add_audio(target_path)
        logger.info("API: audio file ingested")
        return {"message": "Audio ingested", "record": record}
    except Exception as e:
        logger.exception("Error adding audio")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add/image")
async def add_image(file: UploadFile = File(...)) -> dict:
    try:
        logger.info("API: starting ingestion of image file")
        RAW_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        target_path = RAW_IMAGE_DIR / file.filename

        contents = await file.read()
        target_path.write_bytes(contents)
        await file.close()

        record = run_add_image(target_path)
        logger.info("API: image file ingested")
        return {"message": "Image ingested", "record": record}
    except Exception as e:
        logger.exception("Error adding image")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add/text")
async def add_text(file: UploadFile = File(...)) -> dict:
    suffix = file.filename.lower().rsplit(".", 1)[-1]
    if suffix not in {"pdf", "txt"}:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt supported")

    try:
        logger.info("API: starting ingestion of text file")
        RAW_TEXT_DIR.mkdir(parents=True, exist_ok=True)
        target_path = RAW_TEXT_DIR / file.filename

        contents = await file.read()
        target_path.write_bytes(contents)
        await file.close()

        record = run_add_text(target_path)
        logger.info("API: text file ingested")
        return {"message": "Text ingested", "record": record}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error adding text")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
def ingest_corpus() -> dict:
    """
    Run the full ingestion pipeline:
    - ingest_text_corpus.main()
    - ingest_images_corpus.main()
    - ingest_audio_corpus.main()
    """
    try:
        logger.info("API: starting full ingestion via /ingest")
        run_full_ingest()
        logger.info("API: ingestion completed")
        return {"message": "Ingestion process completed."}
    except Exception as e:
        logger.exception("Error during ingestion")
        raise HTTPException(status_code=500, detail=str(e))
