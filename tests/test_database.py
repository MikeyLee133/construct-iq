import pytest
from datetime import date
from pathlib import Path

from construct_iq.database import (
    init_db,
    create_project,
    get_all_projects,
    get_project,
    update_project,
    delete_project,
    create_phases_for_project,
    get_phases,
    update_phase_status,
    create_note,
    get_notes,
    update_note,
    delete_note,
    create_expense,
    get_expenses,
    delete_expense,
)
from construct_iq.config import DEFAULT_PHASES


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Use a fresh temp DB for every test."""
    import construct_iq.database as db_module
    import construct_iq.config as config_module

    test_db = tmp_path / "test.db"
    monkeypatch.setattr(config_module, "DB_PATH", test_db)
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    init_db()


# ── Projects ──────────────────────────────────────────────────────────────────

def test_create_and_get_project():
    pid = create_project("Test House", "123 Main St", "Active", date(2025, 1, 1))
    project = get_project(pid)
    assert project["name"] == "Test House"
    assert project["address"] == "123 Main St"
    assert project["status"] == "Active"


def test_get_all_projects_returns_all():
    create_project("House A", "", "Active", None)
    create_project("House B", "", "Active", None)
    assert len(get_all_projects()) == 2


def test_update_project():
    pid = create_project("Old Name", "", "Active", None)
    update_project(pid, "New Name", "New Address", "Completed", date(2025, 6, 1))
    project = get_project(pid)
    assert project["name"] == "New Name"
    assert project["status"] == "Completed"


def test_delete_project():
    pid = create_project("To Delete", "", "Active", None)
    delete_project(pid)
    assert get_project(pid) is None


def test_get_project_returns_none_for_missing():
    assert get_project(9999) is None


# ── Phases ────────────────────────────────────────────────────────────────────

def test_create_phases_for_project():
    pid = create_project("House", "", "Active", None)
    create_phases_for_project(pid, DEFAULT_PHASES)
    phases = get_phases(pid)
    assert len(phases) == len(DEFAULT_PHASES)
    assert phases[0]["name"] == DEFAULT_PHASES[0]


def test_phases_ordered_correctly():
    pid = create_project("House", "", "Active", None)
    create_phases_for_project(pid, DEFAULT_PHASES)
    phases = get_phases(pid)
    for i, phase in enumerate(phases):
        assert phase["phase_order"] == i


def test_update_phase_status():
    pid = create_project("House", "", "Active", None)
    create_phases_for_project(pid, ["Foundation"])
    phase = get_phases(pid)[0]
    update_phase_status(phase["id"], "Complete")
    updated = get_phases(pid)[0]
    assert updated["status"] == "Complete"


def test_deleting_project_cascades_to_phases():
    pid = create_project("House", "", "Active", None)
    create_phases_for_project(pid, DEFAULT_PHASES)
    delete_project(pid)
    assert get_phases(pid) == []


# ── Notes ─────────────────────────────────────────────────────────────────────

def _setup_phase():
    pid = create_project("House", "", "Active", None)
    create_phases_for_project(pid, ["Foundation"])
    return get_phases(pid)[0]["id"]


def test_create_and_get_note():
    phase_id = _setup_phase()
    create_note(phase_id, "Site looks good")
    notes = get_notes(phase_id)
    assert len(notes) == 1
    assert notes[0]["content"] == "Site looks good"


def test_update_note():
    phase_id = _setup_phase()
    nid = create_note(phase_id, "Original")
    update_note(nid, "Updated")
    assert get_notes(phase_id)[0]["content"] == "Updated"


def test_delete_note():
    phase_id = _setup_phase()
    nid = create_note(phase_id, "To delete")
    delete_note(nid)
    assert get_notes(phase_id) == []


# ── Expenses ──────────────────────────────────────────────────────────────────

def test_create_and_get_expense():
    phase_id = _setup_phase()
    create_expense(phase_id, 1500.0, "Labour", date(2025, 3, 1), "Foundation crew")
    expenses = get_expenses(phase_id)
    assert len(expenses) == 1
    assert expenses[0]["amount"] == 1500.0
    assert expenses[0]["category"] == "Labour"


def test_delete_expense():
    phase_id = _setup_phase()
    eid = create_expense(phase_id, 500.0, "Materials", date(2025, 3, 1), "Concrete")
    delete_expense(eid)
    assert get_expenses(phase_id) == []


def test_expense_total():
    phase_id = _setup_phase()
    create_expense(phase_id, 1000.0, "Labour",    date(2025, 3, 1), "Crew A")
    create_expense(phase_id, 500.0,  "Materials", date(2025, 3, 2), "Lumber")
    total = sum(e["amount"] for e in get_expenses(phase_id))
    assert total == 1500.0
