"""
config.py
---------
All constants and settings in one place.
"""

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).parent.parent
DATA_DIR     = BASE_DIR / "data"
DB_PATH      = DATA_DIR / "construct_iq.db"
UPLOADS_DIR  = DATA_DIR / "uploads"
CHROMA_DIR   = DATA_DIR / "chroma"

# Ensure directories exist at import time
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# ── Construction phases ───────────────────────────────────────────────────────

DEFAULT_PHASES = [
    "Pre-Construction",
    "Site Prep & Foundation",
    "Framing",
    "Rough-In (Electrical, Plumbing, HVAC)",
    "Insulation & Drywall",
    "Finishing",
    "Final Inspection & Closeout",
]

# ── Project status options ────────────────────────────────────────────────────

PROJECT_STATUSES = ["Active", "On Hold", "Completed"]

# ── Phase status options ──────────────────────────────────────────────────────

PHASE_STATUSES = ["Not Started", "In Progress", "Complete"]

# ── Expense categories ────────────────────────────────────────────────────────

EXPENSE_CATEGORIES = [
    "Labour",
    "Materials",
    "Permits",
    "Inspections",
    "Equipment",
    "Other",
]

# ── Supported file types ──────────────────────────────────────────────────────

SUPPORTED_DOCUMENT_TYPES = ["pdf"]
SUPPORTED_IMAGE_TYPES    = ["jpg", "jpeg", "png"]
SUPPORTED_FILE_TYPES     = SUPPORTED_DOCUMENT_TYPES + SUPPORTED_IMAGE_TYPES

# ── AI / embeddings ───────────────────────────────────────────────────────────

EMBEDDING_MODEL  = "all-MiniLM-L6-v2"   # fast, good quality, runs locally
OLLAMA_MODEL     = "llama3"              # change to any model you have pulled
CHUNK_SIZE       = 500                   # characters per chunk
CHUNK_OVERLAP    = 50                    # overlap between chunks
TOP_K_RESULTS    = 5                     # number of chunks to retrieve per query
