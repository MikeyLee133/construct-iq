"""
ui/qa.py
--------
AI Q&A interface — ask questions across all project documents.
"""

import streamlit as st

from construct_iq.database import get_project
from construct_iq.embedder import query
from construct_iq.llm import answer


def show_qa(project_id: int) -> None:
    project = get_project(project_id)
    if not project:
        st.error("Project not found.")
        return

    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Back"):
            st.session_state["view"] = "project"
            st.rerun()
    with col_title:
        st.title(f"🤖 Ask AI — {project['name']}")
        st.caption("Ask any question about your project documents, notes, and reports.")

    # ── Chat history ──────────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.caption(f"📄 {s['phase_name']} — {s['source']}")

    # ── Input ─────────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a question about this project...")

    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                chunks   = query(user_input, project_id)
                response = answer(user_input, chunks)

            st.write(response)

            if chunks:
                with st.expander("Sources"):
                    for chunk in chunks:
                        st.caption(f"📄 {chunk['phase_name']} — {chunk['source']}")

        st.session_state["chat_history"].append({
            "role":    "assistant",
            "content": response,
            "sources": chunks,
        })

    # ── Clear chat ────────────────────────────────────────────────────────────
    if st.session_state["chat_history"]:
        if st.button("Clear conversation"):
            st.session_state["chat_history"] = []
            st.rerun()
