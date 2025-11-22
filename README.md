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
This project uses `pytest` for unit tests, with an initial focus on validating the text ingestion pipeline for Pokémon starter content.
Tests live under the `tests/` directory and exercise the core text ingestion functions in ingestion.text_ingestion.​

Current coverage includes:

 - **PDF text extraction**: a Bulbasaur Bulbapedia PDF under `data/raw/text/` is used to verify `extract_text_from_pdf`, asserting that the file exists, the extracted text is reasonably long, and it contains key markers like “Bulbasaur”, “Grass”, and “Poison” after Unicode normalization.

 - **PDF ingestion schema**: `test_ingest_pdf_returns_expected_schema` checks that `ingest_pdf` returns a well‑formed record with stable fields (`id`, `modality`, `source_path`, `text`, `pokemon`, `generation`, `tags`) and that the ingested text still includes Bulbasaur content after normalization.

 - **TXT ingestion**: `test_ingest_txt_with_tmp_file` creates a temporary Charmander text file via `tmp_path` to validate `ingest_txt`, ensuring IDs, paths, Pokémon metadata, generation, tags, and text content (including “Charmander” and “Fire-type”) are populated as expected.

 - **JSONL writing**: `test_write_record_creates_valid_jsonl` monkeypatches `ingestion.text_ingestion.TEXT_JSONL` to a temporary path, calls `write_record`, and asserts that a single valid JSONL line is written and that deserialized fields such as id, pokemon, and text content match the original record.

As the RAG pipeline grows, this suite will be extended to cover embedding, retrieval, graph construction, and answer‑generation helpers so that tests evolve alongside new capabilities.
