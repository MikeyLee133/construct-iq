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
footer { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1rem; }
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
