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
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800&display=swap" rel="stylesheet">
<style>
/* ── Base ────────────────────────────────────────── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stBottom"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background-color: #f7f5f1 !important;
}

/* ── Chrome ──────────────────────────────────────── */
footer { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stAppViewBlockContainer"] { padding-top: 2.5rem; }

/* ── Cards ───────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid #e9e4dc !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 4px 20px rgba(0,0,0,0.05) !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.07), 0 16px 48px rgba(0,0,0,0.07) !important;
    transform: translateY(-2px) !important;
}

/* ── Metrics ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e9e4dc !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: #0c0a09 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #79716b !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="stMetricDelta"] { font-family: 'Inter', sans-serif !important; }

/* ── Progress bar ────────────────────────────────── */
[role="progressbar"] {
    height: 6px !important;
    border-radius: 99px !important;
    background: #e9e4dc !important;
}
[role="progressbar"] > div {
    background: #0c0a09 !important;
    border-radius: 99px !important;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button,
.stFormSubmitButton > button {
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
    padding: 0.5rem 1rem !important;
}
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: #0c0a09 !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.2) !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
    background: #292524 !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.28) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]),
.stFormSubmitButton > button:not([kind="primaryFormSubmit"]) {
    background: #ffffff !important;
    border: 1px solid #ddd8d2 !important;
    color: #44403c !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover,
.stFormSubmitButton > button:not([kind="primaryFormSubmit"]):hover {
    background: #fafaf9 !important;
    border-color: #a8a29e !important;
}

/* ── Expanders ───────────────────────────────────── */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e9e4dc !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #0c0a09 !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
    background: #fafaf9 !important;
}

/* ── Tabs ────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #e9e4dc !important;
    gap: 0 !important;
    padding: 0 !important;
}
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #79716b !important;
    padding: 0.65rem 1.1rem !important;
    border-radius: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0c0a09 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #0c0a09 !important;
}

/* ── Inputs ──────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea {
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
    border-color: #ddd8d2 !important;
    background: #ffffff !important;
    color: #0c0a09 !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #0c0a09 !important;
    box-shadow: 0 0 0 3px rgba(12,10,9,0.08) !important;
}
[data-baseweb="select"] > div {
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
    border-color: #ddd8d2 !important;
    background: #ffffff !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #0c0a09 !important;
    box-shadow: 0 0 0 3px rgba(12,10,9,0.08) !important;
}

/* ── Widget labels ───────────────────────────────── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #44403c !important;
}

/* ── Captions ────────────────────────────────────── */
[data-testid="stCaptionContainer"] p,
small {
    font-family: 'Inter', sans-serif !important;
    color: #79716b !important;
}

/* ── File uploader ───────────────────────────────── */
[data-testid="stFileUploader"] section {
    border-radius: 12px !important;
    border: 2px dashed #d6d0ca !important;
    background: #fafaf9 !important;
}

/* ── Dataframe ───────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #e9e4dc !important;
}

/* ── Alert / info boxes ──────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Divider ─────────────────────────────────────── */
hr { border-color: #e9e4dc !important; }
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
