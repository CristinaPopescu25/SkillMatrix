# SkillMatrix – Employee Qualification & Performance Management System

Aplicație MVP pentru gestionarea calificărilor, polivalenței și performanței angajaților, adaptabilă mediilor industriale și logistice.

## Obiective acoperite

- Configurare departamente, celule și stații.
- Profiluri individuale angajați.
- Repartizare operatori pe stații în funcție de calificări (cu verificare eligibilitate și override justificat).
- Monitorizare timp lucrat, productivitate și calitate.
- Dashboard cu grafice și statistici.
- Evaluare calificări, polivalență și progres instruire.
- Import manual/CSV/TXT/JSON și export CSV.
- Administrare utilizatori și drepturi de acces (RBAC) + audit log.

## Structură proiect

```text
.
├── app.py                      # UI Streamlit (SkillMatrix)
├── skillmatrix_db.py           # Schema SQLite + interogări + logică business
├── skillmatrix_auth.py         # Autentificare, hash parole, RBAC
├── skillmatrix_import.py       # Parser/validare CSV/TXT/JSON
├── requirements.txt
├── run.bat
├── docs/
│   ├── Obiective.md
│   ├── SRD.md
│   ├── SRS.md
│   ├── Scenarii_Test.md
│   ├── Rezultate_Intermediare.md
│   ├── Activitati_Roluri.md
│   └── Grafic_Implementare.md
└── tests/
    └── test_skillmatrix.py
```

## Instalare (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Rulare

```powershell
.\run.bat
```

sau

```powershell
python -m streamlit run app.py
```

## Cont implicit MVP

- **Utilizator:** `admin`
- **Parolă:** `admin123`

> Schimbă parola implicită pentru orice utilizare reală.

## Import date

Formate acceptate: `.csv`, `.txt`, `.json`.

Entități suportate: departamente, celule, stații, angajați, skill-uri, skill-uri angajați, cerințe stații, alocări, loguri performanță, planuri instruire.

Importul validează câmpurile obligatorii și raportează erorile pe rând. Datele sunt importate în SQLite (`skillmatrix.db`).

## Teste

```powershell
python -m unittest discover -s tests -v
```

## Documentație livrabilă

Documentele cerute se află în folderul `docs/`:
- Obiective generale și specifice
- SRD & SRS
- Scenarii de test
- Rezultate intermediare
- Activități pe roluri
- Grafic de implementare

## Publicare pe GitHub

Repo-ul local este pregătit pentru commit. Pentru publicare într-un repo nou:

```powershell
git add .
git commit -m "Add SkillMatrix MVP and documentation"
# creează un repo gol pe GitHub, apoi:
git remote add skillmatrix https://github.com/<user>/SkillMatrix.git
git push -u skillmatrix HEAD:main
```

Dacă vrei să folosești remote-ul existent, înlocuiește URL-ul corespunzător. Verifică înainte de push că nu suprascrii un proiect diferit.