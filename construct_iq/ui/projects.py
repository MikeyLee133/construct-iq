"""
ui/projects.py
--------------
Project list, create, and edit UI.
"""

from datetime import date

import streamlit as st

from construct_iq.config import DEFAULT_PHASES, PROJECT_STATUSES
from construct_iq.database import (
    create_phases_for_project,
    create_project,
    delete_project,
    get_all_projects,
    get_phases,
    get_project_expenses,
    update_project,
)


_STATUS_BADGE = {
    "Active":    ("#dcfce7", "#15803d"),
    "On Hold":   ("#fef9c3", "#854d0e"),
    "Completed": ("#dbeafe", "#1e40af"),
}


def _status_badge(status: str) -> str:
    bg, fg = _STATUS_BADGE.get(status, ("#f1f5f9", "#475569"))
    return (
        f'<span style="background:{bg};color:{fg};border-radius:4px;'
        f'padding:2px 10px;font-size:12px;font-weight:600">{status}</span>'
    )


def show_projects_dashboard() -> None:
    col_title, col_btn = st.columns([7, 1])
    with col_title:
        st.title("🏗️ ConstructIQ")
        st.caption("AI-powered construction project management")
    with col_btn:
        st.write("")
        if st.button("＋ New Project", use_container_width=True):
            st.session_state["view"] = "create_project"
            st.rerun()

    projects = get_all_projects()

    if not projects:
        st.info("No projects yet. Click '＋ New Project' to get started.")
        return

    for project in projects:
        _project_card(project)


def _project_card(project: dict) -> None:
    phases   = get_phases(project["id"])
    expenses = get_project_expenses(project["id"])
    total    = sum(e["amount"] for e in expenses)

    completed = sum(1 for p in phases if p["status"] == "Complete")
    progress  = completed / len(phases) if phases else 0

    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 2, 1])

        with col1:
            st.markdown(f"### {project['name']}")
            if project["address"]:
                st.caption(f"📍 {project['address']}")
            st.markdown(_status_badge(project["status"]), unsafe_allow_html=True)
            st.write("")
            st.progress(progress, text=f"{completed}/{len(phases)} phases complete")

        with col2:
            st.metric("Total Spend", f"${total:,.2f}")
            if project["start_date"]:
                st.caption(f"Started {project['start_date']}")

        with col3:
            if st.button("Open →", key=f"open_{project['id']}", use_container_width=True):
                st.session_state["view"]       = "project"
                st.session_state["project_id"] = project["id"]
                st.rerun()
            if st.button("Edit", key=f"edit_{project['id']}", use_container_width=True):
                st.session_state["view"]       = "edit_project"
                st.session_state["project_id"] = project["id"]
                st.rerun()


def show_create_project() -> None:
    st.title("New Project")

    with st.form("create_project_form"):
        name       = st.text_input("Project name *", placeholder="123 Main St Renovation")
        address    = st.text_input("Address", placeholder="123 Main St, City, State")
        status     = st.selectbox("Status", PROJECT_STATUSES)
        start_date = st.date_input("Start date", value=date.today())

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Create Project", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state["view"] = "dashboard"
                st.rerun()

    if submitted:
        if not name.strip():
            st.error("Project name is required.")
            return
        project_id = create_project(name.strip(), address.strip(), status, start_date)
        create_phases_for_project(project_id, DEFAULT_PHASES)
        st.success(f"Project '{name}' created with {len(DEFAULT_PHASES)} default phases.")
        st.session_state["view"]       = "project"
        st.session_state["project_id"] = project_id
        st.rerun()


def show_edit_project(project_id: int) -> None:
    from construct_iq.database import get_project
    project = get_project(project_id)
    if not project:
        st.error("Project not found.")
        return

    st.title(f"Edit — {project['name']}")

    with st.form("edit_project_form"):
        name       = st.text_input("Project name *", value=project["name"])
        address    = st.text_input("Address", value=project["address"])
        status     = st.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index(project["status"]))
        start_date = st.date_input(
            "Start date",
            value=date.fromisoformat(project["start_date"]) if project["start_date"] else date.today(),
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("Save", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state["view"] = "project"
                st.rerun()
        with col3:
            delete = st.form_submit_button("Delete Project", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Project name is required.")
            return
        update_project(project_id, name.strip(), address.strip(), status, start_date)
        st.success("Project updated.")
        st.session_state["view"] = "project"
        st.rerun()

    if delete:
        delete_project(project_id)
        st.session_state["view"] = "dashboard"
        st.rerun()
