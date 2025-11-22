import logging
from pathlib import Path

from ingestion.text_ingestion import ingest_pdf, ingest_txt, write_text_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_TEXT_DIR = Path("data/raw/text")

POKEMON_MAPPING = {  # basic metadata (name, generation, types)
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
    for path in RAW_TEXT_DIR.iterdir():
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".pdf", ".txt"}:
            continue

        pokemon, generation, types = resolve_metadata(path)

        if path.suffix.lower() == ".pdf":
            record = ingest_pdf(
                str(path), pokemon=pokemon, generation=generation, types=types
            )
            write_text_record(record)
        elif path.suffix.lower() == ".txt":
            record = ingest_txt(
                str(path), pokemon=pokemon, generation=generation, types=types
            )
            write_text_record(record)


if __name__ == "__main__":
    main()
