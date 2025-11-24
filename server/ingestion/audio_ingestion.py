import json
import logging
from pathlib import Path
from typing import Dict

import whisper

logger = logging.getLogger(__name__)

AUDIO_JSONL = Path("data/processed/audio.jsonl")
_model = None


def _get_whisper_model():
    global _model

    if _model is None:
        logger.info(
            "_get_whisper_model loading model",
            extra={"model_name": "small"},
        )
        _model = whisper.load_model("small")
        logger.info(
            "_get_whisper_model finished loading",
            extra={"model_name": "small"},
        )

    return _model


def extract_text_from_audio(
    path: str, model=None
) -> str:  # test purposes: fake model can be passed to avoid loading whisper on tests
    logger.info(
        "extract_text_from_audio started",
        extra={"path": str(path)},
    )

    if model is None:
        model = _get_whisper_model()

    try:
        result = model.transcribe(path, fp16=False)
    except Exception:
        logger.exception(
            "Error during audio transcription",
            extra={"path": str(path)},
        )
        raise

    text = result["text"].strip() or ""

    if not text:
        logger.debug(
            "Empty or whitespace-only transcription",
            extra={"path": str(path)},
        )

    logger.info(
        "extract_text_from_audio finished",
        extra={
            "path": str(path),
            "chars": len(text),
        },
    )

    return text


def ingest_audio(
    audio_path_string: str, pokemon: str, generation: int, types: list[str], model=None
) -> Dict[str, str]:
    audio_path = Path(audio_path_string)

    logger.info(
        "ingest_audio started",
        extra={"path": str(audio_path)},
    )

    text = extract_text_from_audio(str(audio_path), model)

    record: Dict = {
        "id": audio_path.stem,
        "modality": "audio",
        "source_path": str(audio_path),
        "text": text,
        "pokemon": pokemon,
        "generation": generation,
        "types": types,
        "tags": ["starter", "audio", pokemon.lower()],
    }  # dataset is all starter pokemon, default tag "starter"

    logger.debug(
        "ingest_audio finished",
        extra={
            "path": str(audio_path),
            "chars": len(text),
        },
    )

    return record


def write_audio_record(record: Dict) -> None:
    AUDIO_JSONL.parent.mkdir(parents=True, exist_ok=True)

    with AUDIO_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False))
        f.write("\n")

    logger.info(
        "write_audio_record finished",
        extra={
            "id": record["id"],
            "path": str(AUDIO_JSONL),
        },
    )
