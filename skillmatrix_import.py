"""CSV/TXT/JSON import utilities for SkillMatrix."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

import pandas as pd


def _decode_bytes(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def read_uploaded_file(uploaded_file) -> tuple[str, str]:
    name = getattr(uploaded_file, "name", "upload")
    raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    if isinstance(raw, str):
        return name, raw
    return name, _decode_bytes(raw)


def parse_csv_like(text: str) -> pd.DataFrame:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        sep = dialect.delimiter
    except Exception:
        # fallback
        header = next((l for l in sample.splitlines() if l.strip()), "")
        sep = ";" if header.count(";") > header.count(",") else ","
        if "\t" in header and header.count("\t") >= max(header.count(";"), header.count(",")):
            sep = "\t"
        if "|" in header and header.count("|") >= max(header.count(";"), header.count(",")):
            sep = "|"
    df = pd.read_csv(io.StringIO(text), sep=sep)
    return df


def parse_json(text: str) -> pd.DataFrame:
    obj = json.loads(text)
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        # common wrappers
        for key in ("data", "items", "rows", "records"):
            if key in obj and isinstance(obj[key], list):
                return pd.DataFrame(obj[key])
        # dict of scalars/lists
        return pd.DataFrame([obj]) if all(not isinstance(v, (list, dict)) for v in obj.values()) else pd.DataFrame(obj)
    raise ValueError("JSON-ul trebuie să conțină o listă de obiecte sau un obiect.")


def parse_file(name: str, text: str) -> pd.DataFrame:
    lower = name.lower()
    if lower.endswith(".json"):
        df = parse_json(text)
    elif lower.endswith(".csv") or lower.endswith(".txt"):
        df = parse_csv_like(text)
    else:
        # try json then csv
        try:
            df = parse_json(text)
        except Exception:
            df = parse_csv_like(text)
    df.columns = [str(c).strip() for c in df.columns]
    return df


REQUIRED_FIELDS = {
    "departments": ["name"],
    "cells": ["department_name", "name"],
    "stations": ["department_name", "cell_name", "name"],
    "employees": ["code", "full_name"],
    "skills": ["name"],
    "employee_skills": ["employee_code", "skill_name", "level"],
    "station_requirements": ["station_name", "skill_name", "min_level"],
    "assignments": ["employee_code", "station_name", "start_date"],
    "performance_logs": ["employee_code", "station_name", "work_date", "hours_worked", "output_qty"],
    "training_plans": ["employee_code", "skill_name", "target_level"],
}


def validate_import_df(df: pd.DataFrame, entity: str) -> list[str]:
    errors = []
    required = REQUIRED_FIELDS.get(entity, [])
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        errors.append(f"Lipsesc coloanele obligatorii: {', '.join(missing_cols)}")
        return errors
    for idx, row in df.iterrows():
        for col in required:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                errors.append(f"Rând {idx + 2}: câmp obligatoriu lipsă '{col}'")
    return errors