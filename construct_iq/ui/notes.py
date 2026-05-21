"""
ui/notes.py
-----------
Notes editor per phase — create, edit, delete.
"""

import streamlit as st

from construct_iq.database import create_note, delete_note, get_notes, update_note
from construct_iq.embedder import delete_source, index_chunks
from construct_iq.storage import chunk_text


def _note_source(note_id: int) -> str:
    return f"note_{note_id}"


def _get_project_id(phase_id: int) -> int:
    from construct_iq.database import _conn
    with _conn() as con:
        row = con.execute(
            "SELECT p.project_id, p.name FROM phases p WHERE p.id = ?", (phase_id,)
        ).fetchone()
        return row["project_id"] if row else 0


def _get_phase_name(phase_id: int) -> str:
    from construct_iq.database import _conn
    with _conn() as con:
        row = con.execute("SELECT name FROM phases WHERE id = ?", (phase_id,)).fetchone()
        return row["name"] if row else ""


def show_notes(phase_id: int) -> None:
    project_id = _get_project_id(phase_id)
    phase_name = _get_phase_name(phase_id)

    # ── New note ──────────────────────────────────────────────────────────────
    with st.form(f"new_note_{phase_id}", clear_on_submit=True):
        content = st.text_area("New note", placeholder="Write your note here...", height=100)
        if st.form_submit_button("Save Note"):
            if content.strip():
                note_id = create_note(phase_id, content.strip())
                chunks  = chunk_text(content.strip())
                if chunks:
                    index_chunks(chunks, project_id, phase_id, phase_name, _note_source(note_id))
                st.rerun()

    # ── Existing notes ────────────────────────────────────────────────────────
    notes = get_notes(phase_id)
    if not notes:
        st.caption("No notes yet.")
        return

    for note in notes:
        with st.container(border=True):
            st.caption(note["created_at"][:16])

            edited = st.text_area(
                "Edit note",
                value=note["content"],
                key=f"note_text_{note['id']}",
                height=80,
                label_visibility="collapsed",
            )

            col_save, col_del, _ = st.columns([1, 1, 5])
            with col_save:
                if st.button("Save", key=f"save_note_{note['id']}"):
                    update_note(note["id"], edited)
                    delete_source(project_id, phase_id, _note_source(note["id"]))
                    chunks = chunk_text(edited)
                    if chunks:
                        index_chunks(chunks, project_id, phase_id, phase_name, _note_source(note["id"]))
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"del_note_{note['id']}"):
                    delete_source(project_id, phase_id, _note_source(note["id"]))
                    delete_note(note["id"])
                    st.rerun()
