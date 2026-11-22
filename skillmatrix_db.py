"""SQLite persistence layer for SkillMatrix."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).with_name("skillmatrix.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    employee_id INTEGER,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1,
    UNIQUE(department_id, name),
    FOREIGN KEY(department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cell_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1,
    UNIQUE(cell_id, name),
    FOREIGN KEY(cell_id) REFERENCES cells(id)
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT DEFAULT '',
    role_title TEXT DEFAULT '',
    department_id INTEGER,
    cell_id INTEGER,
    hire_date TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'activ',
    FOREIGN KEY(department_id) REFERENCES departments(id),
    FOREIGN KEY(cell_id) REFERENCES cells(id)
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT DEFAULT '',
    description TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS employee_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    level INTEGER NOT NULL CHECK(level BETWEEN 0 AND 4),
    target_level INTEGER NOT NULL DEFAULT 4 CHECK(target_level BETWEEN 0 AND 4),
    evaluated_at TEXT DEFAULT '',
    expires_at TEXT DEFAULT '',
    evaluator TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    UNIQUE(employee_id, skill_id),
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(skill_id) REFERENCES skills(id)
);

CREATE TABLE IF NOT EXISTS station_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    min_level INTEGER NOT NULL CHECK(min_level BETWEEN 0 AND 4),
    mandatory INTEGER NOT NULL DEFAULT 1,
    UNIQUE(station_id, skill_id),
    FOREIGN KEY(station_id) REFERENCES stations(id),
    FOREIGN KEY(skill_id) REFERENCES skills(id)
);

CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT DEFAULT '',
    assigned_by TEXT DEFAULT '',
    override_reason TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'activ',
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS performance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    work_date TEXT NOT NULL,
    hours_worked REAL NOT NULL CHECK(hours_worked >= 0),
    output_qty REAL NOT NULL CHECK(output_qty >= 0),
    scrap_qty REAL NOT NULL DEFAULT 0 CHECK(scrap_qty >= 0),
    notes TEXT DEFAULT '',
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS training_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    current_level INTEGER NOT NULL DEFAULT 0,
    target_level INTEGER NOT NULL DEFAULT 2,
    due_date TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planificat',
    notes TEXT DEFAULT '',
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(skill_id) REFERENCES skills(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT DEFAULT '',
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id TEXT DEFAULT '',
    details TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session(db_path: Path | str = DB_PATH):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path | str = DB_PATH) -> None:
    with db_session(db_path) as conn:
        conn.executescript(SCHEMA)


def query_all(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def query_one(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> dict[str, Any] | None:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def log_action(conn: sqlite3.Connection, user: dict[str, Any] | None, action: str, entity: str, entity_id: Any = "", details: str = "") -> None:
    conn.execute(
        "INSERT INTO audit_log(user_id, username, action, entity, entity_id, details, created_at) VALUES (?,?,?,?,?,?,?)",
        (
            (user or {}).get("id"),
            (user or {}).get("username", "system"),
            action,
            entity,
            str(entity_id),
            details,
            utc_now(),
        ),
    )


# Generic helpers

def insert_row(conn: sqlite3.Connection, table: str, data: dict[str, Any]) -> int:
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    sql = f"INSERT INTO {table}({', '.join(cols)}) VALUES ({placeholders})"
    cur = conn.execute(sql, tuple(data[c] for c in cols))
    return int(cur.lastrowid)


def update_row(conn: sqlite3.Connection, table: str, row_id: int, data: dict[str, Any]) -> None:
    cols = list(data.keys())
    sets = ", ".join([f"{c}=?" for c in cols])
    sql = f"UPDATE {table} SET {sets} WHERE id=?"
    conn.execute(sql, tuple(data[c] for c in cols) + (row_id,))


def delete_row(conn: sqlite3.Connection, table: str, row_id: int) -> None:
    conn.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))


# Domain queries

def list_departments(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(conn, "SELECT * FROM departments ORDER BY name")


def list_cells(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT c.*, d.name AS department_name
           FROM cells c JOIN departments d ON d.id=c.department_id
           ORDER BY d.name, c.name""",
    )


def list_stations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT s.*, c.name AS cell_name, d.name AS department_name, d.id AS department_id
           FROM stations s
           JOIN cells c ON c.id=s.cell_id
           JOIN departments d ON d.id=c.department_id
           ORDER BY d.name, c.name, s.name""",
    )


def list_employees(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT e.*, d.name AS department_name, c.name AS cell_name
           FROM employees e
           LEFT JOIN departments d ON d.id=e.department_id
           LEFT JOIN cells c ON c.id=e.cell_id
           ORDER BY e.full_name""",
    )


