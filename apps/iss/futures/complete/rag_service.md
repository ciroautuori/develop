# ✅ Feature: Personal RAG Service

## Status
- **Status**: Completed
- **Completion Date**: 2025-12-25
- **Priority**: High

## Description
A retrieval-augmented generation system that allows the AI agents to consult internal documentation from `docs/ISS_OPERATIVO/`. This ensures that tender analysis and project drafting are compliant with the organization's rules and historical best practices.

## Implementation Details
- **Architecture**: Lightweight HTTP-based client to avoid local dependencies (Torch/CUDA).
- **Service**: `rag_service.py` using `httpx`.
- **Vector DB**: Centralized ChromaDB (V2 API).
- **Embeddings**: Generated via `central-ollama` using `llama3.2:3b`.
- **Ingestion**: `ingest_docs.py` processes markdown files in chunks and uploads them with metadata.

## Benefits
- Reduced hallucinations in AI responses.
- Compliance with local regulations.
- Reusability of project templates.
