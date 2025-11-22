import json
from pathlib import Path

from PIL import Image, ImageDraw

from ingestion.image_ingestion import (
    extract_text_from_image,
    ingest_image,
    write_image_record,
)


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

    record = ingest_image(str(img_path), pokemon="Bulbasaur", generation=1)

    assert record["id"] == img_path.stem
    assert record["modality"] == "image"
    assert record["source_path"].endswith("bulbasaur_card.png")
    assert record["pokemon"] == "Bulbasaur"
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
