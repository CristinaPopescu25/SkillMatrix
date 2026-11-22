import json
import os
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from skillmatrix_auth import authenticate, ensure_default_admin, hash_password, verify_password
from skillmatrix_db import (
    check_assignment_eligibility,
    db_session,
    employee_polyvalence,
    init_db,
    insert_row,
    performance_kpis,
    query_one,
)
from skillmatrix_import import parse_file, validate_import_df


class SkillMatrixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        init_db(self.db_path)
        ensure_default_admin(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_admin_auth(self):
        user = authenticate("admin", "admin123", self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "Admin")
        self.assertIsNone(authenticate("admin", "wrong", self.db_path))

    def test_password_hash_verify(self):
        h = hash_password("secret")
        self.assertTrue(verify_password("secret", h))
        self.assertFalse(verify_password("other", h))

    def test_assignment_eligibility(self):
        with db_session(self.db_path) as conn:
            dep = insert_row(conn, "departments", {"name": "Dep", "description": "", "active": 1})
            cell = insert_row(conn, "cells", {"department_id": dep, "name": "Cell", "description": "", "active": 1})
            st = insert_row(conn, "stations", {"cell_id": cell, "name": "Station", "description": "", "active": 1})
            emp = insert_row(conn, "employees", {"code": "E1", "full_name": "Test", "email": "", "role_title": "", "department_id": dep, "cell_id": cell, "hire_date": "", "status": "activ"})
            skill = insert_row(conn, "skills", {"name": "Soldering", "category": "Prod", "description": "", "active": 1})
            insert_row(conn, "station_requirements", {"station_id": st, "skill_id": skill, "min_level": 3, "mandatory": 1})
            elig = check_assignment_eligibility(conn, emp, st)
            self.assertFalse(elig["eligible"])
            insert_row(conn, "employee_skills", {"employee_id": emp, "skill_id": skill, "level": 3, "target_level": 4, "evaluated_at": "", "expires_at": "", "evaluator": "", "notes": ""})
            elig2 = check_assignment_eligibility(conn, emp, st)
            self.assertTrue(elig2["eligible"])

    def test_polyvalence_and_kpis(self):
        with db_session(self.db_path) as conn:
            dep = insert_row(conn, "departments", {"name": "D", "description": "", "active": 1})
            emp = insert_row(conn, "employees", {"code": "E2", "full_name": "Poly", "email": "", "role_title": "", "department_id": dep, "cell_id": None, "hire_date": "", "status": "activ"})
            s1 = insert_row(conn, "skills", {"name": "A", "category": "", "description": "", "active": 1})
            s2 = insert_row(conn, "skills", {"name": "B", "category": "", "description": "", "active": 1})
            insert_row(conn, "employee_skills", {"employee_id": emp, "skill_id": s1, "level": 2, "target_level": 4, "evaluated_at": "", "expires_at": "", "evaluator": "", "notes": ""})
            insert_row(conn, "employee_skills", {"employee_id": emp, "skill_id": s2, "level": 1, "target_level": 3, "evaluated_at": "", "expires_at": "", "evaluator": "", "notes": ""})
            poly = employee_polyvalence(conn, emp)
            self.assertEqual(poly["total_skills"], 2)
            self.assertEqual(poly["qualified_skills"], 1)
            self.assertAlmostEqual(poly["percent"], 50.0)
        kpis = performance_kpis([{"hours_worked": 8, "output_qty": 100, "scrap_qty": 5}, {"hours_worked": 8, "output_qty": 80, "scrap_qty": 0}])
        self.assertAlmostEqual(kpis["hours"], 16)
        self.assertAlmostEqual(kpis["output"], 180)
        self.assertAlmostEqual(kpis["scrap"], 5)
        self.assertAlmostEqual(kpis["productivity"], 11.25)
        self.assertAlmostEqual(kpis["quality_pct"], (175 / 180) * 100)

    def test_import_parsing_and_validation(self):
        csv_text = "code,full_name,status\nE1,John,activ\n,Missing,\n"
        df = parse_file("employees.csv", csv_text)
        errors = validate_import_df(df, "employees")
        self.assertTrue(any("Rând 3" in e for e in errors))

        json_text = json.dumps([{"name": "Dep1"}, {"name": "Dep2"}])
        dfj = parse_file("deps.json", json_text)
        self.assertEqual(len(dfj), 2)
        self.assertEqual(validate_import_df(dfj, "departments"), [])

        txt_text = "name\tdescription\nSkillA\tDesc\n"
        dft = parse_file("skills.txt", txt_text)
        self.assertEqual(list(dft.columns), ["name", "description"])
        self.assertEqual(len(dft), 1)


if __name__ == "__main__":
    unittest.main()
