import logging
from pathlib import Path
from typing import Dict

from data.pokemon_mappings import POKEMON_MAPPING
from ingestion.image_ingestion import ingest_image, write_image_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_IMAGE_DIR = Path("data/raw/images")


def resolve_metadata(path: Path) -> tuple[str, int, list[str]]:
    for key, (pokemon, gen, types) in POKEMON_MAPPING.items():
        if key.lower() in path.stem.lower():
            return pokemon, gen, types
    raise ValueError(f"Could not resolve metadata for {path}")


def add_image(raw_file: Path) -> Dict[str, str]:
    """
    Given a path to an image file, move/copy it into data/raw/images,
    infer metadata, ingest it, and append to data/processed/images.jsonl.
    """
    RAW_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    target = RAW_IMAGE_DIR / raw_file.name
    if raw_file.resolve() != target.resolve():
        target.write_bytes(raw_file.read_bytes())

    pokemon, generation, types = resolve_metadata(target)

    record = ingest_image(
        str(target),
        pokemon=pokemon,
        generation=generation,
        types=types,
    )
    write_image_record(record)
    logging.info("Added image %s for %s (gen %d)", target, pokemon, generation)
    return record


def main() -> None:
    if not RAW_IMAGE_DIR.exists():
        logging.warning("Image directory %s does not exist", RAW_IMAGE_DIR)
        return

    for path in RAW_IMAGE_DIR.iterdir():
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".png", ".jpg"}:
            continue

        pokemon, generation, types = resolve_metadata(path)

        record = ingest_image(
            str(path), pokemon=pokemon, generation=generation, types=types
        )
        write_image_record(record)


if __name__ == "__main__":
    main()
