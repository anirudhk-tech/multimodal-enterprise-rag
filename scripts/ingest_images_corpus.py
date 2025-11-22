import logging
from pathlib import Path

from ingestion.image_ingestion import ingest_image, write_image_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_IMAGE_DIR = Path("data/raw/images")

POKEMON_MAPPING = {  # basic metadata (name, generation)
    "Bulbasaur": ("Bulbasaur", 1, ["Grass", "Poison"]),
    "Charmander": ("Charmander", 1, ["Fire"]),
    "Squirtle": ("Squirtle", 1, ["Water"]),
}


def resolve_metadata(path: Path) -> tuple[str, int, list[str]]:
    for key, (pokemon, gen, types) in POKEMON_MAPPING.items():
        if key.lower() in path.stem.lower():
            return pokemon, gen, types
    raise ValueError(f"Could not resolve metadata for {path}")


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
