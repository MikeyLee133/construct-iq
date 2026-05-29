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
    "Active":    ("#dcfce7", "#166534"),
    "On Hold":   ("#fef3c7", "#92400e"),
    "Completed": ("#e0e7ff", "#3730a3"),
}


def _status_badge(status: str) -> str:
    bg, fg = _STATUS_BADGE.get(status, ("#f5f5f4", "#57534e"))
    return (
        f'<span style="background:{bg};color:{fg};border-radius:6px;'
        f'padding:3px 10px;font-size:11px;font-weight:600;letter-spacing:0.05em;'
        f'text-transform:uppercase;font-family:Inter,sans-serif">{status}</span>'
    )


def show_projects_dashboard() -> None:
    col_title, col_btn = st.columns([7, 1])
    with col_title:
        st.markdown("""
        <div style="padding:0.25rem 0 1.25rem">
            <p style="margin:0 0 6px;font-size:0.7rem;font-weight:700;color:#79716b;
                      letter-spacing:0.12em;text-transform:uppercase;font-family:'Inter',sans-serif">
                Construction Management
            </p>
            <h1 style="margin:0 0 8px;font-size:2.6rem;font-weight:800;color:#0c0a09;
                       letter-spacing:-1.5px;font-family:'Inter',sans-serif;line-height:1.05">
                ConstructIQ
            </h1>
            <p style="margin:0;color:#79716b;font-size:0.95rem;font-family:'Inter',sans-serif;
                      font-weight:400">
                Track every phase, cost, and document — all in one place.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.write("")
        st.write("")
        st.write("")
        if st.button("＋ New Project", use_container_width=True, type="primary"):
            st.session_state["view"] = "create_project"
            st.rerun()

    projects = get_all_projects()

    if not projects:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#79716b;font-family:'Inter',sans-serif">
            <p style="font-size:2.5rem;margin:0 0 12px">🏗️</p>
            <p style="font-size:1.1rem;font-weight:600;color:#0c0a09;margin:0 0 6px">No projects yet</p>
            <p style="font-size:0.9rem;margin:0">Click <strong>＋ New Project</strong> to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    total   = len(projects)
    active  = sum(1 for p in projects if p["status"] == "Active")
    on_hold = sum(1 for p in projects if p["status"] == "On Hold")
    done    = sum(1 for p in projects if p["status"] == "Completed")

    st.markdown(
        f'<p style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#79716b;'
        f'margin:0 0 1.25rem;font-weight:500">'
        f'{total} project{"s" if total != 1 else ""}'
        f'<span style="margin:0 8px;color:#d6d0ca">·</span>'
        f'<span style="color:#166534">{active} active</span>'
        f'<span style="margin:0 8px;color:#d6d0ca">·</span>'
        f'{on_hold} on hold'
        f'<span style="margin:0 8px;color:#d6d0ca">·</span>'
        f'{done} completed</p>',
        unsafe_allow_html=True,
    )

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
            st.markdown(
                f'<h3 style="margin:0 0 4px;font-size:1.15rem;font-weight:700;'
                f'color:#0c0a09;font-family:\'Inter\',sans-serif;letter-spacing:-0.3px">'
                f'{project["name"]}</h3>',
                unsafe_allow_html=True,
            )
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
        st.markdown("""
        <div style="margin-bottom:1.75rem">
            <p style="margin:0 0 4px;font-size:0.7rem;font-weight:700;color:#79716b;
                      letter-spacing:0.12em;text-transform:uppercase;font-family:'Inter',sans-serif">
                Projects
            </p>
            <h2 style="margin:0;font-size:1.75rem;font-weight:800;color:#0c0a09;
                       letter-spacing:-0.75px;font-family:'Inter',sans-serif">
                New Project
            </h2>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div style="margin-bottom:1.75rem">
            <p style="margin:0 0 4px;font-size:0.7rem;font-weight:700;color:#79716b;
                      letter-spacing:0.12em;text-transform:uppercase;font-family:'Inter',sans-serif">
                Projects
            </p>
            <h2 style="margin:0;font-size:1.75rem;font-weight:800;color:#0c0a09;
                       letter-spacing:-0.75px;font-family:'Inter',sans-serif">
                {project['name']}
            </h2>
        </div>
        """, unsafe_allow_html=True)

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
