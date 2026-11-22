# SkillMatrix – Employee Qualification & Performance Management System

Proiect realizat de 3 studenți pentru gestionarea calificărilor, polivalenței și performanței angajaților în medii industriale și logistice.

## Obiective

- Configurarea departamentelor, celulelor și stațiilor.
- Crearea și gestionarea profilurilor angajaților.
- Repartizarea operatorilor pe stații în funcție de calificări.
- Monitorizarea timpului de lucru, productivității și calității.
- Vizualizarea performanței prin grafice și statistici.
- Evaluarea calificărilor, polivalenței și progresului de instruire.
- Import manual sau din fișiere CSV, TXT, JSON.
- Administrarea utilizatorilor și a drepturilor de acces.

## Structură proiect

```text
.
├── app.py                      # Aplicația Streamlit
├── skillmatrix_db.py           # Bază de date SQLite și logică business
├── skillmatrix_auth.py         # Autentificare și roluri
├── skillmatrix_import.py       # Import CSV/TXT/JSON
├── requirements.txt
├── run.bat
├── docs/                       # Documentație proiect
└── tests/
    └── test_skillmatrix.py
```

## Instalare și rulare

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Cont implicit MVP: `admin` / `admin123`

## Teste

```powershell
python -m unittest discover -s tests -v
```

## Documentație

În folderul `docs/` se găsesc: Obiective, SRD, SRS, Scenarii de test, Rezultate intermediare, Activități pe roluri, Grafic de implementare.