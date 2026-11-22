# Scenarii de test – SkillMatrix

## Convenții
- **Tip**: FUNC (funcțional), SEC (securitate), VAL (validare), IMP (import), UI (interfață), REG (regresie).
- **Prioritate**: P1 critic, P2 important, P3 normal.
- **Rezultat așteptat**: comportamentul observabil la final.

## Scenarii

| ID | Tip | Prioritate | Modul | Precondiții | Pași | Rezultat așteptat |
|---|---|---:|---|---|---|---|
| TC-AUTH-01 | SEC | P1 | Autentificare | Utilizator activ există | 1. Deschide app 2. Introdu username/parolă valide 3. Login | Utilizatorul este autentificat și vede meniul conform rolului |
| TC-AUTH-02 | SEC | P1 | Autentificare | Utilizator există | 1. Introdu parolă greșită 2. Login | Mesaj de eroare; acces refuzat; fără sesiune |
| TC-RBAC-01 | SEC | P1 | RBAC | User rol Operator | 1. Login ca Operator 2. Accesează Administrare | Modulul nu este accesibil; mesaj lipsă permisiuni |
| TC-ORG-01 | FUNC | P1 | Organizație | Admin autentificat | 1. Creează departament 2. Creează celulă 3. Creează stație | Ierarhia este salvată și afișată corect |
| TC-EMP-01 | FUNC | P1 | Angajați | Departament/celulă există | 1. Adaugă angajat cu date valide 2. Salvează | Profilul apare în listă și poate fi deschis |
| TC-EMP-02 | VAL | P2 | Angajați | Admin autentificat | 1. Încearcă salvare fără nume/cod | Validare blochează salvarea; mesaj clar |
| TC-SK-01 | FUNC | P1 | Skill Matrix | Angajat și skill există | 1. Atribuie skill nivel 2 2. Salvează | Înregistrarea apare în matricea angajatului |
| TC-SK-02 | FUNC | P2 | Polivalență | Angajat are skill-uri | 1. Deschide profil 2. Verifică indicator polivalență | Procentul corespunde formulei definite |
| TC-ALLOC-01 | FUNC | P1 | Alocare | Stație are cerințe; angajat calificat | 1. Creează alocare 2. Salvează | Alocarea este acceptată și vizibilă |
| TC-ALLOC-02 | SEC/VAL | P1 | Alocare | Angajat sub nivel minim | 1. Încearcă alocare fără override | Sistemul blochează alocarea și afișează gap-ul |
| TC-ALLOC-03 | SEC | P1 | Alocare | Team Lead/Admin, angajat sub nivel | 1. Alocare cu override 2. Introdu motiv | Alocarea salvată; motiv și acțiune în audit log |
| TC-PERF-01 | FUNC | P1 | Performanță | Angajat și stație există | 1. Adaugă log cu ore/output/rebuturi 2. Salvează | KPI se calculează; logul apare în tabel |
| TC-PERF-02 | VAL | P2 | Performanță | Formular deschis | 1. Introdu rebuturi > output | Validare blochează salvarea |
| TC-DASH-01 | UI | P2 | Dashboard | Există date performanță | 1. Deschide dashboard 2. Aplică filtre | Graficele și KPI se actualizează corect |
| TC-IMP-01 | IMP | P1 | Import | Fișier CSV valid | 1. Selectează tip entitate 2. Încarcă CSV 3. Preview 4. Import | Datele sunt importate; raport success |
| TC-IMP-02 | IMP | P1 | Import | Fișier JSON valid | 1. Încarcă JSON 2. Import | Înregistrările valide sunt salvate |
| TC-IMP-03 | IMP | P1 | Import | Fișier TXT delimitat valid | 1. Încarcă TXT 2. Import | Parserul detectează delimitatorul și importă datele |
| TC-IMP-04 | VAL | P1 | Import | Fișier cu erori | 1. Încarcă fișier cu rânduri invalide | Rândurile invalide sunt raportate; datele valide conform politicii; DB consistentă |
| TC-IMP-05 | SEC | P2 | Import | Fișier neacceptat/malformat | 1. Încarcă fișier binar sau JSON invalid | Eroare controlată, fără crash |
| TC-ADM-01 | FUNC | P1 | Administrare | Admin autentificat | 1. Creează utilizator cu rol 2. Salvează | Utilizatorul se poate autentifica cu rolul atribuit |
| TC-AUD-01 | SEC | P2 | Audit | Acțiune critică efectuată | 1. Creează/modifică/importă 2. Deschide audit log | Evenimentul este înregistrat cu user, timp, entitate |
| TC-REG-01 | REG | P2 | General | După modificări cod | 1. Rulează testele automate | Toate testele trec |

## Date de test recomandate
- 2 departamente, 4 celule, 8 stații.
- 10 angajați cu niveluri diferite de skill.
- 6 skill-uri, cerințe pe stații.
- 30 înregistrări performanță pe 2 săptămâni.
- Fișiere import: CSV valid, CSV invalid, TXT tab-delimited, JSON listă, JSON invalid.