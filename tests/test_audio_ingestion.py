import json
from pathlib import Path
from typing import Dict

from ingestion.audio_ingestion import (
    extract_text_from_audio,
    ingest_audio,
    write_audio_record,
)


class FakeModel:
    def transcribe(self, path: str) -> Dict[str, str]:
        assert path.endswith("bulbasaur.mp3")
        return {"text": "This is a Bulbasaur audio clip"}


def test_text_from_audio_smoke(tmp_path: Path, monkeypatch):
    fake_audio = tmp_path / "bulbasaur.mp3"
    fake_audio.write_bytes(b"RIFF....")

    def fake_transcribe(path: str) -> str:
        assert path.endswith("bulbasaur.mp3")
        return "This is a Bulbasaur audio clip"

    monkeypatch.setattr(
        "ingestion.audio_ingestion.extract_text_from_audio", fake_transcribe
    )

    text = extract_text_from_audio(str(fake_audio), model=FakeModel())
    assert "bulbasaur" in text.lower()


def test_ingest_audio_builds_record(tmp_path: Path, monkeypatch):
    audio_path = tmp_path / "bulbasaur.mp3"
    audio_path.write_bytes(b"RIFF....")

    monkeypatch.setattr(
        "ingestion.audio_ingestion.write_audio_record",
        lambda p: "Bulbasaur is a Grass/Poison-type starter Pokémon.",
    )

    record = ingest_audio(
        str(audio_path),
        pokemon="Bulbasaur",
        generation=1,
        types=["Grass", "Poison"],
        model=FakeModel(),
    )

    assert record["id"] == audio_path.stem
    assert record["modality"] == "audio"
    assert record["source_path"].endswith("bulbasaur.mp3")
    assert record["pokemon"] == "Bulbasaur"
    assert record["types"] == ["Grass", "Poison"]
    assert record["generation"] == 1
    assert "audio" in record["tags"]
    assert "starter" in record["tags"]
    assert "bulbasaur" in [t.lower() for t in record["tags"]]
    assert "bulbasaur" in record["text"].lower()


def test_write_audio_record_creates_valid_jsonl(tmp_path: Path, monkeypatch):
    temp_jsonl = tmp_path / "audio.jsonl"
    monkeypatch.setattr("ingestion.audio_ingestion.AUDIO_JSONL", temp_jsonl)

    record = {
        "id": "bulbasaur_audio_test",
        "modality": "audio",
        "source_path": "data/raw/audio/bulbasaur_sample.mp3",
        "text": "Bulbasaur audio sample transcript.",
        "pokemon": "Bulbasaur",
        "generation": 1,
        "types": ["Grass", "Poison"],
        "tags": ["starter", "audio", "bulbasaur"],
    }

    write_audio_record(record)

    assert temp_jsonl.exists()
    lines = temp_jsonl.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    loaded = json.loads(lines[0])
    assert loaded["id"] == "bulbasaur_audio_test"
    assert loaded["pokemon"] == "Bulbasaur"
    assert "Bulbasaur" in loaded["text"]
