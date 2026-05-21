# ConstructIQ

AI-powered construction project management. Upload inspection reports, photos, and notes for each phase of your build — then ask questions in plain English across all your documents.

## Features

- Manage multiple construction projects
- Track progress through 7 default construction phases
- Upload PDFs and images per phase
- Write and save notes per phase
- Track expenses with optional receipt attachments
- Ask AI questions across all project documents

## Install

```bash
pip install ".[dev]"
```

Requires [Ollama](https://ollama.ai) running locally with a model pulled:
```bash
ollama pull llama3
```

## Run

```bash
streamlit run app.py
```

## Tests

```bash
pytest
```
