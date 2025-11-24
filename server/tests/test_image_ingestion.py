import json
from pathlib import Path
from typing import Any, Dict

import scripts.ingest_images_corpus as ingest_corpus
from ingestion.image_ingestion import (
    extract_text_from_image,
    ingest_image,
    write_image_record,
)
from PIL import Image, ImageDraw


def _create_test_image(path: Path, text: str = "Bulbasaur") -> None:
    img = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 80), text, fill="black")
    img.save(path)


def test_extract_text_from_image_simple(tmp_path: Path):
    img_path = tmp_path / "bulbasaur_img.png"
    _create_test_image(img_path, text="This is a Bulbasaur")

    extracted_text = extract_text_from_image(str(img_path))

    assert len(extracted_text) > 0
    assert "bulb" in extracted_text.lower()  # partial to accomodate OCR quirks


def test_ingest_image(tmp_path: Path):
    img_path = tmp_path / "bulbasaur_card.png"
    _create_test_image(img_path, text="Bulbasaur")

    record = ingest_image(
        str(img_path), pokemon="Bulbasaur", generation=1, types=["Grass", "Poison"]
    )

    assert record["id"] == img_path.stem
    assert record["modality"] == "image"
    assert record["source_path"].endswith("bulbasaur_card.png")
    assert record["pokemon"] == "Bulbasaur"
    assert record["types"] == ["Grass", "Poison"]
    assert record["generation"] == 1
    assert "starter" in record["tags"]
    assert "image" in record["tags"]
    assert "bulbasaur" in [t.lower() for t in record["tags"]]
    assert len(record["text"]) > 0


def test_write_image_record_creates_valid_jsonl(tmp_path, monkeypatch):
    temp_jsonl = tmp_path / "images.jsonl"
    monkeypatch.setattr("ingestion.image_ingestion.IMAGES_JSONL", temp_jsonl)

    record = {
        "id": "bulbasaur_test",
        "modality": "text",
        "source_path": "data/raw/text/bulbasaur.pdf",
        "text": "Bulbasaur is a Grass/Poison-type starter Pokémon.",
        "pokemon": "Bulbasaur",
        "types": ["Grass", "Poison"],
        "generation": 1,
        "tags": ["starter", "bulbasaur"],
    }

    write_image_record(record)

    assert temp_jsonl.exists()
    lines = temp_jsonl.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    loaded = json.loads(lines[0])
    assert loaded["id"] == "bulbasaur_test"
    assert loaded["pokemon"] == "Bulbasaur"
    assert "Bulbasaur" in loaded["text"]


def test_add_image_moves_file_and_ingests(tmp_path, monkeypatch):
    raw_dir = tmp_path / "data" / "raw" / "images"
    monkeypatch.setattr(ingest_corpus, "RAW_IMAGE_DIR", raw_dir, raising=True)

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_file = upload_dir / "charmander_card.png"
    upload_file.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header bytes

    calls: Dict[str, Any] = {}

    def fake_ingest_image(path: str, pokemon: str, generation: int, types: list[str]):
        calls["ingest_args"] = (Path(path), pokemon, generation, types)
        return {
            "id": "charmander_card",
            "modality": "image",
            "source_path": path,
            "pokemon": pokemon,
            "generation": generation,
            "types": types,
            "text": "Charmander card OCR text.",
        }

    def fake_write_image_record(record: Dict[str, Any]) -> None:
        calls["written_record"] = record

    monkeypatch.setattr(ingest_corpus, "ingest_image", fake_ingest_image, raising=True)
    monkeypatch.setattr(
        ingest_corpus, "write_image_record", fake_write_image_record, raising=True
    )

    record = ingest_corpus.add_image(upload_file)

    target = raw_dir / upload_file.name
    assert target.exists()
    ingest_path, pokemon, gen, types = calls["ingest_args"]
    assert ingest_path == target
    assert pokemon == "Charmander"
    assert gen == 1
    assert "fire" in [t.lower() for t in types]
    assert calls["written_record"] == record
    assert record["pokemon"] == "Charmander"
