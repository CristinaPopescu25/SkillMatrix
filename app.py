"""SkillMatrix – Employee Qualification & Performance Management System."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from skillmatrix_auth import ROLES, authenticate, can_access, ensure_default_admin, hash_password
from skillmatrix_db import (
    DB_PATH,
    check_assignment_eligibility,
    db_session,
    delete_row,
    employee_polyvalence,
    init_db,
    insert_row,
    list_assignments,
    list_audit_log,
    list_cells,
    list_departments,
    list_employee_skills,
    list_employees,
    list_performance_logs,
    list_skills,
    list_station_requirements,
    list_stations,
    list_training_plans,
    log_action,
    performance_kpis,
    query_all,
    query_one,
    update_row,
)
from skillmatrix_import import REQUIRED_FIELDS, parse_file, read_uploaded_file, validate_import_df

st.set_page_config(page_title="SkillMatrix", page_icon="📊", layout="wide")

LEVEL_LABELS = {0: "0 - Neinstruit", 1: "1 - În instruire", 2: "2 - Autonom", 3: "3 - Avansat", 4: "4 - Expert/Trainer"}


def init_app() -> None:
    init_db(DB_PATH)
    ensure_default_admin(DB_PATH)


def current_user():
    return st.session_state.get("user")


def require_login():
    user = current_user()
    if not user:
        render_login()
        st.stop()
    return user


def render_login():
    st.title("SkillMatrix")
    st.caption("Employee Qualification & Performance Management System")
    with st.form("login_form"):
        username = st.text_input("Utilizator")
        password = st.text_input("Parolă", type="password")
        submitted = st.form_submit_button("Autentificare")
    if submitted:
        user = authenticate(username, password, DB_PATH)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Utilizator sau parolă invalidă, ori cont dezactivat.")
    st.info("Cont implicit MVP: `admin` / `admin123` (schimbă parola în producție).")


def sidebar(user):
    st.sidebar.title("SkillMatrix")
    st.sidebar.write(f"Autentificat: **{user['username']}** ({user['role']})")
    pages = [
        ("dashboard", "Dashboard"),
        ("organization", "Organizație"),
        ("employees", "Angajați"),
        ("skills", "Skill Matrix & Training"),
        ("assignments", "Alocări"),
        ("performance", "Performanță"),
        ("import", "Import/Export"),
        ("admin", "Administrare"),
        ("audit", "Audit Log"),
        ("my_profile", "Profilul meu"),
    ]
    allowed = [(k, label) for k, label in pages if can_access(user["role"], k)]
    labels = [label for _, label in allowed]
    keys = [k for k, _ in allowed]
    choice = st.sidebar.radio("Navigare", labels, index=0)
    if st.sidebar.button("Logout"):
        st.session_state.pop("user", None)
        st.rerun()
    return keys[labels.index(choice)]


def df_or_info(rows, msg="Nu există date."):
    if not rows:
        st.info(msg)
        return None
    df = pd.DataFrame(rows)
    return df


# --- Organization ---
def page_organization(user):
    st.header("Configurare organizație")
    tab1, tab2, tab3 = st.tabs(["Departamente", "Celule", "Stații"])
    with db_session(DB_PATH) as conn:
        with tab1:
            with st.form("add_dept"):
                name = st.text_input("Nume departament")
                desc = st.text_input("Descriere")
                if st.form_submit_button("Adaugă departament") and name.strip():
                    insert_row(conn, "departments", {"name": name.strip(), "description": desc.strip(), "active": 1})
                    log_action(conn, user, "create", "departments", name.strip(), "Departament creat")
                    st.success("Departament adăugat.")
                    st.rerun()
            df = df_or_info(list_departments(conn))
            if df is not None:
                st.dataframe(df, use_container_width=True)
        with tab2:
            depts = list_departments(conn)
            if not depts:
                st.warning("Creează mai întâi un departament.")
            else:
                dept_map = {d["name"]: d["id"] for d in depts}
                with st.form("add_cell"):
                    dept_name = st.selectbox("Departament", list(dept_map.keys()))
                    name = st.text_input("Nume celulă")
                    desc = st.text_input("Descriere celulă")
                    if st.form_submit_button("Adaugă celulă") and name.strip():
                        insert_row(conn, "cells", {"department_id": dept_map[dept_name], "name": name.strip(), "description": desc.strip(), "active": 1})
                        log_action(conn, user, "create", "cells", name.strip(), f"În {dept_name}")
                        st.success("Celulă adăugată.")
                        st.rerun()
            df = df_or_info(list_cells(conn))
            if df is not None:
                st.dataframe(df, use_container_width=True)
        with tab3:
            cells = list_cells(conn)
            if not cells:
                st.warning("Creează mai întâi o celulă.")
            else:
                cell_map = {f"{c['department_name']} / {c['name']}": c["id"] for c in cells}
                with st.form("add_station"):
                    cell_label = st.selectbox("Celulă", list(cell_map.keys()))
                    name = st.text_input("Nume stație")
                    desc = st.text_input("Descriere stație")
                    if st.form_submit_button("Adaugă stație") and name.strip():
                        insert_row(conn, "stations", {"cell_id": cell_map[cell_label], "name": name.strip(), "description": desc.strip(), "active": 1})
                        log_action(conn, user, "create", "stations", name.strip(), f"În {cell_label}")
                        st.success("Stație adăugată.")
                        st.rerun()
            df = df_or_info(list_stations(conn))
            if df is not None:
                st.dataframe(df, use_container_width=True)


# --- Employees ---
def page_employees(user):
    st.header("Profiluri angajați")
    with db_session(DB_PATH) as conn:
        depts = list_departments(conn)
        cells = list_cells(conn)
        dept_map = {"-": None, **{d["name"]: d["id"] for d in depts}}
        cell_map = {"-": None, **{f"{c['department_name']} / {c['name']}": c["id"] for c in cells}}
        with st.expander("Adaugă angajat", expanded=False):
            with st.form("add_emp"):
                c1, c2, c3 = st.columns(3)
                code = c1.text_input("Cod angajat*")
                full_name = c2.text_input("Nume complet*")
                email = c3.text_input("Email")
                role_title = c1.text_input("Funcție")
                dept = c2.selectbox("Departament", list(dept_map.keys()))
                cell = c3.selectbox("Celulă", list(cell_map.keys()))
                hire_date = c1.date_input("Data angajării", value=date.today())
                status = c2.selectbox("Status", ["activ", "inactiv", "instruire", "concediu"])
                if st.form_submit_button("Salvează angajat"):
                    if not code.strip() or not full_name.strip():
                        st.error("Codul și numele sunt obligatorii.")
                    else:
                        try:
                            emp_id = insert_row(conn, "employees", {
                                "code": code.strip(), "full_name": full_name.strip(), "email": email.strip(),
                                "role_title": role_title.strip(), "department_id": dept_map[dept], "cell_id": cell_map[cell],
                                "hire_date": hire_date.isoformat(), "status": status,
                            })
                            log_action(conn, user, "create", "employees", emp_id, full_name.strip())
                            st.success("Angajat adăugat.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eroare: {e}")
        rows = list_employees(conn)
        df = df_or_info(rows)
        if df is not None:
            f1, f2 = st.columns(2)
            status_filter = f1.multiselect("Filtru status", sorted(df["status"].unique().tolist()), default=sorted(df["status"].unique().tolist()))
            dept_filter = f2.multiselect("Filtru departament", sorted([x for x in df["department_name"].dropna().unique().tolist()]), default=sorted([x for x in df["department_name"].dropna().unique().tolist()]))
            view = df[df["status"].isin(status_filter)]
            if dept_filter:
                view = view[view["department_name"].isin(dept_filter) | view["department_name"].isna()]
            st.dataframe(view, use_container_width=True)

            st.subheader("Profil detaliat")
            emp_map = {f"{r['code']} - {r['full_name']}": r["id"] for r in rows}
            sel = st.selectbox("Selectează angajat", list(emp_map.keys()))
            if sel:
                emp_id = emp_map[sel]
                poly = employee_polyvalence(conn, emp_id)
                k1, k2, k3 = st.columns(3)
                k1.metric("Skill-uri totale", poly["total_skills"])
                k2.metric("Skill-uri >= nivel 2", poly["qualified_skills"])
                k3.metric("Polivalență", f"{poly['percent']:.0f}%")
                sk_rows = query_all(conn, """SELECT es.*, s.name AS skill_name FROM employee_skills es JOIN skills s ON s.id=es.skill_id WHERE es.employee_id=?""", (emp_id,))
                st.write("**Skill-uri**")
                st.dataframe(pd.DataFrame(sk_rows) if sk_rows else pd.DataFrame(), use_container_width=True)
                as_rows = query_all(conn, """SELECT a.*, s.name AS station_name FROM assignments a JOIN stations s ON s.id=a.station_id WHERE a.employee_id=? ORDER BY a.start_date DESC""", (emp_id,))
                st.write("**Alocări**")
                st.dataframe(pd.DataFrame(as_rows) if as_rows else pd.DataFrame(), use_container_width=True)


# --- Skills & Training ---
def page_skills(user):
    st.header("Skill Matrix & Training")
    tab1, tab2, tab3, tab4 = st.tabs(["Catalog skill-uri", "Matrice angajați-skill-uri", "Cerințe stații", "Planuri instruire"])
    with db_session(DB_PATH) as conn:
        with tab1:
            with st.form("add_skill"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Nume skill*")
                cat = c2.text_input("Categorie")
                desc = st.text_area("Descriere")
                if st.form_submit_button("Adaugă skill") and name.strip():
                    try:
                        sid = insert_row(conn, "skills", {"name": name.strip(), "category": cat.strip(), "description": desc.strip(), "active": 1})
                        log_action(conn, user, "create", "skills", sid, name.strip())
                        st.success("Skill adăugat.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")
            st.dataframe(df_or_info(list_skills(conn)) or pd.DataFrame(), use_container_width=True)

        employees = list_employees(conn)
        skills = list_skills(conn)
        emp_map = {f"{e['code']} - {e['full_name']}": e["id"] for e in employees}
        skill_map = {s["name"]: s["id"] for s in skills}

        with tab2:
            if not emp_map or not skill_map:
                st.warning("Adaugă angajați și skill-uri.")
            else:
                with st.form("assign_skill"):
                    c1, c2, c3 = st.columns(3)
                    emp = c1.selectbox("Angajat", list(emp_map.keys()))
                    skill = c2.selectbox("Skill", list(skill_map.keys()))
                    level = c3.selectbox("Nivel", options=[0, 1, 2, 3, 4], format_func=lambda x: LEVEL_LABELS[x], index=2)
                    target = c1.selectbox("Nivel țintă", options=[0, 1, 2, 3, 4], format_func=lambda x: LEVEL_LABELS[x], index=4)
                    evaluated = c2.date_input("Data evaluării", value=date.today())
                    expires = c3.text_input("Expiră la (YYYY-MM-DD, opțional)")
                    evaluator = c1.text_input("Evaluator", value=user["username"])
                    notes = c2.text_input("Note")
                    if st.form_submit_button("Salvează evaluare"):
                        data = {
                            "employee_id": emp_map[emp], "skill_id": skill_map[skill], "level": int(level),
                            "target_level": int(target), "evaluated_at": evaluated.isoformat(),
                            "expires_at": expires.strip(), "evaluator": evaluator.strip(), "notes": notes.strip(),
                        }
                        existing = query_one(conn, "SELECT id FROM employee_skills WHERE employee_id=? AND skill_id=?", (data["employee_id"], data["skill_id"]))
                        if existing:
                            update_row(conn, "employee_skills", existing["id"], data)
                            log_action(conn, user, "update", "employee_skills", existing["id"], f"{emp} / {skill}")
                        else:
                            rid = insert_row(conn, "employee_skills", data)
                            log_action(conn, user, "create", "employee_skills", rid, f"{emp} / {skill}")
                        st.success("Evaluare salvată.")
                        st.rerun()
            rows = list_employee_skills(conn)
            st.dataframe(df_or_info(rows) or pd.DataFrame(), use_container_width=True)
            if rows:
                pivot = pd.DataFrame(rows).pivot_table(index="employee_name", columns="skill_name", values="level", aggfunc="max").fillna("-")
                st.write("**Matrice skill-uri (nivel)**")
                st.dataframe(pivot, use_container_width=True)

        with tab3:
            stations = list_stations(conn)
            st_map = {f"{s['department_name']} / {s['cell_name']} / {s['name']}": s["id"] for s in stations}
            if not st_map or not skill_map:
                st.warning("Adaugă stații și skill-uri.")
            else:
                with st.form("add_req"):
                    c1, c2, c3, c4 = st.columns(4)
                    station = c1.selectbox("Stație", list(st_map.keys()))
                    skill = c2.selectbox("Skill cerut", list(skill_map.keys()))
                    min_level = c3.selectbox("Nivel minim", options=[0, 1, 2, 3, 4], format_func=lambda x: LEVEL_LABELS[x], index=2)
                    mandatory = c4.checkbox("Obligatoriu", value=True)
                    if st.form_submit_button("Salvează cerință"):
                        data = {"station_id": st_map[station], "skill_id": skill_map[skill], "min_level": int(min_level), "mandatory": 1 if mandatory else 0}
                        existing = query_one(conn, "SELECT id FROM station_requirements WHERE station_id=? AND skill_id=?", (data["station_id"], data["skill_id"]))
                        if existing:
                            update_row(conn, "station_requirements", existing["id"], data)
                        else:
                            insert_row(conn, "station_requirements", data)
                        log_action(conn, user, "upsert", "station_requirements", "", f"{station} / {skill}")
                        st.success("Cerință salvată.")
                        st.rerun()
            st.dataframe(df_or_info(list_station_requirements(conn)) or pd.DataFrame(), use_container_width=True)

        with tab4:
            if not emp_map or not skill_map:
                st.warning("Adaugă angajați și skill-uri.")
            else:
                with st.form("add_training"):
                    c1, c2, c3 = st.columns(3)
                    emp = c1.selectbox("Angajat training", list(emp_map.keys()))
                    skill = c2.selectbox("Skill training", list(skill_map.keys()))
                    target = c3.selectbox("Nivel țintă training", options=[1, 2, 3, 4], format_func=lambda x: LEVEL_LABELS[x], index=1)
                    due = c1.date_input("Termen", value=date.today())
                    status = c2.selectbox("Status training", ["planificat", "în curs", "finalizat", "întârziat", "anulat"])
                    notes = c3.text_input("Note training")
                    cur_row = query_one(conn, "SELECT level FROM employee_skills WHERE employee_id=? AND skill_id=?", (emp_map[emp], skill_map[skill]))
                    cur_level = int(cur_row["level"]) if cur_row else 0
                    if st.form_submit_button("Salvează plan instruire"):
                        rid = insert_row(conn, "training_plans", {
                            "employee_id": emp_map[emp], "skill_id": skill_map[skill], "current_level": cur_level,
                            "target_level": int(target), "due_date": due.isoformat(), "status": status, "notes": notes.strip(),
                        })
                        log_action(conn, user, "create", "training_plans", rid, f"{emp} / {skill}")
                        st.success("Plan de instruire salvat.")
                        st.rerun()
            st.dataframe(df_or_info(list_training_plans(conn)) or pd.DataFrame(), use_container_width=True)

# --- Assignments ---
def page_assignments(user):
    st.header("Alocări operatori pe celule și stații")
    with db_session(DB_PATH) as conn:
        employees = list_employees(conn)
        stations = list_stations(conn)
        emp_map = {f"{e['code']} - {e['full_name']}": e for e in employees}
        st_map = {f"{s['department_name']} / {s['cell_name']} / {s['name']}": s for s in stations}
        if not emp_map or not st_map:
            st.warning("Adaugă angajați și stații.")
            return
        with st.form("add_assignment"):
            c1, c2, c3 = st.columns(3)
            emp_label = c1.selectbox("Angajat", list(emp_map.keys()))
            st_label = c2.selectbox("Stație", list(st_map.keys()))
            start_d = c3.date_input("Data start", value=date.today())
            end_d = c1.text_input("Data final (YYYY-MM-DD, opțional)")
            status = c2.selectbox("Status alocare", ["activ", "planificat", "finalizat", "anulat"])
            override_reason = c3.text_input("Motiv override (dacă e cazul)")
            check = st.form_submit_button("Verifică eligibilitate")
            save = st.form_submit_button("Salvează alocare")
            emp = emp_map[emp_label]
            station = st_map[st_label]
            elig = check_assignment_eligibility(conn, emp["id"], station["id"])
            if check or save:
                if elig["eligible"]:
                    st.success("Angajatul îndeplinește cerințele obligatorii pentru stație.")
                else:
                    st.warning("Gap-uri identificate:")
                    st.dataframe(pd.DataFrame(elig["gaps"]), use_container_width=True)
            if save:
                can_override = user["role"] in {"Admin", "Manager", "Team Lead"}
                if not elig["eligible"] and not can_override:
                    st.error("Nu ai dreptul să faci override pentru alocare neeligibilă.")
                elif not elig["eligible"] and not override_reason.strip():
                    st.error("Override-ul necesită motiv.")
                else:
                    aid = insert_row(conn, "assignments", {
                        "employee_id": emp["id"], "station_id": station["id"], "start_date": start_d.isoformat(),
                        "end_date": end_d.strip(), "assigned_by": user["username"],
                        "override_reason": override_reason.strip(), "status": status,
                    })
                    log_action(conn, user, "create", "assignments", aid, f"{emp_label} -> {st_label}; override={bool(override_reason.strip())}")
                    st.success("Alocare salvată.")
                    st.rerun()

        st.subheader("Alocări existente")
        st.dataframe(df_or_info(list_assignments(conn)) or pd.DataFrame(), use_container_width=True)

        st.subheader("Acoperire cerințe stație")
        st_label2 = st.selectbox("Selectează stație pentru acoperire", list(st_map.keys()), key="cov_station")
        station2 = st_map[st_label2]
        reqs = query_all(conn, """SELECT sr.*, sk.name AS skill_name FROM station_requirements sr JOIN skills sk ON sk.id=sr.skill_id WHERE sr.station_id=?""", (station2["id"],))
        if not reqs:
            st.info("Stația nu are cerințe definite.")
        else:
            cov_rows = []
            for e in employees:
                elig = check_assignment_eligibility(conn, e["id"], station2["id"])
                cov_rows.append({"Angajat": e["full_name"], "Cod": e["code"], "Eligibil": "Da" if elig["eligible"] else "Nu", "Gap-uri obligatorii": len(elig["mandatory_gaps"]), "Gap-uri totale": len(elig["gaps"])})
            st.dataframe(pd.DataFrame(cov_rows), use_container_width=True)


# --- Performance ---
def page_performance(user):
    st.header("Monitorizare timp, productivitate și calitate")
    with db_session(DB_PATH) as conn:
        employees = list_employees(conn)
        stations = list_stations(conn)
        emp_map = {f"{e['code']} - {e['full_name']}": e["id"] for e in employees}
        st_map = {f"{s['department_name']} / {s['cell_name']} / {s['name']}": s["id"] for s in stations}
        with st.expander("Adaugă înregistrare performanță"):
            if not emp_map or not st_map:
                st.warning("Adaugă angajați și stații.")
            else:
                with st.form("add_perf"):
                    c1, c2, c3 = st.columns(3)
                    emp = c1.selectbox("Angajat", list(emp_map.keys()))
                    station = c2.selectbox("Stație", list(st_map.keys()))
                    work_date = c3.date_input("Data", value=date.today())
                    hours = c1.number_input("Ore lucrate", min_value=0.0, value=8.0, step=0.5)
                    output = c2.number_input("Output (bucăți)", min_value=0.0, value=0.0, step=1.0)
                    scrap = c3.number_input("Rebuturi (bucăți)", min_value=0.0, value=0.0, step=1.0)
                    notes = st.text_input("Note")
                    if st.form_submit_button("Salvează înregistrare"):
                        if scrap > output:
                            st.error("Rebuturile nu pot depăși outputul.")
                        else:
                            pid = insert_row(conn, "performance_logs", {
                                "employee_id": emp_map[emp], "station_id": st_map[station], "work_date": work_date.isoformat(),
                                "hours_worked": float(hours), "output_qty": float(output), "scrap_qty": float(scrap), "notes": notes.strip(),
                            })
                            log_action(conn, user, "create", "performance_logs", pid, emp)
                            st.success("Înregistrare salvată.")
                            st.rerun()

        rows = list_performance_logs(conn)
        if not rows:
            st.info("Nu există înregistrări de performanță.")
            return
        df = pd.DataFrame(rows)
        # filters
        c1, c2, c3 = st.columns(3)
        depts = ["Toate"] + sorted([x for x in df["department_name"].dropna().unique().tolist()])
        cells = ["Toate"] + sorted([x for x in df["cell_name"].dropna().unique().tolist()])
        emps = ["Toți"] + sorted([x for x in df["employee_name"].dropna().unique().tolist()])
        fd = c1.selectbox("Departament", depts)
        fc = c2.selectbox("Celulă", cells)
        fe = c3.selectbox("Angajat", emps)
        view = df.copy()
        if fd != "Toate":
            view = view[view["department_name"] == fd]
        if fc != "Toate":
            view = view[view["cell_name"] == fc]
        if fe != "Toți":
            view = view[view["employee_name"] == fe]
        kpis = performance_kpis(view.to_dict("records"))
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Ore lucrate", f"{kpis['hours']:.1f}")
        k2.metric("Output", f"{kpis['output']:.0f}")
        k3.metric("Rebuturi", f"{kpis['scrap']:.0f}")
        k4.metric("Productivitate", f"{kpis['productivity']:.2f} buc/oră")
        k5.metric("Calitate", f"{kpis['quality_pct']:.1f}%")
        st.dataframe(view, use_container_width=True)


# --- Dashboard ---
def page_dashboard(user):
    st.header("Dashboard performanță")
    with db_session(DB_PATH) as conn:
        rows = list_performance_logs(conn)
        if not rows:
            st.info("Adaugă înregistrări de performanță pentru a vedea graficele.")
            return
        df = pd.DataFrame(rows)
        df["work_date"] = pd.to_datetime(df["work_date"])
        df["productivity"] = df.apply(lambda r: (r["output_qty"] / r["hours_worked"]) if r["hours_worked"] else 0, axis=1)
        df["quality_pct"] = df.apply(lambda r: ((r["output_qty"] - r["scrap_qty"]) / r["output_qty"] * 100) if r["output_qty"] else 0, axis=1)

        c1, c2 = st.columns(2)
        dept = c1.selectbox("Departament", ["Toate"] + sorted(df["department_name"].dropna().unique().tolist()), key="dash_dept")
        emp = c2.selectbox("Angajat", ["Toți"] + sorted(df["employee_name"].dropna().unique().tolist()), key="dash_emp")
        view = df.copy()
        if dept != "Toate":
            view = view[view["department_name"] == dept]
        if emp != "Toți":
            view = view[view["employee_name"] == emp]

        kpis = performance_kpis(view.to_dict("records"))
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ore", f"{kpis['hours']:.1f}")
        k2.metric("Output", f"{kpis['output']:.0f}")
        k3.metric("Productivitate", f"{kpis['productivity']:.2f}")
        k4.metric("Calitate", f"{kpis['quality_pct']:.1f}%")

        by_date = view.groupby(view["work_date"].dt.date).agg({"output_qty": "sum", "scrap_qty": "sum", "hours_worked": "sum"}).reset_index()
        by_date["productivity"] = by_date.apply(lambda r: r["output_qty"] / r["hours_worked"] if r["hours_worked"] else 0, axis=1)
        by_date = by_date.set_index("work_date")
        st.subheader("Trend output și rebuturi")
        st.bar_chart(by_date[["output_qty", "scrap_qty"]])
        st.subheader("Trend productivitate")
        st.line_chart(by_date[["productivity"]])

        st.subheader("Performanță pe angajat")
        by_emp = view.groupby("employee_name").agg({"output_qty": "sum", "scrap_qty": "sum", "hours_worked": "sum"}).reset_index()
        by_emp["productivity"] = by_emp.apply(lambda r: r["output_qty"] / r["hours_worked"] if r["hours_worked"] else 0, axis=1)
        st.dataframe(by_emp, use_container_width=True)
        st.bar_chart(by_emp.set_index("employee_name")[["output_qty", "productivity"]])


# --- Import/Export ---
def page_import(user):
    st.header("Import / Export date")
    tab1, tab2 = st.tabs(["Import", "Export"])
    with tab1:
        entity = st.selectbox("Tip entitate", list(REQUIRED_FIELDS.keys()))
        st.caption(f"Câmpuri obligatorii: {', '.join(REQUIRED_FIELDS[entity])}")
        uploaded = st.file_uploader("Fișier CSV, TXT sau JSON", type=["csv", "txt", "json"])
        if uploaded:
            name, text = read_uploaded_file(uploaded)
            try:
                df = parse_file(name, text)
            except Exception as e:
                st.error(f"Nu s-a putut citi fișierul: {e}")
                return
            st.write("Preview")
            st.dataframe(df.head(50), use_container_width=True)
            errors = validate_import_df(df, entity)
            if errors:
                st.error("Erori de validare:")
                for err in errors[:50]:
                    st.write(f"- {err}")
                if len(errors) > 50:
                    st.write(f"... și încă {len(errors)-50} erori")
            if st.button("Importă date valide", disabled=bool(errors)):
                imported, skipped = import_rows(entity, df, user)
                st.success(f"Import finalizat: {imported} importate, {skipped} omise.")
    with tab2:
        with db_session(DB_PATH) as conn:
            export_map = {
                "departments": list_departments(conn), "cells": list_cells(conn), "stations": list_stations(conn),
                "employees": list_employees(conn), "skills": list_skills(conn), "employee_skills": list_employee_skills(conn),
                "station_requirements": list_station_requirements(conn), "assignments": list_assignments(conn),
                "performance_logs": list_performance_logs(conn), "training_plans": list_training_plans(conn), "audit_log": list_audit_log(conn),
            }
        ex_entity = st.selectbox("Exportă entitate", list(export_map.keys()))
        ex_df = pd.DataFrame(export_map[ex_entity])
        st.dataframe(ex_df, use_container_width=True)
        st.download_button("Descarcă CSV", ex_df.to_csv(index=False).encode("utf-8-sig"), file_name=f"{ex_entity}.csv", mime="text/csv")


def import_rows(entity: str, df: pd.DataFrame, user):
    imported = 0
    skipped = 0
    with db_session(DB_PATH) as conn:
        dept_by_name = {d["name"]: d["id"] for d in list_departments(conn)}
        cell_by_key = {(c["department_name"], c["name"]): c["id"] for c in list_cells(conn)}
        station_by_key = {(s["department_name"], s["cell_name"], s["name"]): s["id"] for s in list_stations(conn)}
        emp_by_code = {e["code"]: e["id"] for e in list_employees(conn)}
        skill_by_name = {s["name"]: s["id"] for s in list_skills(conn)}
        station_by_name = {s["name"]: s["id"] for s in list_stations(conn)}

        for _, row in df.iterrows():
            r = {k: ("" if pd.isna(v) else str(v).strip()) for k, v in row.to_dict().items()}
            try:
                if entity == "departments":
                    insert_row(conn, "departments", {"name": r["name"], "description": r.get("description", ""), "active": int(r.get("active", "1") or 1)})
                elif entity == "cells":
                    did = dept_by_name.get(r["department_name"])
                    if not did: skipped += 1; continue
                    insert_row(conn, "cells", {"department_id": did, "name": r["name"], "description": r.get("description", ""), "active": int(r.get("active", "1") or 1)})
                elif entity == "stations":
                    cid = cell_by_key.get((r["department_name"], r["cell_name"]))
                    if not cid: skipped += 1; continue
                    insert_row(conn, "stations", {"cell_id": cid, "name": r["name"], "description": r.get("description", ""), "active": int(r.get("active", "1") or 1)})
                elif entity == "employees":
                    insert_row(conn, "employees", {
                        "code": r["code"], "full_name": r["full_name"], "email": r.get("email", ""), "role_title": r.get("role_title", ""),
                        "department_id": dept_by_name.get(r.get("department_name", "")), "cell_id": cell_by_key.get((r.get("department_name", ""), r.get("cell_name", ""))),
                        "hire_date": r.get("hire_date", ""), "status": r.get("status", "activ") or "activ",
                    })
                elif entity == "skills":
                    insert_row(conn, "skills", {"name": r["name"], "category": r.get("category", ""), "description": r.get("description", ""), "active": int(r.get("active", "1") or 1)})
                elif entity == "employee_skills":
                    eid = emp_by_code.get(r["employee_code"]); sid = skill_by_name.get(r["skill_name"])
                    if not eid or not sid: skipped += 1; continue
                    existing = query_one(conn, "SELECT id FROM employee_skills WHERE employee_id=? AND skill_id=?", (eid, sid))
                    data = {"employee_id": eid, "skill_id": sid, "level": int(float(r.get("level", 0))), "target_level": int(float(r.get("target_level", 4))), "evaluated_at": r.get("evaluated_at", ""), "expires_at": r.get("expires_at", ""), "evaluator": r.get("evaluator", ""), "notes": r.get("notes", "")}
                    if existing: update_row(conn, "employee_skills", existing["id"], data)
                    else: insert_row(conn, "employee_skills", data)
                elif entity == "station_requirements":
                    stid = station_by_name.get(r["station_name"]); sid = skill_by_name.get(r["skill_name"])
                    if not stid or not sid: skipped += 1; continue
                    existing = query_one(conn, "SELECT id FROM station_requirements WHERE station_id=? AND skill_id=?", (stid, sid))
                    data = {"station_id": stid, "skill_id": sid, "min_level": int(float(r.get("min_level", 0))), "mandatory": int(float(r.get("mandatory", 1)))}
                    if existing: update_row(conn, "station_requirements", existing["id"], data)
                    else: insert_row(conn, "station_requirements", data)
                elif entity == "assignments":
                    eid = emp_by_code.get(r["employee_code"]); stid = station_by_name.get(r["station_name"])
                    if not eid or not stid: skipped += 1; continue
                    insert_row(conn, "assignments", {"employee_id": eid, "station_id": stid, "start_date": r["start_date"], "end_date": r.get("end_date", ""), "assigned_by": r.get("assigned_by", user["username"]), "override_reason": r.get("override_reason", ""), "status": r.get("status", "activ")})
                elif entity == "performance_logs":
                    eid = emp_by_code.get(r["employee_code"]); stid = station_by_name.get(r["station_name"])
                    if not eid or not stid: skipped += 1; continue
                    insert_row(conn, "performance_logs", {"employee_id": eid, "station_id": stid, "work_date": r["work_date"], "hours_worked": float(r["hours_worked"]), "output_qty": float(r["output_qty"]), "scrap_qty": float(r.get("scrap_qty", 0) or 0), "notes": r.get("notes", "")})
                elif entity == "training_plans":
                    eid = emp_by_code.get(r["employee_code"]); sid = skill_by_name.get(r["skill_name"])
                    if not eid or not sid: skipped += 1; continue
                    insert_row(conn, "training_plans", {"employee_id": eid, "skill_id": sid, "current_level": int(float(r.get("current_level", 0))), "target_level": int(float(r["target_level"])), "due_date": r.get("due_date", ""), "status": r.get("status", "planificat"), "notes": r.get("notes", "")})
                else:
                    skipped += 1; continue
                imported += 1
            except Exception:
                skipped += 1
        log_action(conn, user, "import", entity, "", f"imported={imported}, skipped={skipped}")
    return imported, skipped


# --- Admin ---
def page_admin(user):
    st.header("Administrare utilizatori și drepturi")
    with db_session(DB_PATH) as conn:
        with st.form("add_user"):
            c1, c2, c3 = st.columns(3)
            username = c1.text_input("Username")
            password = c2.text_input("Parolă", type="password")
            role = c3.selectbox("Rol", ROLES)
            active = c1.checkbox("Activ", value=True)
            if st.form_submit_button("Creează utilizator"):
                if not username.strip() or not password:
                    st.error("Username și parola sunt obligatorii.")
                else:
                    try:
                        uid = insert_row(conn, "users", {"username": username.strip(), "password_hash": hash_password(password), "role": role, "employee_id": None, "active": 1 if active else 0, "created_at": pd.Timestamp.utcnow().isoformat()})
                        log_action(conn, user, "create", "users", uid, username.strip())
                        st.success("Utilizator creat.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare: {e}")
        users = query_all(conn, "SELECT id, username, role, active, created_at FROM users ORDER BY username")
        st.dataframe(pd.DataFrame(users) if users else pd.DataFrame(), use_container_width=True)
        st.subheader("Matrice permisiuni pe rol (rezumat)")
        perms = pd.DataFrame([
            {"Rol": r, "Organizație": "Da" if r in {"Admin","Manager"} else "Nu", "Angajați/Skill": "Da" if r in {"Admin","Manager","Team Lead","HR/Training"} else "Nu", "Alocări": "Da" if r in {"Admin","Manager","Team Lead"} else "Nu", "Performanță": "Da" if r in {"Admin","Manager","Team Lead"} else "Nu", "Import": "Da" if r in {"Admin","Manager"} else "Nu", "Administrare": "Da" if r=="Admin" else "Nu", "Audit": "Da" if r in {"Admin","Auditor","Manager"} else "Nu"}
            for r in ROLES
        ])
        st.dataframe(perms, use_container_width=True, hide_index=True)


# --- Audit ---
def page_audit(user):
    st.header("Audit log")
    with db_session(DB_PATH) as conn:
        rows = list_audit_log(conn, limit=300)
    st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True)


# --- My profile ---
def page_my_profile(user):
    st.header("Profilul meu")
    st.write(f"**Utilizator:** {user['username']}")
    st.write(f"**Rol:** {user['role']}")
    st.info("În MVP, profilul operatorului este legat de contul de utilizator. Pentru legare completă, setează `employee_id` în administrare (extensie viitoare).")


def main():
    init_app()
    user = require_login()
    page = sidebar(user)
    if not can_access(user["role"], page):
        st.error("Nu ai permisiuni pentru această pagină.")
        return
    routes = {
        "dashboard": page_dashboard,
        "organization": page_organization,
        "employees": page_employees,
        "skills": page_skills,
        "assignments": page_assignments,
        "performance": page_performance,
        "import": page_import,
        "admin": page_admin,
        "audit": page_audit,
        "my_profile": page_my_profile,
    }
    routes[page](user)


if __name__ == "__main__":
    main()
