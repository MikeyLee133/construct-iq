"""
ui/expenses.py
--------------
Expense logging and listing per phase.
"""

from datetime import date

import pandas as pd
import streamlit as st

from construct_iq.config import EXPENSE_CATEGORIES, SUPPORTED_FILE_TYPES
from construct_iq.database import create_expense, delete_expense, get_expenses
from construct_iq.storage import save_file


def show_expenses(phase_id: int) -> None:
    expenses = get_expenses(phase_id)
    total    = sum(e["amount"] for e in expenses)

    if expenses:
        st.metric("Phase Total", f"${total:,.2f}")

    # ── Add expense form ──────────────────────────────────────────────────────
    with st.expander("+ Add Expense", expanded=not expenses):
        with st.form(f"add_expense_{phase_id}", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                amount      = st.number_input("Amount ($) *", min_value=0.01, step=0.01, format="%.2f")
                category    = st.selectbox("Category", EXPENSE_CATEGORIES)
            with col2:
                expense_date = st.date_input("Date", value=date.today())
                description  = st.text_input("Description", placeholder="What was this for?")

            receipt = st.file_uploader(
                "Attach receipt (optional)",
                type=SUPPORTED_FILE_TYPES,
                key=f"receipt_{phase_id}",
            )

            if st.form_submit_button("Add Expense", use_container_width=True):
                receipt_path = None
                if receipt:
                    receipt_path, _ = save_file(phase_id, f"receipt_{receipt.name}", receipt.read())
                create_expense(phase_id, amount, category, expense_date, description, receipt_path)
                st.rerun()

    # ── Expense list ──────────────────────────────────────────────────────────
    if not expenses:
        st.caption("No expenses logged yet.")
        return

    df = pd.DataFrame([{
        "Date":        e["expense_date"],
        "Category":    e["category"],
        "Description": e["description"] or "—",
        "Amount":      e["amount"],
    } for e in expenses])
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn("Amount", format="$%.2f")},
    )

    with st.expander("🗑 Remove an expense"):
        for exp in expenses:
            col_info, col_del = st.columns([6, 1])
            with col_info:
                st.caption(f"{exp['expense_date']}  ·  {exp['category']}  ·  ${exp['amount']:,.2f}  —  {exp['description'] or ''}")
            with col_del:
                if st.button("Remove", key=f"del_exp_{exp['id']}"):
                    delete_expense(exp["id"])
                    st.rerun()
