import json
import unicodedata
from pathlib import Path

from ingestion.text_ingestion import (
    extract_text_from_pdf,
    ingest_pdf,
    ingest_txt,
    write_text_record,
)

PDF_PATH = Path(
    "data/raw/text/"
    "Bulbasaur (Pokémon) - Bulbapedia, the community-driven Pokémon encyclopedia.pdf"
)


def _normalize(text: str) -> str:
    # Normalize Unicode to avoid accent issues like Pok\u00e9mon vs Pokemon
    return unicodedata.normalize("NFKC", text)


def test_extract_text_from_pdf_bulbasaur():
    assert PDF_PATH.exists(), "Bulbasaur PDF missing under data/raw/text"

    raw_text = extract_text_from_pdf(str(PDF_PATH))
    text = _normalize(raw_text)

    assert len(text) > 5_000
    assert "Bulbasaur" in text
    assert "Grass" in text
    assert "Poison" in text


def test_ingest_pdf_returns_expected_schema():
    assert PDF_PATH.exists(), "Bulbasaur PDF missing under data/raw/text"

    record = ingest_pdf(str(PDF_PATH), pokemon="Bulbasaur", generation=1)

    assert record["id"] == PDF_PATH.stem
    assert record["modality"] == "text"
    assert record["source_path"].endswith(PDF_PATH.name)
    assert record["pokemon"] == "Bulbasaur"
    assert record["generation"] == 1
    assert "starter" in record["tags"]
    assert "bulbasaur" in record["tags"]
    assert len(record["text"]) > 0
    assert "Bulbasaur" in _normalize(record["text"])


def test_ingest_txt_with_tmp_file(tmp_path):
    txt_path = tmp_path / "charmander.txt"
    txt_path.write_text(
        "Charmander is a Fire-type starter Pokémon from Generation I.",
        encoding="utf-8",
    )

    record = ingest_txt(str(txt_path), pokemon="Charmander", generation=1)

    assert record["id"] == "charmander"
    assert record["modality"] == "text"
    assert record["source_path"].endswith("charmander.txt")
    assert record["pokemon"] == "Charmander"
    assert record["generation"] == 1
    assert "starter" in record["tags"]
    assert "charmander" in record["tags"]
    assert "Charmander" in record["text"]
    assert "Fire-type" in record["text"]


def test_write_textrecord_creates_valid_jsonl(tmp_path, monkeypatch):
    temp_jsonl = tmp_path / "text.jsonl"
    monkeypatch.setattr("ingestion.text_ingestion.TEXT_JSONL", temp_jsonl)

    record = {
        "id": "bulbasaur_test",
        "modality": "text",
        "source_path": "data/raw/text/bulbasaur.pdf",
        "text": "Bulbasaur is a Grass/Poison-type starter Pokémon.",
        "pokemon": "Bulbasaur",
        "generation": 1,
        "tags": ["starter", "bulbasaur"],
    }

    write_text_record(record)

    assert temp_jsonl.exists()
    lines = temp_jsonl.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    loaded = json.loads(lines[0])
    assert loaded["id"] == "bulbasaur_test"
    assert loaded["pokemon"] == "Bulbasaur"
    assert "Bulbasaur" in loaded["text"]
