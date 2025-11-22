import logging
from pathlib import Path

from ingestion.audio_ingestion import ingest_audio, write_audio_record

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_AUDIO_DIR = Path("data/raw/audio")

POKEMON_MAPPING = {  # basic metadata (name, generation, tags)
    "Bulbasaur": ("Bulbasaur", 1, ["grass", "poison"]),
    "Charmander": ("Charmander", 1, ["fire"]),
    "Squirtle": ("Squirtle", 1, ["water"]),
}


def resolve_metadata(path: Path) -> tuple[str, int, list[str]]:
    for key, (pokemon, gen, types) in POKEMON_MAPPING.items():
        if key.lower() in path.stem.lower():
            return pokemon, gen, types
    raise ValueError(f"Could not resolve metadata for {path}")


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
