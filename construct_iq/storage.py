"""
storage.py
----------
File upload, retrieval, and text extraction from PDFs and images.
"""

import uuid
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

from construct_iq.config import CHUNK_OVERLAP, CHUNK_SIZE, UPLOADS_DIR


def save_file(phase_id: int, filename: str, file_bytes: bytes) -> tuple[str, str]:
    """
    Save uploaded file to disk.
    Returns (file_path, file_type).
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    unique_name = f"{phase_id}_{uuid.uuid4().hex}_{filename}"
    dest = UPLOADS_DIR / unique_name
    dest.write_bytes(file_bytes)
    return str(dest), ext


def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract plain text from a PDF or image file.
    Returns empty string if extraction fails.
    """
    try:
        if file_type == "pdf":
            return _extract_pdf(file_path)
        if file_type in ("jpg", "jpeg", "png"):
            return _extract_image(file_path)
    except Exception:
        pass
    return ""


def _extract_pdf(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n\n".join(text_parts)


def _extract_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


def chunk_text(text: str) -> list[str]:
    """
    Split text into overlapping chunks for embedding.
    Returns list of non-empty chunks.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return [c for c in chunks if c]
