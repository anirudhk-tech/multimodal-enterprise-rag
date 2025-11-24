# Hybrid Multi-Modal Enterprise RAG System

## Project Goals

Before building any ingestion or pipeline logic, this project defines how solution quality will be measured and what outcomes are expected:

- **Correct Response:** A response is correct if it is factually accurate, relevant to the query, and grounded in the ingested enterprise data. Responses must reference supporting sources whenever possible.
- **Supported Query Types:** System supports factual lookups, summarization, and multi-step reasoning across ingested modalities of text, image, and audio.
- **Success Metrics:** Evaluation tracks retrieval quality, hallucination rate (frequency of unsupported/generated outputs), answer accuracy, and response latency.
- **Graceful Failure:** If confident answers cannot be generated, the system will fallback to informative error messages or request clarification, avoiding hallucinated or unsupported output.

All pipeline components will include functional unit tests, and evaluation reports will be automatically logged per query for continuous tracking.

## Project Overview

This project aims to design and implement a modular, scalable prototype of an enterprise-grade Retrieval-Augmented Generation (RAG) system. It supports ingestion of heterogeneous data sources from three modalities — text (PDF, TXT), images (JPG, PNG), and audio (MP3) — enabling a unified, multimodal knowledge base.

Core features include:

- Modular pipeline design prioritizing robustness and ease of testing
- Ingestion with modality-specific preprocessing: OCR for images, ASR transcription for audio, text extraction for documents
- Entity and relationship extraction leveraging large language models (LLMs)
- Construction of a cross-modal knowledge graph for semantic and multi-hop retrieval
- Hybrid search combining keyword matching and vector similarity search for improved retrieval relevance
- A demo user interface with file upload, natural language queries, and visualization of results including graph exploration

## Architecture Highlights

The system is architected as composed, independently testable modules:

- **Data Ingestion & Preprocessing:**  
  - Text documents parsed to clean text  
  - Images OCR-processed to extract text  
  - Audio transcribed via automatic speech recognition  

- **Query Processing & Retrieval:**  
  - Query triage and rewriting for enhanced search precision  
  - Agent-driven orchestration combining vector and keyword search  
  - Multi-modal indexing with managed vector databases  

- **Entity & Relationship Extraction:**  
  - Use of LLMs for named entity recognition and relationship identification across modalities  
  - Cross-modal entity linking to unify references (e.g., same person in text and audio)  
  - Schema inference for knowledge graph construction  

- **Knowledge Graph & Hybrid Search:**  
  - Graph database (e.g., Neo4j) storing entities and relations  
  - Hybrid search combining graph traversal and dense vector retrieval  
  - Integration with LLM for grounded response generation  

- **User Interface & Evaluation:**  
  - Intuitive UI or notebook for file upload, querying, and visualizing answers  
  - Logging of evaluation metrics per query for continuous improvement  
  - Graceful handling of ambiguous or incomplete queries with fallback responses

This design ensures an evaluation-first, extensible system tailored to enterprise needs and demonstrates cutting-edge multimodal retrieval-augmented generation technology with professional documentation and engineering best practices.

---

## Evaluation-First Pipeline Design

Supported query types are:
- Lookup: precise factual retrieval from ingested Pokémon starter data.
- Summarization: concise synthesis of multi-source information about a starter’s role, traits, or history.
- Semantic linkages: relational retrieval spanning connected entities, such as cross-generation comparisons or shared typings.

Evaluation goals are:
- Retrieval quality: measuring how accurately and consistently the system returns relevant context and correct answers.
- Hallucination control: reducing unsupported or fabricated information in responses, using retrieved context as the single source of truth.
- Latency: tracking end-to-end response time to ensure interactive performance under typical query loads.

### Tests
This project uses `pytest` for unit tests, with an initial focus on validating the text, image, and audio ingestion pipelines for Pokémon starter content. [web:195][web:201]  
Tests live under the `tests/` directory and exercise the core ingestion functions in `ingestion.text_ingestion`, `ingestion.image_ingestion`, and `ingestion.audio_ingestion`. 

Current coverage includes:

