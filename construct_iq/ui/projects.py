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
        st.markdown("""
        <div style="padding:0.25rem 0 0.75rem">
            <h1 style="margin:0 0 4px;font-size:2.2rem;font-weight:800;color:#0f172a;letter-spacing:-1px">
                🏗️ ConstructIQ
            </h1>
            <p style="margin:0;color:#64748b;font-size:0.9rem">
                AI-powered construction project management
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("＋ New Project", use_container_width=True, type="primary"):
            st.session_state["view"] = "create_project"
            st.rerun()

    projects = get_all_projects()

    if not projects:
        st.info("No projects yet. Click '＋ New Project' to get started.")
        return

    total    = len(projects)
    active   = sum(1 for p in projects if p["status"] == "Active")
    on_hold  = sum(1 for p in projects if p["status"] == "On Hold")
    done     = sum(1 for p in projects if p["status"] == "Completed")
    st.caption(f"{total} project{'s' if total != 1 else ''}  ·  {active} active  ·  {on_hold} on hold  ·  {done} completed")
    st.write("")

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
            if st.button("Open →", key=f"open_{project['id']}", use_container_width=True, type="primary"):
                st.session_state["view"]       = "project"
                st.session_state["project_id"] = project["id"]
                st.rerun()
            if st.button("Edit", key=f"edit_{project['id']}", use_container_width=True):
                st.session_state["view"]       = "edit_project"
                st.session_state["project_id"] = project["id"]
                st.rerun()


def show_create_project() -> None:
    _, col, _ = st.columns([1, 3, 1])
    with col:
        st.markdown("<h2 style='margin-bottom:1.5rem'>New Project</h2>", unsafe_allow_html=True)

        with st.form("create_project_form"):
            name       = st.text_input("Project name *", placeholder="123 Main St Renovation")
            address    = st.text_input("Address", placeholder="123 Main St, City, State")
            status     = st.selectbox("Status", PROJECT_STATUSES)
            start_date = st.date_input("Start date", value=date.today())

            c1, c2 = st.columns(2)
            with c1:
                submitted = st.form_submit_button("Create Project", use_container_width=True, type="primary")
            with c2:
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

    _, col, _ = st.columns([1, 3, 1])
    with col:
        st.markdown(f"<h2 style='margin-bottom:1.5rem'>Edit — {project['name']}</h2>", unsafe_allow_html=True)

        with st.form("edit_project_form"):
            name       = st.text_input("Project name *", value=project["name"])
            address    = st.text_input("Address", value=project["address"])
            status     = st.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index(project["status"]))
            start_date = st.date_input(
                "Start date",
                value=date.fromisoformat(project["start_date"]) if project["start_date"] else date.today(),
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
            with c2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state["view"] = "project"
                    st.rerun()
            with c3:
                delete = st.form_submit_button("Delete", use_container_width=True)

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
