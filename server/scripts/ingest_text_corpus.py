import logging
from pathlib import Path
from typing import Dict

from data.pokemon_mappings import POKEMON_MAPPING
from ingestion.text_ingestion import ingest_pdf, ingest_txt, write_text_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

RAW_TEXT_DIR = Path("data/raw/text")


def resolve_metadata(path: Path) -> tuple[str, int, list[str]]:
    for key, (pokemon, gen, types) in POKEMON_MAPPING.items():
        if key.lower() in path.stem.lower():
            return pokemon, gen, types
    raise ValueError(f"Could not resolve metadata for {path}")


def add_text(raw_file: Path) -> Dict[str, str]:
    """
    Given a path to a .pdf or .txt file, move/copy it into data/raw/text,
    infer metadata, ingest it, and append to data/processed/text.jsonl.
    """
    suffix = raw_file.suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise ValueError(f"Unsupported text file type: {raw_file}")

    RAW_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    target = RAW_TEXT_DIR / raw_file.name
    if raw_file.resolve() != target.resolve():
        target.write_bytes(raw_file.read_bytes())

    pokemon, generation, types = resolve_metadata(target)

    if suffix == ".pdf":
        record = ingest_pdf(
            str(target),
            pokemon=pokemon,
            generation=generation,
            types=types,
        )
    else:  # ".txt"
        record = ingest_txt(
            str(target),
            pokemon=pokemon,
            generation=generation,
            types=types,
        )

    write_text_record(record)
    logging.info("Added text %s for %s (gen %d)", target, pokemon, generation)
    return record


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
