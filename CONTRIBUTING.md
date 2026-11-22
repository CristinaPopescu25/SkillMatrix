# Contribuție echipă – SkillMatrix

## Propunere împărțire (3 persoane)

> Ajustați după rolurile reale din echipă. Fiecare persoană trebuie să aibă commit-uri proprii.

### Persoana 1 – Analiză / Documentație
- `docs/Obiective.md`
- `docs/SRD.md`
- `docs/SRS.md`
- `README.md` (revizuire)

### Persoana 2 – Implementare aplicație
- `app.py`
- `skillmatrix_db.py`
- `skillmatrix_auth.py`
- `skillmatrix_import.py`
- `requirements.txt`, `run.bat`

### Persoana 3 – Testare / Planificare / Livrare
- `docs/Scenarii_Test.md`
- `docs/Rezultate_Intermediare.md`
- `docs/Activitati_Roluri.md`
- `docs/Grafic_Implementare.md`
- `tests/test_skillmatrix.py`
- `.gitignore`

## Flux recomandat GitHub

1. **Persoana 1** creează repo-ul pe GitHub și încarcă baza proiectului.
2. Adaugă colegii ca **Collaborators**: GitHub repo → *Settings* → *Collaborators*.
3. Fiecare persoană lucrează pe branch propriu:
   ```bash
   git checkout -b feature/nume-task
   # modificări
   git add .
   git commit -m "Descriere clară"
   git push -u origin feature/nume-task
   ```
4. Deschide **Pull Request** către `main`, cere review, apoi merge.
5. Evitați push direct pe `main` după setup-ul inițial.

## Reguli simple
- Commit-uri mici, cu mesaje clare.
- Nu urcați `skillmatrix.db`, `.venv/`, `__pycache__/`, secrete.
- Rulați testele înainte de PR: `python -m unittest discover -s tests -v`.