- **PDF text extraction**: 
A Bulbasaur Bulbapedia PDF under `data/raw/text/` is used to verify `extract_text_from_pdf`, asserting that the file exists, the extracted text is reasonably long, and it contains key markers like “Bulbasaur”, “Grass”, and “Poison” after Unicode normalization.

- **PDF ingestion schema**: 
`test_ingest_pdf_returns_expected_schema` checks that `ingest_pdf` returns a well‑formed record with stable fields (`id`, `modality`, `source_path`, `text`, `pokemon`, `generation`, `tags`) and that the ingested text still includes Bulbasaur content after normalization. [web:199][web:201]  

- **TXT ingestion**: 
`test_ingest_txt_with_tmp_file` creates a temporary Charmander text file via `tmp_path` to validate `ingest_txt`, ensuring IDs, paths, Pokémon metadata, generation, tags, and text content (including “Charmander” and “Fire-type”) are populated as expected.   

- **Text JSONL writing**: 
`test_write_text_record_creates_valid_jsonl` monkeypatches `ingestion.text_ingestion.TEXT_JSONL` to a temporary path, calls `write_text_record`, and asserts that a single valid JSONL line is written and that deserialized fields such as `id`, `pokemon`, and `text` content match the original record.  

- **Image OCR extraction**: 
`test_extract_text_from_image_simple` programmatically creates a temporary Bulbasaur image using Pillow, runs `extract_text_from_image` on it, and asserts that some text is returned and that the lowercase output contains the substring `"bulb"` to accommodate OCR quirks. 

- **Image ingestion schema**: 
`test_ingest_image` creates a synthetic Bulbasaur card image, passes it to `ingest_image`, and verifies that the returned record has the expected schema (`id` from the filename stem, `modality == "image"`, correct `source_path`, `pokemon`, `generation`, informative `text`) and that the `tags` include `"starter"`, `"image"`, and a Bulbasaur tag.

- **Image JSONL writing**: 
`test_write_image_record_creates_valid_jsonl` monkeypatches `ingestion.image_ingestion.IMAGES_JSONL` to a temporary file, calls `write_image_record` with a synthetic Bulbasaur record, and asserts that the file is created, exactly one JSONL line is written, and that the deserialized `id`, `pokemon`, and `text` fields match the original record.

- **Audio transcription smoke test**: 
`test_text_from_audio_smoke` creates a temporary Bulbasaur MP3 under `tmp_path`, monkeypatches `ingestion.audio_ingestion.extract_text_from_audio` and passes a `FakeModel` that mimics Whisper’s `transcribe` output, then asserts that the returned text is non-empty and that `"bulbasaur"` appears in the lowercase transcript.

- **Audio ingestion schema**: 
`test_ingest_audio_builds_record` writes a synthetic Bulbasaur MP3, injects a `FakeModel` so no real Whisper model is loaded, calls `ingest_audio`, and verifies that the resulting record has the expected schema (`id` from the filename stem, `modality == "audio"`, correct `source_path`, `pokemon`, `generation`, and `tags` including `"starter"`, `"audio"`, and a Bulbasaur tag) and that the transcript text contains `"bulbasaur"`. 

- **Audio JSONL writing**: 
`test_write_audio_record_creates_valid_jsonl` monkeypatches `ingestion.audio_ingestion.AUDIO_JSONL` to a temporary file, calls `write_audio_record` with a synthetic Bulbasaur audio record, and asserts that the file is created, exactly one JSONL line is written, and that the deserialized `id`, `pokemon`, and `text` fields match the original record.

- **Graph merge from JSONL**: 
`test_build_graph_merges_fragments` uses tmp_path to create temporary `text.jsonl`, `audio.jsonl`, and `images.jsonl` files under an isolated `data/processed/` directory, each containing a single synthetic record for Bulbasaur, Charmander, and Squirtle, so graph building is exercised without touching real project data.

- **Entity extraction JSON handling**: 
`test_extract_entities_parse_valid_json` constructs a `fake_payload` dict with one Bulbasaur node, Grass and Poison type nodes, Pokémon‑type edges, an evolution edge to Ivysaur, and a `mentions_edges` entry linking "bulbasaur_audio" to "Charmander", then serializes it to `fake_json`.

