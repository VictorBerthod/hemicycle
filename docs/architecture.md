# Architecture technique

## Stack

- **Frontend**: SvelteKit (SSR) + D3.js (visualisations) + CSS custom (dark theme, sobre, accessible)
- **Backend**: Python + FastAPI
- **Base de donnees**: SQLite (MVP), migration PostgreSQL si volume l'exige
- **Pipeline ETL**: Scripts Python, cron jobs, sync quotidienne
- **Module IA**: Generation d'analyses (LLM), validation humaine obligatoire
- **Infra**: Docker Compose, services bindes sur 127.0.0.1

## Schema general

```
+-----------------------------------------------------+
|                    FRONTEND                          |
|  SvelteKit (SSR) + D3.js (visualisations)           |
|  CSS custom (dark theme, sobre, accessible)         |
|  Score Lighthouse > 90                              |
+----------------------------+------------------------+
                             | API REST
+----------------------------+------------------------+
|                    BACKEND                           |
|  Python + FastAPI                                   |
|  Module ETL : collecte + normalisation              |
|  Module IA : generation d'analyses (LLM)            |
|  Module editorial : file de validation humaine      |
+----------------------------+------------------------+
                             |
+----------------------------+------------------------+
|                 DONNEES                              |
|  SQLite (MVP) — tables : deputes, scrutins,         |
|  votes, declarations_interet, analyses              |
|  Cron jobs : sync quotidienne API AN                |
+-----------------------------------------------------+
```

## Pipeline editorial hybride

```
API AN/HATVP --> ETL (cron) --> Base de donnees
                                      |
                                      v
                              Moteur d'angles (LLM)
                              "Detecte les faits saillants"
                                      |
                                      v
                              File de validation
                              (interface admin)
                                      |
                                      v (validation humaine)
                              Publication sur le site
```

## Justification des choix

- **SvelteKit** : leger (sobriete numerique), SSR natif (accessibilite, SEO), hydratation progressive
- **FastAPI** : performant, bien type, coherent avec l'ecosysteme existant
- **D3.js** : standard pour les visualisations de donnees complexes
- **SQLite** : simplicite pour le MVP, zero config, backup trivial
- **Docker Compose** : reproductibilite, isolation des services

## Port prevu

| Service | Port |
|---------|------|
| hemicycle (dev) | 8047 |
