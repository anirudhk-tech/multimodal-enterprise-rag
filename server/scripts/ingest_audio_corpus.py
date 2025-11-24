import logging
from pathlib import Path
from typing import Dict

from data.pokemon_mappings import POKEMON_MAPPING
from ingestion.audio_ingestion import ingest_audio, write_audio_record

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_AUDIO_DIR = Path("data/raw/audio")


def resolve_metadata(path: Path) -> tuple[str, int, list[str]]:
    for key, (pokemon, gen, types) in POKEMON_MAPPING.items():
        if key.lower() in path.stem.lower():
            return pokemon, gen, types
    raise ValueError(f"Could not resolve metadata for {path}")


def add_audio(path: Path) -> Dict[str, str]:
    RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_AUDIO_DIR / path.name
    if path.resolve() != target.resolve():
        target.write_bytes(path.read_bytes())

    pokemon, generation, types = resolve_metadata(target)

    record = ingest_audio(
        str(target),
        pokemon=pokemon,
        generation=generation,
        types=types,
    )
    write_audio_record(record)
    logger.info("Added audio %s for %s (gen %d)", target, pokemon, generation)
    return record


def main() -> None:
    if not RAW_AUDIO_DIR.exists():
        logging.warning("Audio directory %s does not exist", RAW_AUDIO_DIR)
        return

    for path in RAW_AUDIO_DIR.iterdir():
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".mp3"}:
            continue

        pokemon, generation, types = resolve_metadata(path)

        record = ingest_audio(
            str(path), pokemon=pokemon, generation=generation, types=types
        )
        write_audio_record(record)


if __name__ == "__main__":
    main()
