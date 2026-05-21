# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# First-time setup
pre-commit install

# Run the app
streamlit run app.py

# Install dependencies
pip install ".[dev]"

# Run tests
pytest

# Lint
ruff check construct_iq/ app.py

# Type check
mypy construct_iq/ --ignore-missing-imports
```

Requires [Ollama](https://ollama.ai) running locally with a model pulled:
```bash
ollama pull llama3
ollama serve
```

## Architecture

Data flows in one direction: **storage/database → embedder → llm → ui**

```
database.py    SQLite — projects, phases, notes, expenses, documents
storage.py     file upload, PDF text extraction, OCR, text chunking
embedder.py    sentence-transformers + ChromaDB (index, query, delete)
llm.py         Ollama interface with grounded prompting
ui/            Streamlit components (one file per concern)
app.py         session-state router — wires views together
```

## Key design decisions

**`config.py` is the single source of truth** for all constants — phase names, expense categories, file types, model names, chunk sizes, directory paths. Change behaviour by editing config, not source files.

**SQLite for structured data, ChromaDB for vectors.** SQLite stores all metadata (projects, phases, notes, expenses, document records). ChromaDB stores text embeddings for semantic search. They are kept in sync — deleting a document removes its chunks from both stores.

**Everything stored locally.** No external API calls for AI — Ollama runs on the user's machine. Files are saved to `data/uploads/`, the SQLite database to `data/construct_iq.db`, and ChromaDB to `data/chroma/`. The entire `data/` directory is gitignored.

**Session-state routing.** `app.py` reads `st.session_state["view"]` and `st.session_state["project_id"]` to decide which UI component to render. Navigation works by setting these values and calling `st.rerun()`.

**Each document/note is indexed independently.** When a document is deleted, its chunks are removed from ChromaDB by source key (`phase_id_filename`). Notes use `note_{id}` as their source key. This means the vector store stays in sync with the database without a full reindex.

## Adding a new phase category or expense type

Edit `DEFAULT_PHASES` or `EXPENSE_CATEGORIES` in `config.py`. No other file needs to change. Note: `DEFAULT_PHASES` only applies to newly created projects — existing projects keep their current phases.

## Changing the LLM or embedding model

Edit `OLLAMA_MODEL` or `EMBEDDING_MODEL` in `config.py`. If you change the embedding model, delete `data/chroma/` and re-upload all documents — embeddings from different models are not compatible.
