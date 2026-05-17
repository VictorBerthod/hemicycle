# Roadmap et jalons

## Jalons MVP

| Jalon | Contenu | Duree estimee | Dependances |
|-------|---------|---------------|-------------|
| J0 — Setup | Repo, Docker, CI, structure projet | 2-3 jours | — |
| J1 — Data pipeline | ETL deputes + scrutins depuis API AN | 1 semaine | J0 |
| J2 — Backend API | Endpoints REST : deputes, scrutins, votes | 1 semaine | J1 |
| J3 — Frontend socle | SvelteKit, pages deputes, liste scrutins | 1-2 semaines | J2 |
| J4 — Visualisations | Graphes de votes, dissidences, groupes | 1-2 semaines | J3 |
| J5 — Module IA angles | Generation d'analyses + interface validation | 1 semaine | J2 |
| J6 — HATVP | Integration declarations d'interets | 3-4 jours | J1 |
| J7 — Accessibilite + perf | Audit RGAA, optimisations, tests utilisateurs | 1 semaine | J3, J4 |
| J8 — Lancement MVP | Deploiement, 10 analyses publiees, communication | 3-4 jours | Tous |

**Total estime MVP : 6-8 semaines** de travail effectif.

## Post-MVP

| Phase | Contenu | Priorite |
|-------|---------|----------|
| P2.1 | Senat + comparateur deputes | Haute |
| P2.2 | Graphes lobbys (HATVP registre) | Haute |
| P2.3 | Alertes personnalisees | Moyenne |
| P3.1 | Parlement europeen | Basse |
| P3.2 | API publique | Moyenne |
