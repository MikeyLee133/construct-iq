# ConstructIQ

AI-powered construction project management. Organise inspection reports, photos, receipts, and notes by project phase — then ask questions in plain English across all your documents.

## Features

- **Multi-project management** — create and switch between projects, each with status tracking and total spend
- **7 default construction phases** — Pre-Construction through Final Inspection, each with its own documents, notes, and expenses
- **Document upload** — PDFs and images (JPG/PNG) extracted and indexed automatically for AI search
- **Notes** — write, edit, and save notes directly in the app; fully searchable by AI
- **Expense tracking** — log costs by category with optional receipt attachments; phase and project totals calculated automatically
- **AI Q&A** — ask plain-English questions across all documents and notes in a project, with source citations showing which phase and file the answer came from

## How it works

1. Upload an inspection report, photo, or write a note in any phase
2. The app extracts text (PDF parsing + OCR for images), splits it into chunks, and stores vector embeddings in ChromaDB
3. When you ask a question, the most relevant chunks are retrieved and sent to a local LLM (Ollama) with a grounded prompt
4. The answer is returned with citations — no hallucination, answers are based only on your documents

## Tech stack

| Purpose | Tool |
|---|---|
| UI | Streamlit |
| Database | SQLite |
| PDF extraction | pdfplumber |
| Image OCR | pytesseract |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB |
| LLM | Ollama (local, free) |

## Install

```bash
pip install ".[dev]"
```

Requires [Ollama](https://ollama.ai) running locally:
```bash
ollama pull llama3
```

## Run

```bash
streamlit run app.py
```

## Project structure

```
construct_iq/
├── app.py                     # Streamlit entry point + router
└── construct_iq/
    ├── config.py              # All constants and settings
    ├── database.py            # SQLite operations (projects, phases, notes, expenses, documents)
    ├── storage.py             # File upload, PDF/OCR text extraction, chunking
    ├── embedder.py            # sentence-transformers + ChromaDB indexing and retrieval
    ├── llm.py                 # Ollama interface with grounded prompting
    └── ui/
        ├── projects.py        # Project dashboard, create, edit
        ├── phases.py          # Phase view and status
        ├── documents.py       # Document upload and listing
        ├── notes.py           # Notes editor
        ├── expenses.py        # Expense logging
        └── qa.py              # AI Q&A chat interface
```

## Tests

```bash
pytest
```
