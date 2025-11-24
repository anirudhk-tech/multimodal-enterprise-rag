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
  - Vector embeddings and similarity search for a hybrid context

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

`test_health` uses FastAPI’s `TestClient` to call the `/health` endpoint and asserts that it returns a 200 status code with the exact JSON body `{"status": 
"ok"}`, serving as a quick smoke test that the server is up and correctly wired.

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

## Data Ingestion and Preprocessing

This project ingests a multimodal Pokémon corpus across **text, images, and audio**, normalizes it into a unified schema, and enriches every record with graph-friendly metadata.

### Supported modalities and formats
- **Text:** `.pdf`, `.txt`  
- **Images:** `.jpg`, `.jpeg`, `.png`  
- **Audio:** `.mp3`  
- *(Video `.mp4` is planned for future expansion.)*

### Modal-specific preprocessing pipeline

**Text (PDF / TXT)**  
- PDFs are parsed into raw text using a document text extractor.  
- TXT files are read directly as UTF-8.  
- Each record is normalized (Unicode cleanup), tagged with Pokémon metadata (`pokemon`, `generation`, `types`), and labeled as `modality="text"`.  
- A document-level embedding is computed and stored in the vector database.

**Images (PNG / JPG)**  
- Images are saved under `data/raw/images`.  
- OCR extracts any Pokémon-related text (e.g., card text, labels).  
- Records include OCR text, metadata fields, `modality="image"`, and tags like `"image"`, `"starter"`, and the Pokémon name.  
- OCR text is embedded and upserted into the vector database so images participate in text-based search.

**Audio (MP3)**  
- Audio files are stored under `data/raw/audio`.  
- A speech-to-text step produces transcripts.  
- Each transcript is stored as `text` with matching metadata fields and tags (`"audio"`, `"starter"`, Pokémon name).  
- Transcript text is embedded and added to the vector database.

### Unified schema and metadata enrichment

Across all modalities, the ingestion layer produces a consistent JSON record shape, for example:

```json
{
  "id": "bulbasaur_bulbapedia_pdf",
  "modality": "text",
  "source_path": "data/raw/text/Bulbasaur-…pdf",
  "text": "Bulbasaur is a dual-type Grass/Poison starter Pokémon from Generation 1...",
  "pokemon": "Bulbasaur",
  "types": ["Grass", "Poison"],
  "generation": 1,
  "tags": ["starter", "bulbasaur", "gen1"]
}
```

## Entity & Relationship Extraction and Hybrid Indexing

This project turns the raw multimodal corpus into a structured Pokémon knowledge graph and a parallel vector index that power hybrid retrieval.

**Entity and relationship extraction**  
For each ingested record (text, image OCR, audio transcript), an LLM is prompted to extract structured entities and relations from the raw text. The extraction step produces normalized Pokémon-centric records, including fields such as `pokemon`, `types`, `generation`, `evolutions`, and cross-references between entities (e.g., “Bulbasaur → Ivysaur → Venusaur”). These structured outputs are appended to intermediate JSONL files, which serve as the canonical source for graph construction and downstream analysis.

**Cross-modal entity linking**  
Because all modalities share the same metadata schema, mentions of the same Pokémon across PDFs, images, and audio are aligned via their shared `pokemon` field and tags. For example, a Bulbasaur entry extracted from a PDF, an OCR’d Bulbasaur trading card, and a Bulbasaur audio clip transcript are all linked to the same logical node in the graph and can be retrieved together. This cross-modal alignment allows the system to answer questions by combining evidence from multiple sources that talk about the same entity.

**Graph schema generation**  
From the extracted entities and relations, the pipeline infers and materializes a graph schema that includes:
- Pokémon nodes (name, generation, primary/secondary types)  
- Type nodes (e.g., Grass, Fire, Water)  
- Edges for Pokémon–type membership, evolution chains, and text/image/audio “mentions”

The graph builder exports this schema to CSV and `graph.json`, which are then served through the `/graph` API and visualized in the UI as an interactive knowledge graph.

**Parallel vector index construction**  
In parallel with graph construction, the ingestion pipeline builds a vector index over all textual signals in the corpus (PDF text, OCR output, audio transcripts). Each record’s text is embedded into a dense vector and stored together with its metadata (`pokemon`, `modality`, `tags`) in the vector store. This yields a hybrid retrieval layer: graph lookups provide explicit entity–relation structure, while vector search provides semantic similarity over the raw multimodal content, and both are combined at query time to ground the LLM’s answers.

## User Interface / Demo

The project ships with a web UI that exposes the full multimodal RAG pipeline end-to-end.

**Uploading new files**  
The top bar includes an Upload dialog that accepts `.pdf`, `.txt`, `.png`, `.jpg`, and `.mp3` files. On upload, the file is sent to the backend, routed to the appropriate ingestion path (text, image, or audio), and fed through the same preprocessing, entity extraction, graph building, and vector indexing pipeline used for the initial corpus. After ingestion completes, the UI triggers a graph refresh so new entities and relationships become immediately explorable.

