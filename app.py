"""
app.py
------
ConstructIQ — AI-powered construction project management.
Run with:  streamlit run app.py
"""

import streamlit as st

from construct_iq.database import init_db
from construct_iq.ui.phases import show_project_view
from construct_iq.ui.projects import show_create_project, show_edit_project, show_projects_dashboard
from construct_iq.ui.qa import show_qa

st.set_page_config(
    page_title="ConstructIQ",
    page_icon="🏗️",
    layout="wide",
)

st.markdown("""
<style>
/* ── Chrome ──────────────────────────────────────── */
footer { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1.5rem; }

/* ── Cards ───────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: #e2e8f0 !important;
    box-shadow: 0 2px 10px rgba(15,23,42,0.07) !important;
    transition: box-shadow 0.15s ease !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 4px 20px rgba(15,23,42,0.12) !important;
}

/* ── Metrics ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricValue"] { font-weight: 700 !important; color: #0f172a !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.8rem !important; font-weight: 500 !important; text-transform: uppercase !important; letter-spacing: 0.04em !important; }

/* ── Progress bar ────────────────────────────────── */
[role="progressbar"] {
    height: 8px !important;
    border-radius: 99px !important;
    background: #e0e7ff !important;
}
[role="progressbar"] > div {
    background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
    border-radius: 99px !important;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5) !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 14px rgba(79,70,229,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Expanders ───────────────────────────────────── */
[data-testid="stExpander"] {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: #1e293b !important;
}

/* ── Tabs ────────────────────────────────────────── */
button[data-baseweb="tab"] { font-weight: 500 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #1d4ed8 !important; }

/* ── Inputs ──────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    border-radius: 8px !important;
}
[data-baseweb="select"] > div {
    border-radius: 8px !important;
}

/* ── Divider ─────────────────────────────────────── */
hr { border-color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# Initialise DB on every startup — safe to call repeatedly
init_db()

# ── Session state defaults ────────────────────────────────────────────────────

if "view" not in st.session_state:
    st.session_state["view"] = "dashboard"

if "project_id" not in st.session_state:
    st.session_state["project_id"] = None

# ── Router ────────────────────────────────────────────────────────────────────

view       = st.session_state["view"]
project_id = st.session_state["project_id"]

if view == "dashboard":
    show_projects_dashboard()

elif view == "create_project":
    show_create_project()

elif view == "edit_project" and project_id:
    show_edit_project(project_id)

elif view == "project" and project_id:
    show_project_view(project_id)

elif view == "qa" and project_id:
    show_qa(project_id)

else:
    st.session_state["view"] = "dashboard"
    st.rerun()
