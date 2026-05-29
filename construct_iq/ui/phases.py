"""
ui/phases.py
------------
Phase view — documents, notes, and expenses tabs per phase.
"""

import streamlit as st

from construct_iq.config import PHASE_STATUSES
from construct_iq.database import get_phases, get_project, get_project_expenses, update_phase_status
from construct_iq.ui.checklist import show_checklist
from construct_iq.ui.documents import show_documents
from construct_iq.ui.expenses import show_expenses
from construct_iq.ui.notes import show_notes

_PHASE_STATUS_STYLE = {
    "Not Started": ("⚪", "#79716b"),
    "In Progress": ("🟡", "#92400e"),
    "Complete":    ("🟢", "#166534"),
}


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
        if project["address"]:
            st.markdown(
                f'<p style="margin:0 0 4px;font-size:0.7rem;font-weight:700;color:#79716b;'
                f'letter-spacing:0.12em;text-transform:uppercase;font-family:\'Inter\',sans-serif">'
                f'📍 {project["address"]}</p>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<h1 style="margin:0;font-size:2rem;font-weight:800;color:#0c0a09;'
            f'letter-spacing:-1px;font-family:\'Inter\',sans-serif;line-height:1.1">'
            f'{project["name"]}</h1>',
            unsafe_allow_html=True,
        )
    with col_qa:
        if st.button("🤖 Ask AI", use_container_width=True, type="primary"):
            st.session_state["view"] = "qa"
            st.rerun()

    # ── Summary metrics ───────────────────────────────────────────────────────
    phases      = get_phases(project_id)
    expenses    = get_project_expenses(project_id)
    total_spend = sum(e["amount"] for e in expenses)
    completed   = sum(1 for p in phases if p["status"] == "Complete")
    in_progress = sum(1 for p in phases if p["status"] == "In Progress")

    st.write("")
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
    icon, _ = _PHASE_STATUS_STYLE.get(phase["status"], ("⚪", "#79716b"))

    with st.expander(f"{icon}  {phase['name']}", expanded=False):
        col_status, col_badge, _ = st.columns([2, 2, 3])
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
        with col_badge:
            _, color = _PHASE_STATUS_STYLE.get(phase["status"], ("⚪", "#79716b"))
            st.markdown(
                f'<p style="margin:0;padding-top:0.6rem;font-size:0.78rem;font-weight:600;'
                f'color:{color};font-family:\'Inter\',sans-serif;text-transform:uppercase;'
                f'letter-spacing:0.05em">{phase["status"]}</p>',
                unsafe_allow_html=True,
            )

        st.write("")

        # Tabs
        chk_tab, doc_tab, note_tab, expense_tab = st.tabs(
            ["✅ Checklist", "📄 Documents", "📝 Notes", "💰 Expenses"]
        )

        with chk_tab:
            show_checklist(phase["id"])
        with doc_tab:
            show_documents(phase["id"], phase["name"])
        with note_tab:
            show_notes(phase["id"])
        with expense_tab:
            show_expenses(phase["id"])