**Natural language querying**  
A chat-style panel on the left allows users to type free-form questions about the starter Pokémon domain. Each query calls the `/chat` endpoint, which combines:
- Knowledge graph context (focused Pokémon node + neighbors)  
- Vector search results from the multimodal corpus (PDF text, OCR’d images, audio transcripts)  

The model’s answer is streamed back into the chat history, alternating user and assistant turns in a familiar messaging layout.

**Graph-aware answer exploration**  
The right side of the UI renders an interactive knowledge graph built from the extracted entities and relationships. When the chatbot focuses on a particular Pokémon, that node is highlighted in the graph so users can see its types, evolutions, and related entities. Users can visually explore the graph to understand how different Pokémon, types, and documents connect behind each answer.

**Evaluation logging and logs viewer**  
Every `/chat` request writes a structured evaluation log entry capturing:
- Query text, model answer, and the graph/vector context used  
- Basic evaluation metadata (e.g., whether the answer was grounded in the graph, latency placeholder)  
- The focused Pokémon node, if one was resolved from the query  

A Logs dialog in the top bar (next to Upload) lets users inspect recent queries. Each log entry shows the question, answer, focused Pokémon, and expandable sections for context and evaluation fields. This makes it easy to debug retrieval behavior, verify grounding, and demonstrate the evaluation-first design of the system during the demo.

## How to Run
1. Prerequisites
- Python 3.9+
- Node.js + pnpm / npm / yarn
- An OpenAI API key (OPENAI_API_KEY)
- A Qdrant Cloud cluster URL and API key

2. Backend setup
From the `server/` directory, create and activate a virtual environment and install dependencies:

```bash
cd server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a .env file in server/ with at least:

```text
OPENAI_API_KEY=your_openai_key

QDRANT_URL=https://YOUR-CLUSTER-ID.region.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=pokemon_corpus
```

(Optional) Run the backend test suite:
```bash
pytest
```

3. Initialize the Qdrant collection
Create the pokemon_corpus collection once in Qdrant Cloud (via the Qdrant UI or HTTP):

Collection name: pokemon_corpus

Vector size: 1536

Distance: Cosine

After this, the backend will upsert points into this collection automatically during ingestion.

4. Run the ingestion and graph build pipelines
From `server/`:

```bash
cd server
python -m scripts.ingest    # ingest and preprocess the multimodal corpus
python -m scripts.process   # build the Pokémon knowledge graph (graph.json + CSVs)
```

- `scripts.ingest`

Ingests PDFs, text files, images, and audio into normalized JSONL records.

Extracts entities and relationships and writes intermediate structured data.

Computes embeddings and upserts vectors + payloads into Qdrant.

- `scripts.process`

Reads the structured JSONL corpus.

Builds the Pokémon knowledge graph (nodes + edges).

Exports graph.json and CSVs consumed by the /graph API and UI.

You should re‑run scripts.ingest (and then scripts.process) whenever you add new raw data under `data/raw/....`

5. Run the backend API
Start the FastAPI app:

```bash
uvicorn api.main:app --reload --port 8000
```

Key routes:

- `GET /health` – health check

- `POST /ingest` – manually trigger ingestion (thin wrapper over scripts.ingest)

- `POST /process` – rebuild the graph (wrapper over scripts.process)

- `GET /graph` – serve graph.json for the UI graph view

- `POST /chat` – hybrid RAG chat over the knowledge graph + Qdrant vectors

- `GET /logs` – return evaluation logs for each chat query

6. Run the frontend
From the web/ (Next.js) directory:

```bash
cd web
pnpm install        # or npm install / yarn
pnpm dev            # or npm run dev / yarn dev
```

By default the frontend expects the API at http://localhost:8000 (configurable via an env or config file such as API_BASE). Open the UI at http://localhost:3000.


7. Using the demo
Upload new files

Use the Upload button in the top bar to add .pdf, .txt, .png/.jpg, or .mp3 files.

The backend routes them through the same ingestion + embedding pipeline.

After uploading new data, re‑run python -m scripts.process or hit POST /process so the knowledge graph reflects the updated corpus.

## Ask questions

Use the chat panel on the left to ask natural language questions about the starter Pokémon domain.

Each query calls `/chat`, which combines knowledge‑graph context with vector search results from Qdrant to generate an answer.

## Explore the graph

The right panel shows the Pokémon knowledge graph built from the extracted entities and relationships.

The graph is currently rendered as an explorable visualization; the API also returns a “focused Pokémon” node per query, which is available for future UI enhancements, but the current UI does not auto‑highlight that node yet.

## Inspect evaluation logs

Use the Logs button in the top bar to open the evaluation log viewer.

Each log entry shows the query, answer, focused Pokémon, and the stored context/evaluation fields, which is useful for understanding and debugging retrieval behavior.

8. Optional: run evaluation tests
To run the evaluation‑focused tests (including the DeepEval‑backed check on /chat):

```bash
cd server
pytest tests/test_deepeval.py
```
This exercises the hybrid RAG pipeline on a small set of Pokémon questions and asserts answer relevance against a gold snippet.
