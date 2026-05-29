"""
ui/checklist.py
---------------
Checklist tab per phase — pre-seeded items with completion tracking.
"""

import streamlit as st

from construct_iq.database import (
    create_checklist_item,
    delete_checklist_item,
    get_checklist_items,
    toggle_checklist_item,
)


def show_checklist(phase_id: int) -> None:
    items = get_checklist_items(phase_id)

    # ── Progress ──────────────────────────────────────────────────────────────
    if items:
        done  = sum(1 for i in items if i["completed"])
        total = len(items)
        pct   = done / total
        st.progress(pct, text=f"{done} / {total} items complete")
        st.write("")

    # ── Items grouped by category ─────────────────────────────────────────────
    categories: list[str] = []
    for item in items:
        cat = item["category"] or ""
        if cat not in categories:
            categories.append(cat)

    for cat in categories:
        cat_items = [i for i in items if (i["category"] or "") == cat]

        if cat:
            st.markdown(
                f'<p style="margin:0.75rem 0 0.35rem;font-size:0.7rem;font-weight:700;'
                f'color:#79716b;letter-spacing:0.1em;text-transform:uppercase;'
                f'font-family:\'Inter\',sans-serif">{cat}</p>',
                unsafe_allow_html=True,
            )

        for item in cat_items:
            col_check, col_del = st.columns([10, 1])
            with col_check:
                checked = st.checkbox(
                    item["text"],
                    value=bool(item["completed"]),
                    key=f"chk_{item['id']}",
                )
                if checked != bool(item["completed"]):
                    toggle_checklist_item(item["id"], checked)
                    st.rerun()
            with col_del:
                if st.button("✕", key=f"del_chk_{item['id']}", help="Remove item"):
                    delete_checklist_item(item["id"])
                    st.rerun()

    if not items:
        st.caption("No checklist items yet.")

    # ── Add custom item ───────────────────────────────────────────────────────
    st.write("")
    with st.expander("+ Add item"):
        with st.form(f"add_chk_{phase_id}", clear_on_submit=True):
            text = st.text_input("Item", placeholder="Describe the task...")
            if st.form_submit_button("Add", use_container_width=True, type="primary"):
                if text.strip():
                    create_checklist_item(phase_id, text.strip())
                    st.rerun()
