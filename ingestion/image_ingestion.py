import json
import logging
from pathlib import Path

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
IMAGES_JSONL = PROCESSED_DIR / "images.jsonl"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_image(image_path_string: str) -> str:
    image_path = Path(image_path_string)
    logger.info(
        "extract_text_from_image started", extra={"image_path": str(image_path)}
    )

    try:
        image = Image.open(image_path)
    except Exception as e:
        logger.exception(
            "Error opening image",
            extra={"path": str(image_path)},
        )
        raise e

    try:
        raw_text = pytesseract.image_to_string(image)
    except Exception as e:
        logger.exception(
            "Error running OCR",
            extra={"path": str(image_path)},
        )
        raise e

    text = raw_text.strip()

    logger.info(
        "extract_text_from_image finished",
        extra={
            "path": str(image_path),
            "chars": len(text),
        },
    )
    return text


def ingest_image(
    image_path_string: str, pokemon: str, generation: int, types: list[str]
):
    image_path = Path(image_path_string)

    logger.info(
        "ingest_image started",
        extra={
            "image_path": str(image_path),
            "pokemon": pokemon,
            "generation": generation,
        },
    )

    text = extract_text_from_image(image_path_string)

    record = {
        "id": image_path.stem,
        "modality": "image",
        "source_path": str(image_path),
        "text": text,
        "pokemon": pokemon,
        "generation": generation,
        "types": types,
        "tags": [
            "starter",
            "image",
            pokemon.lower(),
        ],
    }  # dataset is all starter pokemon, default tag "starter"

    logger.debug(
        "ingest_image record created",
        extra={
            "id": record["id"],
            "chars": len(record["text"]),
            "pokemon": pokemon,
            "generation": generation,
        },
    )
    return record


def write_image_record(record: dict) -> None:
    IMAGES_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with IMAGES_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False))
        f.write("\n")

    logger.info(
        "write_image_record finished",
        extra={"id": record["id"], "path": str(IMAGES_JSONL)},
    )
