"""
ui/phases.py
------------
Phase view — documents, notes, and expenses tabs per phase.
"""

import streamlit as st

from construct_iq.config import PHASE_STATUSES
from construct_iq.database import get_phases, get_project, get_project_expenses, update_phase_status
from construct_iq.ui.documents import show_documents
from construct_iq.ui.expenses import show_expenses
from construct_iq.ui.notes import show_notes


def show_project_view(project_id: int) -> None:
    project = get_project(project_id)
    if not project:
        st.error("Project not found.")
        return

    # ── Header ────────────────────────────────────────────────────────────────
    col_back, col_title, col_qa = st.columns([1, 6, 1])
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state["view"] = "dashboard"
            st.rerun()
    with col_title:
        st.markdown(
            f"<h1 style='margin:0 0 4px;font-size:2rem;font-weight:800;color:#0f172a;letter-spacing:-0.5px'>{project['name']}</h1>",
            unsafe_allow_html=True,
        )
        if project["address"]:
            st.caption(f"📍 {project['address']}")
    with col_qa:
        if st.button("🤖 Ask AI", use_container_width=True, type="primary"):
            st.session_state["view"] = "qa"
            st.rerun()

    # ── Summary metrics ───────────────────────────────────────────────────────
    phases   = get_phases(project_id)
    expenses = get_project_expenses(project_id)
    total_spend = sum(e["amount"] for e in expenses)
    completed   = sum(1 for p in phases if p["status"] == "Complete")
    in_progress = sum(1 for p in phases if p["status"] == "In Progress")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Phases Complete", f"{completed} / {len(phases)}")
    m2.metric("In Progress", in_progress)
    m3.metric("Total Spend", f"${total_spend:,.2f}")
    m4.metric("Status", project["status"])

    st.divider()

    # ── Phase list ────────────────────────────────────────────────────────────
    for phase in phases:
        _phase_section(phase)


def _phase_section(phase: dict) -> None:
    status_icon = {"Not Started": "⚪", "In Progress": "🟡", "Complete": "🟢"}.get(phase["status"], "⚪")

    with st.expander(f"{status_icon}  {phase['name']}", expanded=False):
        # Status selector
        col_status, _ = st.columns([2, 5])
        with col_status:
            new_status = st.selectbox(
                "Phase status",
                PHASE_STATUSES,
                index=PHASE_STATUSES.index(phase["status"]),
                key=f"status_{phase['id']}",
                label_visibility="collapsed",
            )
            if new_status != phase["status"]:
                update_phase_status(phase["id"], new_status)
                st.rerun()

        # Tabs for documents, notes, expenses
        doc_tab, note_tab, expense_tab = st.tabs(["📄 Documents", "📝 Notes", "💰 Expenses"])

        with doc_tab:
            show_documents(phase["id"], phase["name"])
        with note_tab:
            show_notes(phase["id"])
        with expense_tab:
            show_expenses(phase["id"])
