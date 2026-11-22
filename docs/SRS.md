# SRS – Software Requirements Specification
## SkillMatrix – Employee Qualification & Performance Management System

**Versiune:** 1.0  
**Data:** 2026-11-22

## 1. Introducere

### 1.1 Scop
SRS detaliază cerințele software pentru implementarea MVP SkillMatrix.

### 1.2 Public țintă
Echipă de dezvoltare, testare, product owner, stakeholderi operaționali.

### 1.3 Referințe
- `docs/Obiective.md`
- `docs/SRD.md`

## 2. Descriere generală

### 2.1 Perspectiva produsului
Aplicație web locală Streamlit cu bază de date SQLite. Interfața este organizată pe module accesibile în funcție de rol.

### 2.2 Clase de utilizatori
| Rol | Permisiuni principale |
|---|---|
| Admin | CRUD complet, utilizatori, roluri, import, audit |
| Manager | Vizualizare toate modulele, rapoarte, aprobare alocări, training |
| Team Lead | Alocări, evaluări skill, introducere performanță, vizualizare echipă |
| HR/Training | Skill-uri, evaluări, planuri instruire, rapoarte training |
| Operator | Vizualizare profil propriu, skill-uri proprii, performanță proprie |
| Auditor | Vizualizare read-only și audit log |

### 2.3 Constrângeri de design
- Python 3.11+.
- Streamlit pentru UI.
- SQLite pentru persistență.
- Pandas pentru import/analiză.
- Fără dependențe externe obligatorii pentru funcțiile de bază.

## 3. Cerințe funcționale detaliate

### 3.1 Autentificare și administrare
- **FR-AUTH-01**: Sistemul permite autentificare cu username și parolă.
- **FR-AUTH-02**: Parolele sunt stocate ca hash (PBKDF2/SHA256).
- **FR-AUTH-03**: Admin poate crea, dezactiva și modifica utilizatori.
- **FR-AUTH-04**: Admin poate atribui roluri.
- **FR-RBAC-01**: Accesul la pagini/acțiuni este controlat pe rol.
- **FR-AUD-01**: Acțiunile critice sunt înregistrate în audit log.

### 3.2 Structură organizațională
- **FR-ORG-01**: Admin/Manager poate crea departamente.
- **FR-ORG-02**: Admin/Manager poate crea celule în cadrul unui departament.
- **FR-ORG-03**: Admin/Manager poate crea stații în cadrul unei celule.
- **FR-ORG-04**: Entitățile pot fi activate/dezactivate.
- **FR-ORG-05**: UI afișează structura ierarhică.

### 3.3 Angajați
- **FR-EMP-01**: Creare profil angajat: cod, nume, email, rol, departament/celulă, data angajării, status.
- **FR-EMP-02**: Editare și dezactivare angajat.
- **FR-EMP-03**: Căutare/filtrare după nume, departament, celulă, status.
- **FR-EMP-04**: Vizualizare profil cu skill-uri, alocări și performanță.

### 3.4 Skill-uri și calificări
- **FR-SK-01**: Definire catalog skill-uri cu categorie și descriere.
- **FR-SK-02**: Definire niveluri 0-4: 0=Neinstruit, 1=În instruire, 2=Autonom, 3=Avansat, 4=Expert/Trainer.
- **FR-SK-03**: Atribuire skill la angajat cu nivel, dată evaluare, evaluator, expirare.
- **FR-SK-04**: Calcul polivalență: număr skill-uri nivel >=2 / total skill-uri relevante.
- **FR-SK-05**: Identificare gap-uri: cerințe stație vs. skill-uri angajat.
- **FR-SK-06**: Plan instruire: skill țintă, nivel țintă, termen, status.

### 3.5 Alocare pe stații
- **FR-ALLOC-01**: Definire cerințe skill per stație (skill, nivel minim, obligatoriu).
- **FR-ALLOC-02**: Alocare angajat la stație/celulă pentru o perioadă.
- **FR-ALLOC-03**: Sistemul verifică eligibilitatea pe baza skill-urilor.
- **FR-ALLOC-04**: Override permis doar pentru roluri autorizate, cu motiv și audit.
- **FR-ALLOC-05**: Vizualizare acoperire stații și alocări active.

### 3.6 Monitorizare performanță
- **FR-PERF-01**: Înregistrare log: angajat, stație, dată, ore lucrate, output, rebuturi.
- **FR-PERF-02**: Calcul productivitate: output/oră.
- **FR-PERF-03**: Calcul calitate: (output - rebuturi) / output.
- **FR-PERF-04**: Filtrare pe perioadă, departament, celulă, stație, angajat.
- **FR-PERF-05**: Dashboard cu grafice trend, bar chart, KPI cards.

### 3.7 Import/Export
- **FR-IMP-01**: Import CSV cu separator detectat automat (virgulă, punct-virgulă, tab).
- **FR-IMP-02**: Import TXT delimitat (tab/; /, /|).
- **FR-IMP-03**: Import JSON (listă de obiecte sau obiect cu cheie de date).
- **FR-IMP-04**: Validare schema, tipuri, câmpuri obligatorii; raport erori pe rând.
- **FR-IMP-05**: Preview înainte de importul final.
- **FR-IMP-06**: Export CSV pentru rapoarte principale.

## 4. Cerințe de date

### 4.1 Entități principale
| Entitate | Câmpuri cheie |
|---|---|
| users | id, username, password_hash, role, employee_id, active, created_at |
| departments | id, name, description, active |
| cells | id, department_id, name, description, active |
| stations | id, cell_id, name, description, active |
| employees | id, code, full_name, email, role_title, department_id, cell_id, hire_date, status |
| skills | id, name, category, description, active |
| employee_skills | id, employee_id, skill_id, level, target_level, evaluated_at, expires_at, evaluator, notes |
| station_requirements | id, station_id, skill_id, min_level, mandatory |
| assignments | id, employee_id, station_id, start_date, end_date, assigned_by, override_reason, status |
| performance_logs | id, employee_id, station_id, work_date, hours_worked, output_qty, scrap_qty, notes |
| training_plans | id, employee_id, skill_id, current_level, target_level, due_date, status, notes |
| audit_log | id, user_id, action, entity, entity_id, details, created_at |

### 4.2 Integritate
- Chei străine pentru relații.
- Statusuri controlate prin valori permise.
- Validări la nivel de aplicație și DB.

## 5. Cerințe non-funcționale

- **NFR-SEC-01**: Hash parole PBKDF2-HMAC-SHA256 cu salt.
- **NFR-SEC-02**: Control acces pe rol la fiecare pagină/acțiune.
- **NFR-USE-01**: Mesaje de eroare în limba română.
- **NFR-PERF-01**: Interogări indexate pe chei străine și date frecvent filtrate.
- **NFR-REL-01**: Importul eșuat nu scrie parțial; se raportează erorile.
- **NFR-MAINT-01**: Structură modulară: `db.py`, `auth.py`, `importers.py`, `ui/*` sau module logice.

## 6. Criterii de acceptare

- Toate modulele din obiectivele specifice sunt accesibile în MVP.
- Utilizatorul poate importa un CSV valid și vede înregistrările.
- Alocarea unui angajat necalificat este blocată sau necesită override autorizat.
- Dashboard-ul afișează KPI și grafice pentru datele existente.
- Admin poate crea utilizator și rol; utilizatorul se autentifică.