- **API health check**: 
`test_health` uses FastAPI’s `TestClient` to call the `/health` endpoint and asserts that it returns a 200 status code with the exact JSON body `{"status": "ok"}`, serving as a quick smoke test that the server is up and correctly wired.

- **Ingestion API smoke**: 
`test_ingest_endpoint_smoke` monkeypatches `api.main.run_full_ingest` with a fake_ingest function that simply flips a flag in a local calls dict, then posts to `/ingest` and asserts that the response status is 200, the JSON `message` starts with `"Ingestion process"`, and that the fake ingest function was actually invoked, confirming the endpoint correctly triggers the ingestion pipeline without running the full job in tests.

- **Graph build API smoke**: 
`test_process_endpoint_smoke` similarly monkeypatches `api.main.run_build_graph` with a `fake_process` function that marks `calls["process"] = True`, sends a POST request to `/process`, and asserts that the response is 200, the JSON `message` contains `"Graph built"`, and the fake function was called, verifying that the graph‑building endpoint is correctly wired to its script entrypoint while keeping tests fast and side‑effect free.

- **Single audio file add**: 
`test_add_audio_moves_file_and_ingests` points `RAW_AUDIO_DIR` at a temp directory, fakes `ingest_audio` / `write_audio_record`, writes a dummy Bulbasaur MP3, calls `add_audio(...)`, and asserts the file is copied under data/raw/audio/ and that ingestion is invoked with the expected Bulbasaur metadata.

- **Single image file add**: 
`test_add_image_moves_file_and_ingests` redirects `RAW_IMAGE_DIR` to a temp directory, monkeypatches `ingest_image` / `write_image_record`, creates a fake Charmander PNG, runs `add_image(...)`, and checks that the image is copied under data/raw/images/ and that ingestion is called with the correct Charmander metadata.

- **Single text file add (PDF/TXT)**: 
`test_add_text_pdf_moves_file_and_ingests` and `test_add_text_txt_uses_ingest_txt` redirect `RAW_TEXT_DIR`, fake `ingest_pdf` / `ingest_txt` and `write_text_record`, feed in synthetic Squirtle PDF and Bulbasaur TXT files, and assert that each is copied under data/raw/text/ and routed to the correct ingestion function with the right Pokémon metadata.

- **Chat API**:  
`test_chat_endpoint_uses_openai_and_returns_content` monkeypatches the `openai_client` inside the chat routes so that `responses.create` returns a deterministic fake answer. It then posts to `/chat` with a sample question and asserts that the status is 200, the JSON contains a `content` field equal to that fake answer, and that the fake client was invoked with the expected user message — confirming correct wiring without calling the real OpenAI API.

- **Graph API**:  
`test_graph_endpoint_404_when_missing` overrides `GRAPH_JSON` to point to a non-existent temp file and asserts that `GET /graph` returns a 404 with `"Graph not built yet"`.  
`test_graph_endpoint_returns_graph_json` then points `GRAPH_JSON` at a temp file containing a minimal graph payload and verifies that `GET /graph` returns 200 with the expected `pokemon_nodes` and `type_nodes`, demonstrating both the error and success paths of the endpoint.

- **Logs API**:  
`test_logs_endpoint_returns_parsed_records` monkeypatches `LOG_PATH` to a temp `eval.jsonl` containing a single JSONL entry, calls `GET /logs`, and asserts that the response is a list of parsed objects whose first item includes the correct `query` and nested `focused_pokemon.name` — verifying that the endpoint parses JSONL into structured records rather than returning raw text.

- **DeepEval + Chat**:  
`test_bulbasaur_types` uses FastAPI’s `TestClient` to query the `/chat` endpoint with the prompt **“What types is Bulbasaur?”**. It then wraps the model’s reply in an `LLMTestCase` and evaluates it using DeepEval’s `AnswerRelevancyMetric` (configured with a relevance threshold and model). The test asserts that the answer is sufficiently relevant to a short gold snippet describing **Bulbasaur as a dual-type Grass/Poison Pokémon**, confirming the chat endpoint’s semantic correctness rather than just string matching.

As the RAG pipeline grows, this suite will be extended to cover embedding, retrieval, graph construction, and answer‑generation helpers so that tests evolve alongside new capabilities.
