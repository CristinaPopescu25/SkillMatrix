# SRD – System Requirements Document
## SkillMatrix – Employee Qualification & Performance Management System

**Versiune:** 1.0  
**Data:** 2026-11-22  
**Status:** Draft aprobat pentru implementare MVP

## 1. Introducere

### 1.1 Scop
Documentul definește cerințele de sistem la nivel înalt pentru SkillMatrix, o aplicație destinată gestionării calificărilor, polivalenței și performanței angajaților în medii industriale și logistice.

### 1.2 Domeniu
SkillMatrix oferă:
- modelare organizațională (departamente, celule, stații);
- gestionare angajați și competențe;
- alocare pe stații pe baza calificărilor;
- monitorizare timp/productivitate/calitate;
- dashboard și rapoarte;
- import date CSV/TXT/JSON;
- administrare utilizatori și drepturi de acces.

### 1.3 Definiții și abrevieri
| Termen | Definiție |
|---|---|
| Skill Matrix | Matrice care corelează angajații cu competențele și nivelurile acestora |
| Polivalență | Capacitatea unui angajat de a opera pe mai multe stații/competențe |
| Stație | Post de lucru sau punct operațional |
| Celulă | Grup de stații în cadrul unui departament |
| KPI | Indicator cheie de performanță |
| RBAC | Role-Based Access Control |
| MVP | Minimum Viable Product |

## 2. Stakeholderi și utilizatori

| Rol | Interes | Responsabilități |
|---|---|---|
| Administrator sistem | Configurare, securitate, continuitate | Gestionează utilizatori, roluri, setări, importuri |
| Manager departament | Performanță și acoperire competențe | Monitorizează KPI, aprobă alocări, analizează gap-uri |
| Team Lead / Supervizor | Operare zilnică | Alocă operatori, introduce date de producție/calitate, evaluează skill-uri |
| Operator / Angajat | Vizibilitate asupra propriului profil | Consultă profil, calificări, instruiri, performanță proprie |
| HR / Training | Dezvoltare competențe | Gestionează planuri de instruire, evaluări, expirări calificări |
| Auditor / Calitate | Trasabilitate | Consultă înregistrări, audit log, rapoarte |

## 3. Context de sistem

### 3.1 Mediu operațional
- Aplicație web locală, rulată în rețea internă sau pe stație de lucru.
- MVP implementat în Python/Streamlit, cu persistenta SQLite.
- Compatibilă Windows; poate fi rulată și pe Linux/macOS cu Python.

### 3.2 Interfețe externe
- **Fișiere**: import CSV, TXT, JSON; export CSV.
- **Sistem de fișiere**: baza de date SQLite locală.
- **Utilizator**: browser web.

## 4. Cerințe de sistem

### 4.1 Cerințe funcționale de sistem
- **SYS-F-01**: Sistemul trebuie să permită modelarea ierarhică Departament > Celulă > Stație.
- **SYS-F-02**: Sistemul trebuie să gestioneze profiluri de angajați și asocierea lor la structura organizațională.
- **SYS-F-03**: Sistemul trebuie să gestioneze un catalog de skill-uri și niveluri de calificare per angajat.
- **SYS-F-04**: Sistemul trebuie să definească cerințe de skill pentru stații și să valideze alocările.
- **SYS-F-05**: Sistemul trebuie să înregistreze date de timp, producție și calitate.
- **SYS-F-06**: Sistemul trebuie să calculeze KPI și să afișeze grafice/statistici.
- **SYS-F-07**: Sistemul trebuie să importe date din CSV, TXT și JSON cu validare.
- **SYS-F-08**: Sistemul trebuie să gestioneze autentificarea, rolurile și permisiunile.
- **SYS-F-09**: Sistemul trebuie să păstreze audit log pentru acțiuni critice.

### 4.2 Cerințe non-funcționale
- **SYS-NF-01 Securitate**: parole stocate hash-uit; acces bazat pe roluri; sesiune autentificată.
- **SYS-NF-02 Usabilitate**: interfață web intuitivă, mesaje de eroare clare, formulare validate.
- **SYS-NF-03 Performanță**: încărcarea paginilor principale sub 2s pentru seturi de date MVP (<10.000 înregistrări).
- **SYS-NF-04 Fiabilitate**: validare la import; tranzacții DB pentru operații critice; backup prin copiere fișier SQLite.
- **SYS-NF-05 Portabilitate**: rulare locală cu Python 3.11+; fără dependențe de cloud obligatorii.
- **SYS-NF-06 Mentenabilitate**: cod modular, teste automate, structură documentată.
- **SYS-NF-07 Trasabilitate**: audit log pentru creare/modificare/ștergere/import.

### 4.3 Constrângeri
- MVP local, fără infrastructură cloud obligatorie.
- Baza de date SQLite pentru simplitate; migrare ulterioară posibilă la PostgreSQL.
- Importul trebuie să accepte fișiere cu separator variabil și codare UTF-8.

### 4.4 Presupuneri și dependențe
- Utilizatorii au browser modern și Python instalat.
- Datele importate respectă un template sau mapare de coloane.
- KPI-urile sunt calculate din datele introduse/importate în aplicație.

## 5. Criterii de acceptare la nivel de sistem
- Administratorul poate configura structura organizațională și utilizatorii.
- Team Lead poate aloca un angajat doar dacă îndeplinește cerințele minime sau cu override justificat.
- Managerul poate vizualiza KPI și grafice filtrate.
- Importul CSV/TXT/JSON raportează erorile fără a corupe datele existente.
- Utilizatorii neautorizați nu pot accesa funcții administrative.