def list_skills(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(conn, "SELECT * FROM skills ORDER BY category, name")


def list_employee_skills(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT es.*, e.full_name AS employee_name, e.code AS employee_code, s.name AS skill_name, s.category AS skill_category
           FROM employee_skills es
           JOIN employees e ON e.id=es.employee_id
           JOIN skills s ON s.id=es.skill_id
           ORDER BY e.full_name, s.name""",
    )


def list_station_requirements(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT sr.*, s.name AS station_name, sk.name AS skill_name,
                  c.name AS cell_name, d.name AS department_name
           FROM station_requirements sr
           JOIN stations s ON s.id=sr.station_id
           JOIN skills sk ON sk.id=sr.skill_id
           JOIN cells c ON c.id=s.cell_id
           JOIN departments d ON d.id=c.department_id
           ORDER BY d.name, c.name, s.name, sk.name""",
    )


def list_assignments(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT a.*, e.full_name AS employee_name, e.code AS employee_code,
                  s.name AS station_name, c.name AS cell_name, d.name AS department_name
           FROM assignments a
           JOIN employees e ON e.id=a.employee_id
           JOIN stations s ON s.id=a.station_id
           JOIN cells c ON c.id=s.cell_id
           JOIN departments d ON d.id=c.department_id
           ORDER BY a.start_date DESC, e.full_name""",
    )


def list_performance_logs(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT p.*, e.full_name AS employee_name, e.code AS employee_code,
                  s.name AS station_name, c.name AS cell_name, d.name AS department_name
           FROM performance_logs p
           JOIN employees e ON e.id=p.employee_id
           JOIN stations s ON s.id=p.station_id
           JOIN cells c ON c.id=s.cell_id
           JOIN departments d ON d.id=c.department_id
           ORDER BY p.work_date DESC""",
    )


def list_training_plans(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return query_all(
        conn,
        """SELECT t.*, e.full_name AS employee_name, s.name AS skill_name
           FROM training_plans t
           JOIN employees e ON e.id=t.employee_id
           JOIN skills s ON s.id=t.skill_id
           ORDER BY t.due_date, e.full_name""",
    )


def list_audit_log(conn: sqlite3.Connection, limit: int = 200) -> list[dict[str, Any]]:
    return query_all(conn, "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,))


# Business logic

def check_assignment_eligibility(conn: sqlite3.Connection, employee_id: int, station_id: int) -> dict[str, Any]:
    reqs = query_all(
        conn,
        """SELECT sr.*, sk.name AS skill_name
           FROM station_requirements sr JOIN skills sk ON sk.id=sr.skill_id
           WHERE sr.station_id=?""",
        (station_id,),
    )
    gaps = []
    for req in reqs:
        row = query_one(
            conn,
            "SELECT level FROM employee_skills WHERE employee_id=? AND skill_id=?",
            (employee_id, req["skill_id"]),
        )
        current = int(row["level"]) if row else 0
        if current < int(req["min_level"]):
            gaps.append(
                {
                    "skill": req["skill_name"],
                    "required": int(req["min_level"]),
                    "current": current,
                    "mandatory": bool(req["mandatory"]),
                }
            )
    mandatory_gaps = [g for g in gaps if g["mandatory"]]
    return {"eligible": len(mandatory_gaps) == 0, "gaps": gaps, "mandatory_gaps": mandatory_gaps}


def employee_polyvalence(conn: sqlite3.Connection, employee_id: int) -> dict[str, Any]:
    skills = query_all(conn, "SELECT level FROM employee_skills WHERE employee_id=?", (employee_id,))
    total = len(skills)
    qualified = sum(1 for s in skills if int(s["level"]) >= 2)
    pct = (qualified / total * 100) if total else 0.0
    return {"total_skills": total, "qualified_skills": qualified, "percent": pct}


def performance_kpis(logs: list[dict[str, Any]]) -> dict[str, float]:
    hours = sum(float(r.get("hours_worked", 0) or 0) for r in logs)
    output = sum(float(r.get("output_qty", 0) or 0) for r in logs)
    scrap = sum(float(r.get("scrap_qty", 0) or 0) for r in logs)
    productivity = output / hours if hours else 0.0
    quality = ((output - scrap) / output * 100) if output else 0.0
    return {
        "hours": hours,
        "output": output,
        "scrap": scrap,
        "productivity": productivity,
        "quality_pct": quality,
    }