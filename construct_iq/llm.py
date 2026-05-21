"""
llm.py
------
Ollama interface. Builds a grounded prompt from retrieved chunks
and returns a plain-English answer with source citations.
"""

import ollama

from construct_iq.config import OLLAMA_MODEL


def answer(question: str, chunks: list[dict]) -> str:
    """
    Generate an answer grounded in the retrieved document chunks.
    Returns the answer string, or an error message if Ollama is unavailable.
    """
    if not chunks:
        return "I couldn't find any relevant documents to answer that question. Try uploading inspection reports, notes, or other documents for this project."

    context = _build_context(chunks)
    prompt  = _build_prompt(question, context)

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return (
            f"Could not reach Ollama: {e}\n\n"
            "Make sure Ollama is running (`ollama serve`) and you have the model pulled (`ollama pull llama3`)."
        )


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {chunk['phase_name']} — {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)


def _build_prompt(question: str, context: str) -> str:
    return f"""You are an assistant helping a construction project manager understand their project documents.

Answer the question below using ONLY the provided document excerpts.
Be specific and cite which phase and document your answer comes from.
If the answer is not in the documents, say so clearly — do not make anything up.

Documents:
{context}

Question: {question}

Answer:"""
