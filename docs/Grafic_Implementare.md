# Grafic de implementare – SkillMatrix

## Rezumat plan
- **Durată totală:** 10 săptămâni (MVP + documentare + livrare)
- **Metodologie:** iterativă, cu livrabile intermediare
- **Echipă recomandată:** 1 PM/BA, 1 developer full-stack Python, 1 tester/QA, 1 stakeholder domeniu

## Grafic Gantt (simplificat)

| Fază | Activități principale | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1. Analiză | Colectare cerințe, obiective, SRD/SRS | X | X |  |  |  |  |  |  |  |  |
| 2. Design | Model date, RBAC, UX, fluxuri import |  | X | X |  |  |  |  |  |  |  |
| 3. Fundament | DB, auth, structură organizațională |  |  | X | X |  |  |  |  |  |  |
| 4. Core HR/Skill | Angajați, skill matrix, training |  |  |  | X | X |  |  |  |  |  |
| 5. Operațional | Alocări, cerințe stații, override/audit |  |  |  |  | X | X |  |  |  |  |
| 6. Performanță | Loguri, KPI, dashboard, grafice |  |  |  |  |  | X | X |  |  |  |
| 7. Import/Export | CSV/TXT/JSON, validare, rapoarte |  |  |  |  |  |  | X | X |  |  |
| 8. Testare | Teste unitare, scenarii, bugfix |  |  |  |  |  |  |  | X | X |  |
| 9. Livrare | Documentație finală, README, GitHub |  |  |  |  |  |  |  |  | X | X |

## Milestone-uri

| Milestone | Săptămână | Criteriu de finalizare |
|---|---:|---|
| M1 – Cerințe aprobate | S2 | SRD/SRS și obiective semnate |
| M2 – Bază tehnică | S4 | DB, auth, structură organizațională funcționale |
| M3 – Skill & Alocare | S6 | Matrice skill, cerințe stații, alocări cu validare |
| M4 – Performanță & Dashboard | S7 | KPI și grafice funcționale |
| M5 – Import & Testare | S9 | Import CSV/TXT/JSON și teste trecute |
| M6 – Livrare | S10 | Cod pe GitHub, documentație completă |

## Resurse și responsabilități

| Rol proiect | Responsabilități principale |
|---|---|
| Project Manager / BA | Cerințe, planificare, comunicare stakeholderi |
| Developer | Implementare DB, logică, UI, import, rapoarte |
| QA / Tester | Scenarii test, testare, raportare defecte |
| Product Owner / Stakeholder | Validare cerințe, acceptanță livrabile |