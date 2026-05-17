# Sources de donnees

## MVP — Assemblee nationale uniquement

| Source | Donnees | Format | Fiabilite | URL |
|--------|---------|--------|-----------|-----|
| data.assemblee-nationale.fr | Deputes, organes, scrutins, amendements | API REST JSON/XML | Officielle | https://data.assemblee-nationale.fr |
| HATVP open data | Declarations d'interets et activites | CSV/JSON | Officielle | https://www.hatvp.fr/open-data/ |
| NosDéputés.fr (Regards Citoyens) | Donnees enrichies, presences, interventions | API JSON | Associative fiable | https://www.nosdeputes.fr/api |
| Legifrance API (DILA) | Textes de loi references dans les votes | API REST | Officielle | https://api.legifrance.gouv.fr |

## Perimeter etendu (post-MVP)

| Source | Donnees | Priorite |
|--------|---------|----------|
| data.senat.fr | Senateurs, travaux | P2 |
| EUR-Lex | Directives europeennes | P3 |
| Registre des lobbys (HATVP) | Representants d'interets | P2 |
| OpenCorporates | Liens avec entreprises | P3 |

## Principes de gestion des donnees

1. **Tracabilite** : chaque donnee stocke la source + date de collecte
2. **Fraicheur** : sync quotidienne via cron pour les APIs principales
3. **Cache** : donnees peu volatiles cachees agressivement
4. **Fallback** : si API AN indisponible, fallback sur NosDéputés.fr
5. **Versioning** : historique des changements dans les donnees (soft delete, timestamps)
