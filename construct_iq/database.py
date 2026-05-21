"""
database.py
-----------
All SQLite operations. Single source of truth for schema and queries.
No business logic lives here — just data access.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from construct_iq.config import DB_PATH


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


# ── Schema ────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                address     TEXT    NOT NULL DEFAULT '',
                status      TEXT    NOT NULL DEFAULT 'Active',
                start_date  TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS phases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name        TEXT    NOT NULL,
                phase_order INTEGER NOT NULL DEFAULT 0,
                status      TEXT    NOT NULL DEFAULT 'Not Started'
            );

            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id    INTEGER NOT NULL REFERENCES phases(id) ON DELETE CASCADE,
                content     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id     INTEGER NOT NULL REFERENCES phases(id) ON DELETE CASCADE,
                amount       REAL    NOT NULL,
                category     TEXT    NOT NULL,
                expense_date TEXT    NOT NULL,
                description  TEXT    NOT NULL DEFAULT '',
                receipt_path TEXT
            );

            CREATE TABLE IF NOT EXISTS documents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id    INTEGER NOT NULL REFERENCES phases(id) ON DELETE CASCADE,
                filename    TEXT    NOT NULL,
                file_path   TEXT    NOT NULL,
                file_type   TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)


# ── Projects ──────────────────────────────────────────────────────────────────

def create_project(name: str, address: str, status: str, start_date: date | None) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO projects (name, address, status, start_date) VALUES (?,?,?,?)",
            (name, address, status, start_date.isoformat() if start_date else None),
        )
        return cur.lastrowid  # type: ignore[return-value]


def get_all_projects() -> list[dict]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_project(project_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None


def update_project(project_id: int, name: str, address: str, status: str, start_date: date | None) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE projects SET name=?, address=?, status=?, start_date=? WHERE id=?",
            (name, address, status, start_date.isoformat() if start_date else None, project_id),
        )


def delete_project(project_id: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM projects WHERE id = ?", (project_id,))


# ── Phases ────────────────────────────────────────────────────────────────────

def create_phases_for_project(project_id: int, phase_names: list[str]) -> None:
    with _conn() as con:
        con.executemany(
            "INSERT INTO phases (project_id, name, phase_order) VALUES (?,?,?)",
            [(project_id, name, i) for i, name in enumerate(phase_names)],
        )


def get_phases(project_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM phases WHERE project_id = ? ORDER BY phase_order",
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def update_phase_status(phase_id: int, status: str) -> None:
    with _conn() as con:
        con.execute("UPDATE phases SET status=? WHERE id=?", (status, phase_id))


# ── Notes ─────────────────────────────────────────────────────────────────────

def create_note(phase_id: int, content: str) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO notes (phase_id, content) VALUES (?,?)",
            (phase_id, content),
        )
        return cur.lastrowid  # type: ignore[return-value]


def get_notes(phase_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM notes WHERE phase_id = ? ORDER BY created_at DESC",
            (phase_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def update_note(note_id: int, content: str) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE notes SET content=?, updated_at=? WHERE id=?",
            (content, datetime.now().isoformat(), note_id),
        )


def delete_note(note_id: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM notes WHERE id = ?", (note_id,))


# ── Expenses ──────────────────────────────────────────────────────────────────

def create_expense(
    phase_id: int,
    amount: float,
    category: str,
    expense_date: date,
    description: str,
    receipt_path: str | None = None,
) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO expenses (phase_id, amount, category, expense_date, description, receipt_path) VALUES (?,?,?,?,?,?)",
            (phase_id, amount, category, expense_date.isoformat(), description, receipt_path),
        )
        return cur.lastrowid  # type: ignore[return-value]


def get_expenses(phase_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM expenses WHERE phase_id = ? ORDER BY expense_date DESC",
            (phase_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_project_expenses(project_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT e.*, p.name as phase_name
               FROM expenses e
               JOIN phases p ON e.phase_id = p.id
               WHERE p.project_id = ?
               ORDER BY e.expense_date DESC""",
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_expense(expense_id: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


# ── Documents ─────────────────────────────────────────────────────────────────

def create_document(phase_id: int, filename: str, file_path: str, file_type: str) -> int:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO documents (phase_id, filename, file_path, file_type) VALUES (?,?,?,?)",
            (phase_id, filename, file_path, file_type),
        )
        return cur.lastrowid  # type: ignore[return-value]


def get_documents(phase_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM documents WHERE phase_id = ? ORDER BY created_at DESC",
            (phase_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_project_documents(project_id: int) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT d.*, p.name as phase_name
               FROM documents d
               JOIN phases p ON d.phase_id = p.id
               WHERE p.project_id = ?""",
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_document(doc_id: int) -> None:
    with _conn() as con:
        row = con.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if row:
            Path(row["file_path"]).unlink(missing_ok=True)
        con.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
