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
    "Demolition",
    "Pre-Construction & Special Inspection",
    "Temporary Power",
    "Excavation",
    "Foundation",
    "Sewer",
    "Underground Plumbing",
    "Framing",
    "Rough-In (Electrical, Plumbing, HVAC)",
    "Insulation & Drywall",
    "Finishing",
    "Final Inspections & Closeout",
]

DEFAULT_PHASE_CHECKLISTS: dict[str, list[dict[str, str]]] = {
    "Demolition": [
        {"text": "Survey done of the lot",                                                          "category": "Permits & Surveys"},
        {"text": "Tree survey completed",                                                           "category": "Permits & Surveys"},
        {"text": "File demo permit with the City of Seattle",                                       "category": "Permits & Surveys"},
        {"text": "Call 811 before any digging",                                                    "category": "Utilities"},
        {"text": "Contact Seattle City Light — submit application to remove power connection",      "category": "Utilities"},
        {"text": "Submit side sewer permit with the city",                                         "category": "Utilities"},
        {"text": "Contact PSE (gas disconnection)",                                                "category": "Utilities"},
        {"text": "Place water valve near property line (keeps access during construction)",         "category": "Utilities"},
        {"text": "Contact Clean Air Agency — fill out required paperwork for demo",                "category": "Environmental & Safety"},
        {"text": "Asbestos survey and removal",                                                    "category": "Environmental & Safety"},
        {"text": "Rat and pest control — schedule 2 weeks before demo date",                       "category": "Environmental & Safety"},
        {"text": "Meet inspector on site to discuss demo plan",                                    "category": "Environmental & Safety"},
        {"text": "Spray water on structure during demo to contain dust",                           "category": "During Demolition"},
        {"text": "Track garbage volume and material types being hauled",                           "category": "During Demolition"},
        {"text": "Document where all garbage and materials are being sent",                        "category": "During Demolition"},
    ],
    "Pre-Construction & Special Inspection": [
        {"text": "Tree protection fencing up with signs (follow plan details or to drip line)",    "category": "Site Setup"},
        {"text": "Silt fencing installed around perimeter of lot",                                 "category": "Site Setup"},
        {"text": "Temporary road built with clean, washed rock",                                   "category": "Site Setup"},
        {"text": "Geotechnical engineer present for special inspection",                           "category": "Inspection"},
        {"text": "Excavator present for special inspection",                                       "category": "Inspection"},
    ],
    "Temporary Power": [
        {"text": "Acquire temporary power pole",                                                   "category": ""},
        {"text": "Contact City Light — apply for temporary power pole",                            "category": ""},
        {"text": "Confirm utility pole connection point and best location for temp pole",           "category": ""},
        {"text": "Electrician: ground temp power pole and prepare for inspection",                 "category": ""},
        {"text": "Call SDCI when ready for inspection",                                            "category": ""},
        {"text": "After SDCI approval: contact City Light to connect temp power",                  "category": ""},
    ],
    "Excavation": [
        {"text": "Have survey company mark house corners (or mark yourself)",                      "category": ""},
        {"text": "Assess land area — plan phased approach if insufficient space for excavated dirt", "category": ""},
        {"text": "Check dirt quality with excavator and geotech — no excess clay or silt",         "category": ""},
        {"text": "Verify excavation depth is correct for foundation height",                       "category": ""},
        {"text": "Backfill and compact soil inside foundation walls once walls are complete",       "category": ""},
        {"text": "Place 4\" of clean, washed rock on top of compacted soil",                       "category": ""},
        {"text": "Install conduit for electrical (requires inspection)",                           "category": ""},
    ],
    "Foundation": [
        {"text": "Confirm foundation crew follows engineering requirements (not architectural plans)", "category": "General"},
        {"text": "Install UFER wire with footings",                                                "category": "Footings"},
        {"text": "Footings inspection passed",                                                     "category": "Footings"},
        {"text": "Install hold-downs and J-hooks per spec",                                        "category": "Walls"},
        {"text": "Foundation walls inspection passed",                                             "category": "Walls"},
        {"text": "Backfill with dirt and rock before slab",                                        "category": "Slab"},
        {"text": "Underground plumbing installed before slab placement",                           "category": "Slab"},
        {"text": "Vapor barrier and insulation boards placed",                                     "category": "Slab"},
        {"text": "Foundation slab inspection passed",                                              "category": "Slab"},
    ],
    "Sewer": [
        {"text": "File side sewer permit",                                                         "category": "Permits"},
        {"text": "Complete and notarize all required city paperwork",                              "category": "Permits"},
        {"text": "Assess sewer main — determine if relining is needed",                            "category": "Installation"},
        {"text": "If deep dig: install safety box to prevent soil collapse",                       "category": "Installation"},
        {"text": "Pipe size: 4\" for single family, 6\" for multiple units",                       "category": "Installation"},
        {"text": "Confirm adequate clean rock under and above the pipe",                           "category": "Installation"},
        {"text": "Drainage cover (storm water) inspection passed",                                 "category": "Inspections"},
        {"text": "Sewage cover (sewage and waste) inspection passed",                              "category": "Inspections"},
    ],
    "Underground Plumbing": [
        {"text": "Backfill with dirt and rock complete",                                           "category": ""},
        {"text": "Plumbers briefed on plans and bathroom/kitchen layout",                          "category": ""},
        {"text": "Pipes drilled through foundation walls (not placed alongside walls)",            "category": ""},
        {"text": "Schedule inspection — pressure test by inspector",                               "category": ""},
        {"text": "Plumbing inspection passed",                                                     "category": ""},
    ],
    "Framing": [
        {"text": "Plans finalized — any changes approved by structural engineer",                  "category": ""},
        {"text": "All plumbing pipes routed inside walls",                                         "category": ""},
        {"text": "Adequate glue used on stairs and hangers",                                       "category": ""},
        {"text": "Garbage and recycling storage bin (plywood) built",                             "category": ""},
        {"text": "Structural framing inspection passed",                                           "category": ""},
    ],
    "Rough-In (Electrical, Plumbing, HVAC)": [
        {"text": "Rough plumbing inspection passed",                                               "category": ""},
        {"text": "Rough electrical inspection passed",                                             "category": ""},
        {"text": "Rough mechanical (HVAC) inspection passed",                                     "category": ""},
    ],
    "Insulation & Drywall": [
        {"text": "Insulation inspection passed",                                                   "category": ""},
        {"text": "Drywall inspection passed (if required for scope/fire rating)",                  "category": ""},
    ],
    "Final Inspections & Closeout": [
        {"text": "Mechanical final inspection passed",                                             "category": ""},
        {"text": "Plumbing final inspection passed",                                              "category": ""},
        {"text": "Electrical final inspection passed",                                             "category": ""},
        {"text": "Final building inspection passed",                                              "category": ""},
    ],
}

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
