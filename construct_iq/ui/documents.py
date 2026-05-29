"""
ui/documents.py
---------------
Document upload and listing per phase.
"""

import pandas as pd
import streamlit as st

from construct_iq.config import SUPPORTED_FILE_TYPES
from construct_iq.database import create_document, delete_document, get_documents
from construct_iq.embedder import delete_source, index_chunks
from construct_iq.storage import chunk_text, extract_text, save_file


def show_documents(phase_id: int, phase_name: str) -> None:
    # ── Upload ────────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload a document or image",
        type=SUPPORTED_FILE_TYPES,
        key=f"upload_{phase_id}",
    )

    if uploaded:
        file_bytes = uploaded.read()
        file_path, file_type = save_file(phase_id, uploaded.name, file_bytes)
        create_document(phase_id, uploaded.name, file_path, file_type)

        with st.spinner(f"Processing {uploaded.name}..."):
            text   = extract_text(file_path, file_type)
            chunks = chunk_text(text)

            # Get project_id from the phase
            from construct_iq.database import _conn
            with _conn() as con:
                row = con.execute("SELECT project_id FROM phases WHERE id = ?", (phase_id,)).fetchone()
                project_id = row["project_id"] if row else 0

            if chunks:
                index_chunks(chunks, project_id, phase_id, phase_name, uploaded.name)
                st.success(f"Uploaded and indexed {uploaded.name} ({len(chunks)} chunks)")
            else:
                st.warning(f"Uploaded {uploaded.name} but could not extract text for AI search.")

        st.rerun()

    # ── Document list ─────────────────────────────────────────────────────────
    docs = get_documents(phase_id)
    if not docs:
        st.caption("No documents uploaded yet.")
        return

    df = pd.DataFrame([{
        "File": doc["filename"],
        "Type": doc["file_type"].upper(),
    } for doc in docs])
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("🗑 Remove a document"):
        for doc in docs:
            col_name, col_del = st.columns([6, 1])
            with col_name:
                st.caption(f"📄 {doc['filename']}  ({doc['file_type'].upper()})")
            with col_del:
                if st.button("Remove", key=f"del_doc_{doc['id']}"):
                    from construct_iq.database import _conn
                    with _conn() as con:
                        row = con.execute("SELECT project_id FROM phases WHERE id = ?", (phase_id,)).fetchone()
                        project_id = row["project_id"] if row else 0
                    delete_source(project_id, phase_id, doc["filename"])
                    delete_document(doc["id"])
                    st.rerun()
