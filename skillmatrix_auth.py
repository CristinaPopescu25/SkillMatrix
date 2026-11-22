"""Authentication and authorization for SkillMatrix."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Any

from skillmatrix_db import db_session, insert_row, log_action, query_one, utc_now

ROLES = ["Admin", "Manager", "Team Lead", "HR/Training", "Operator", "Auditor"]

# Page/action permissions
PERMISSIONS = {
    "dashboard": {"Admin", "Manager", "Team Lead", "HR/Training", "Operator", "Auditor"},
    "organization": {"Admin", "Manager"},
    "employees": {"Admin", "Manager", "Team Lead", "HR/Training"},
    "skills": {"Admin", "Manager", "Team Lead", "HR/Training"},
    "assignments": {"Admin", "Manager", "Team Lead"},
    "performance": {"Admin", "Manager", "Team Lead"},
    "import": {"Admin", "Manager"},
    "admin": {"Admin"},
    "audit": {"Admin", "Auditor", "Manager"},
    "my_profile": {"Admin", "Manager", "Team Lead", "HR/Training", "Operator", "Auditor"},
}


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return "pbkdf2_sha256$200000$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations, salt_b64, hash_b64 = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64.encode())
        expected = base64.b64decode(hash_b64.encode())
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def ensure_default_admin(db_path=None) -> None:
    with db_session(db_path) if db_path else db_session() as conn:
        existing = query_one(conn, "SELECT id FROM users WHERE username=?", ("admin",))
        if not existing:
            insert_row(
                conn,
                "users",
                {
                    "username": "admin",
                    "password_hash": hash_password("admin123"),
                    "role": "Admin",
                    "employee_id": None,
                    "active": 1,
                    "created_at": utc_now(),
                },
            )
            log_action(conn, {"id": None, "username": "system"}, "seed", "users", "admin", "Default admin created")


def authenticate(username: str, password: str, db_path=None) -> dict[str, Any] | None:
    with db_session(db_path) if db_path else db_session() as conn:
        user = query_one(conn, "SELECT * FROM users WHERE username=? AND active=1", (username.strip(),))
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        log_action(conn, user, "login", "users", user["id"], "User logged in")
        user.pop("password_hash", None)
        return user


def can_access(role: str, page: str) -> bool:
    return role in PERMISSIONS.get(page, set())