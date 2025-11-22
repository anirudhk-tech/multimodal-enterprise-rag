import json
import logging
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)
PROCESSED_DIR = Path("data/processed")
TEXT_JSONL = PROCESSED_DIR / "text.jsonl"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_pdf(pdf_path: str) -> str:
    logger.info("extract_text_from_pdf started", extra={"path": str(pdf_path)})

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        logger.exception("Error reading PDF", extra={"path": str(pdf_path)})
        raise e

    chunks: list[str] = []

    for page_idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            logger.exception(
                "Failed to extract text from page",
                extra={"path": str(pdf_path), "page": page_idx},
            )
            continue

        clean = page_text.strip()
        if not clean:
            logger.debug(
                "Empty or whitespace-only page text",
                extra={"path": str(pdf_path), "page": page_idx},
            )
            continue

        chunks.append(clean)

    text = "\n\n".join(chunks).strip()
    logger.info(
        "extract_text_from_pdf finished",
        extra={"path": str(pdf_path), "chars": len(text), "pages": len(reader.pages)},
    )
    return text


def ingest_pdf(
    pdf_path_string: str, pokemon: str, generation: int, types: list[str]
) -> dict:
    pdf_path = Path(pdf_path_string)
    logger.info(
        "ingest_pdf started",
        extra={
            "path": str(pdf_path),
            "pokemon": pokemon,
            "generation": generation,
        },
    )

    text = extract_text_from_pdf(str(pdf_path))

    record = {
        "id": pdf_path.stem,
        "modality": "text",
        "source_path": str(pdf_path),
        "text": text,
        "pokemon": pokemon,
        "generation": generation,
        "types": types,
        "tags": [
            "starter",
            pokemon.lower(),
        ],  # dataset is all starter pokemon, default tag "starter"
    }

    logger.debug(
        "ingest_pdf record created",
        extra={
            "id": record["id"],
            "chars": len(record["text"]),
            "pokemon": pokemon,
            "generation": generation,
        },
    )

    return record


def ingest_txt(
    txt_path_string: str, pokemon: str, generation: int, types: list[str]
) -> dict:
    txt_path = Path(txt_path_string)
    logger.info(
        "ingest_txt started",
        extra={
            "path": str(txt_path),
            "pokemon": pokemon,
            "generation": generation,
        },
    )

    text = txt_path.read_text(encoding="utf-8")

    record = {
        "id": txt_path.stem,
        "modality": "text",
        "source_path": str(txt_path),
        "text": text.strip(),
        "pokemon": pokemon,
        "generation": generation,
        "types": types,
        "tags": ["starter", pokemon.lower()],
    }

    logger.debug(
        "ingest_txt record created",
        extra={
            "id": record["id"],
            "chars": len(record["text"]),
            "pokemon": pokemon,
            "generation": generation,
        },
    )
    return record


def write_text_record(record: dict) -> None:
    TEXT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with TEXT_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False))
        f.write("\n")

    logger.info(
        "write_text_record finished",
        extra={"id": record["id"], "path": str(TEXT_JSONL)},
    )
