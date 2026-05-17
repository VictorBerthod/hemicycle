# Plan de developpement — Hemicycle

## 1. Analyse du besoin

Construire un pipeline de donnees fiable alimentant un site web qui expose les votes
et interets des deputes de l'Assemblee nationale, avec une editorialisation engagee
generee par IA et validee humainement. Le MVP doit permettre de consulter les fiches
deputes, explorer les scrutins, et lire des analyses a angles viraux.

## 2. Architecture confirmee

```
+------------------------------------------------------------------+
|                         FRONTEND                                  |
|  SvelteKit (SSR, port 5173 dev)                                  |
|  Pages : /deputes, /depute/[slug], /scrutins, /scrutin/[id],     |
|          /analyses, /analyse/[slug]                               |
|  Composants D3.js : hemicycle viz, vote breakdown, dissidences   |
+-------------------------------+----------------------------------+
                                | fetch API REST (JSON)
+-------------------------------+----------------------------------+
|                         BACKEND (port 8047)                       |
|  FastAPI                                                         |
|  /api/deputes, /api/deputes/{uid}                                |
|  /api/scrutins, /api/scrutins/{uid}                              |
|  /api/scrutins/{uid}/votes                                       |
|  /api/analyses, /api/analyses/{slug}                             |
|  /api/admin/analyses (CRUD validation)                           |
+-------------------------------+----------------------------------+
                                |
+-------------------------------+----------------------------------+
|                     ETL + DONNEES                                 |
|  SQLite : deputes, groupes, scrutins, votes, declarations,       |
|           analyses (status: draft/published)                      |
|  Scripts : etl/sync_deputes.py, etl/sync_scrutins.py,            |
|            etl/sync_hatvp.py                                     |
|  Sources : NosDéputés.fr API (primaire) + CIVIX API (complement) |
+------------------------------------------------------------------+
```

### Choix de source primaire : NosDéputés.fr

Justification :
- API mature, bien documentee, utilisee depuis 15 ans
- Donnees enrichies (presences, interventions, pas juste les votes)
- Formats multiples (JSON, CSV, XML)
- Fallback CIVIX API pour donnees complementaires
- data.assemblee-nationale.fr pour validation officielle

## 3. Decisions techniques

| Decision | Choix | Justification |
|----------|-------|---------------|
| Source primaire ETL | NosDéputés.fr API | Plus riche, mieux documentee |
| ORM | SQLAlchemy + Alembic | Coherent ecosysteme, migrations |
| Frontend routing | SvelteKit file-based | Convention, SSR gratuit |
| Visualisations | D3.js | Hemicycle SVG, graphes force |
| Generation analyses | Claude API | Meilleur pour du francais editorial |
| Auth admin | Simple token .env | MVP, pas de gestion users |
| Tests | pytest (back) + vitest (front) | Standards ecosysteme |

## 4. Liste de taches numerotees

### Phase 0 — Infrastructure [2 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 0.1 | Structure dossiers backend (FastAPI boilerplate) | 1h | — |
| 0.2 | Docker Compose (backend + frontend) | 2h | 0.1 |
| 0.3 | Schema BDD SQLAlchemy + migration initiale | 2h | 0.1 |
| 0.4 | Structure dossiers frontend (SvelteKit init) | 1h | — |
| 0.5 | CI basique (lint + tests) | 1h | 0.1, 0.4 |

### Phase 1 — Pipeline de donnees [4-5 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 1.1 | Script ETL deputes (NosDéputés.fr -> SQLite) | 3h | 0.3 |
| 1.2 | Script ETL groupes parlementaires | 1h | 0.3 |
| 1.3 | Script ETL scrutins + votes | 4h | 0.3 |
| 1.4 | Script ETL declarations HATVP | 3h | 0.3 |
| 1.5 | Commande CLI sync globale (orchestrateur) | 1h | 1.1-1.4 |
| 1.6 | Tests unitaires pipeline | 2h | 1.1-1.4 |
| 1.7 | Cron job / scheduler pour sync quotidienne | 1h | 1.5 |

### Phase 2 — API Backend [3-4 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 2.1 | Endpoints /api/deputes (liste + detail) | 2h | 1.1 |
| 2.2 | Endpoints /api/scrutins (liste + detail + votes) | 3h | 1.3 |
| 2.3 | Endpoints /api/groupes | 1h | 1.2 |
| 2.4 | Endpoint /api/search (recherche globale) | 2h | 2.1, 2.2 |
| 2.5 | Endpoints /api/analyses (CRUD) | 2h | 0.3 |
| 2.6 | Endpoint /api/stats (metriques globales) | 1h | 1.3 |
| 2.7 | Tests API (pytest + httpx) | 2h | 2.1-2.6 |

### Phase 3 — Frontend socle [5-7 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 3.1 | Layout global (header, nav, footer, dark theme) | 3h | 0.4 |
| 3.2 | Page /deputes (liste filtrable par groupe) | 3h | 2.1 |
| 3.3 | Page /depute/[slug] (fiche complete) | 4h | 2.1 |
| 3.4 | Page /scrutins (liste avec filtres) | 3h | 2.2 |
| 3.5 | Page /scrutin/[id] (detail + votes) | 4h | 2.2 |
| 3.6 | Page /analyses (liste articles) | 2h | 2.5 |
| 3.7 | Page /analyse/[slug] (article complet) | 2h | 2.5 |
| 3.8 | Composant recherche globale | 2h | 2.4 |
| 3.9 | Accessibilite de base (aria, contraste, navigation clavier) | 3h | 3.1-3.7 |

### Phase 4 — Visualisations [4-5 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 4.1 | Composant hemicycle SVG (places colorees par groupe) | 4h | 3.3 |
| 4.2 | Composant vote breakdown (pour/contre/abstention) | 3h | 3.5 |
| 4.3 | Composant dissidences (deputes vs groupe) | 3h | 2.2 |
| 4.4 | Composant timeline votes d'un depute | 3h | 3.3 |
| 4.5 | Responsive + accessibilite des visualisations | 2h | 4.1-4.4 |

### Phase 5 — Module editorial IA [3-4 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 5.1 | Prompt engineering : detection d'angles saillants | 3h | 1.3 |
| 5.2 | Script generation d'analyses (batch) | 3h | 5.1 |
| 5.3 | Interface admin validation (approve/reject/edit) | 4h | 2.5 |
| 5.4 | Publication automatique post-validation | 1h | 5.3 |
| 5.5 | Tests du pipeline editorial | 2h | 5.1-5.4 |

### Phase 6 — Polish et lancement [3 jours]

| # | Tache | Estimation | Dependances |
|---|-------|------------|-------------|
| 6.1 | SEO (meta tags, OG images, sitemap) | 2h | 3.1-3.7 |
| 6.2 | Audit accessibilite RGAA | 3h | 3.9 |
| 6.3 | Optimisation performances (cache, lazy load) | 2h | Tous |
| 6.4 | Deploiement production | 3h | Tous |
| 6.5 | Monitoring + alertes pipeline | 1h | 1.7 |

---

## 5. User Stories detaillees

---

**US-01 : Synchroniser les deputes depuis l'API**
> En tant que systeme, je veux recuperer automatiquement la liste des deputes en mandat
> afin de disposer de donnees a jour sans intervention manuelle.

**Conditions de succes :**
- [ ] Tous les deputes en mandat de la 17e legislature sont presents en base
- [ ] Les donnees incluent : nom, prenom, groupe, circo, photo_url, date_mandat
- [ ] La sync s'execute en moins de 60 secondes
- [ ] En cas d'API indisponible, les donnees existantes sont preservees (pas d'ecrasement)

**Criteres de validation Pablo :**
- [ ] Script `etl/sync_deputes.py` executable en CLI
- [ ] Upsert (insert or update) — pas de doublons
- [ ] Logging des ajouts/modifications/erreurs
- [ ] Source et timestamp stockes sur chaque enregistrement

**Tests attendus :**
- test_sync_deputes_creates_records() — verifie insertion depuis mock API
- test_sync_deputes_updates_existing() — verifie mise a jour sans doublon
- test_sync_deputes_api_failure() — verifie que la base n'est pas corrompue

---

**US-02 : Synchroniser les scrutins et votes**
> En tant que systeme, je veux recuperer tous les scrutins publics et le detail des votes
> afin de pouvoir afficher qui a vote quoi sur chaque texte.

**Conditions de succes :**
- [ ] Tous les scrutins de la legislature courante sont indexes
- [ ] Pour chaque scrutin : titre, date, resultat (adopte/rejete), nombre pour/contre/abstention
- [ ] Pour chaque vote : depute_uid + position (pour/contre/abstention/absent)
- [ ] Sync incrementale (ne re-telecharge pas ce qui est deja en base)

**Criteres de validation Pablo :**
- [ ] Script `etl/sync_scrutins.py` avec mode incremental (par date)
- [ ] Relations FK : votes -> scrutins, votes -> deputes
- [ ] Gestion des scrutins sans detail de vote (scrutins a main levee exclus)

**Tests attendus :**
- test_sync_scrutins_incremental() — ne re-traite pas les scrutins existants
- test_vote_positions_complete() — chaque scrutin a nb_votants positions
- test_scrutin_without_detail_skipped() — pas d'erreur sur scrutins incomplets

---

**US-03 : Consulter la fiche d'un depute**
> En tant que citoyen, je veux consulter la fiche d'un depute
> afin de voir son profil, son groupe, et ses votes cles d'un coup d'oeil.

**Conditions de succes :**
- [ ] La page affiche : photo, nom, groupe, circonscription, date debut mandat
- [ ] Les 10 derniers votes du depute sont affiches avec leur intitule
- [ ] Un lien vers la source officielle (AN) est present
- [ ] La page charge en moins de 2s sur connexion 3G
- [ ] Accessible au clavier et compatible lecteur d'ecran

**Criteres de validation Pablo :**
- [ ] Route SvelteKit `/depute/[slug]` avec SSR
- [ ] Appel API backend `/api/deputes/{uid}` inclut votes recents
- [ ] Balises meta OG pour partage social

**Tests attendus :**
- test_depute_page_renders() — page retourne 200 avec contenu attendu
- test_depute_not_found_404() — slug inexistant retourne 404 propre
- test_depute_votes_included() — response API inclut liste votes

---

**US-04 : Explorer les scrutins publics**
> En tant que citoyen, je veux parcourir la liste des scrutins
> afin de decouvrir sur quoi l'Assemblee a vote recemment.

**Conditions de succes :**
- [ ] Liste paginee (20 par page) triee par date decroissante
- [ ] Chaque scrutin affiche : date, titre, resultat (adopte/rejete), repartition visuelle
- [ ] Filtres disponibles : par date, par resultat, par theme (si disponible)
- [ ] Clic sur un scrutin mene au detail avec votes par depute

**Criteres de validation Pablo :**
- [ ] Route `/scrutins` avec pagination cote serveur
- [ ] Endpoint `/api/scrutins?page=X&limit=20&sort=-date`
- [ ] Composant barre de repartition (pour/contre/abstention) en SVG accessible

**Tests attendus :**
- test_scrutins_list_paginated() — retourne 20 items max, total count en header
- test_scrutins_filter_by_date() — filtre fonctionne correctement
- test_scrutin_detail_has_votes() — page detail inclut breakdown complet

---

**US-05 : Visualiser les dissidences d'un depute par rapport a son groupe**
> En tant que citoyen, je veux voir quand un depute vote differemment de son groupe
> afin d'identifier les personnalites independantes ou les votes controverses.

**Conditions de succes :**
- [ ] Sur la fiche depute, un indicateur "taux de dissidence" est affiche
- [ ] Liste des scrutins ou le depute a vote contre la majorite de son groupe
- [ ] Visuel clair distinguant votes conformes vs dissidents
- [ ] Pas de jugement de valeur ("dissidence" est neutre dans l'interface)

**Criteres de validation Pablo :**
- [ ] Calcul dissidence : position_depute != position_majoritaire_groupe
- [ ] Endpoint `/api/deputes/{uid}/dissidences`
- [ ] Composant frontend timeline dissidences (D3.js)

**Tests attendus :**
- test_dissidence_calculation() — calcul correct sur donnees connues
- test_depute_100pct_conforme() — taux 0% si toujours avec son groupe
- test_depute_sans_groupe_excluded() — non-inscrits exclus du calcul

---

**US-06 : Generer une analyse editoriale par IA**
> En tant qu'editeur, je veux que le systeme genere automatiquement des analyses
> a partir des donnees de vote afin de disposer de brouillons prets a valider.

**Conditions de succes :**
- [ ] Le systeme produit un brouillon avec : titre accrocheur, chapeau, corps, sources
- [ ] Le ton est engagee (angles type "qui a trahi", "qui a vote contre les gens")
- [ ] Chaque affirmation est liee a un scrutin/vote verifiable
- [ ] L'analyse est stockee en statut "draft" jusqu'a validation humaine

**Criteres de validation Pablo :**
- [ ] Script `editorial/generate_analysis.py` avec prompt systeme editorial
- [ ] Stockage en base : titre, body_md, sources[], status, created_at
- [ ] Le prompt inclut les donnees de vote en contexte (pas d'hallucination)
- [ ] Rate limiting sur appels API Claude

**Tests attendus :**
- test_analysis_generated_with_sources() — output contient references scrutins
- test_analysis_stored_as_draft() — statut initial toujours "draft"
- test_analysis_prompt_includes_data() — prompt contient donnees reelles

---

**US-07 : Valider et publier une analyse**
> En tant qu'editeur, je veux relire, modifier et publier une analyse generee
> afin de garantir la qualite editoriale avant mise en ligne.

**Conditions de succes :**
- [ ] Interface admin listant les analyses en draft
- [ ] Possibilite d'editer titre et corps avant publication
- [ ] Bouton "publier" qui passe le statut a "published"
- [ ] L'analyse publiee apparait immediatement sur le site public

**Criteres de validation Pablo :**
- [ ] Route admin protegee par token
- [ ] Endpoint PATCH `/api/admin/analyses/{id}` (edit + publish)
- [ ] Historique des modifications (updated_at)

**Tests attendus :**
- test_publish_analysis() — statut passe a published, visible en API publique
- test_edit_preserves_sources() — modification du texte ne casse pas les liens
- test_unauthorized_rejected() — sans token, 401

---

**US-08 : Integrer les declarations d'interets HATVP**
> En tant que citoyen, je veux voir les declarations d'interets des deputes
> afin de connaitre leurs activites annexes et potentiels conflits d'interets.

**Conditions de succes :**
- [ ] Sur la fiche depute, section "interets declares" avec activites/mandats/participations
- [ ] Lien vers la declaration complete sur hatvp.fr
- [ ] Date de la derniere declaration affichee
- [ ] Si pas de declaration trouvee, mention explicite "non disponible"

**Criteres de validation Pablo :**
- [ ] Script `etl/sync_hatvp.py` parsant l'open data HATVP
- [ ] Matching depute AN <-> declarant HATVP (par nom + prenom, tolerance accents)
- [ ] Stockage normalise : type_interet, description, organisme

**Tests attendus :**
- test_hatvp_matching_depute() — liaison correcte malgre variantes noms
- test_hatvp_no_match_graceful() — pas d'erreur si depute absent HATVP
- test_hatvp_data_structure() — champs obligatoires presents

---

## 6. Risques specifiques au developpement

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|------------|
| API NosDéputés.fr indisponible/deprecated | Faible | Fort | Fallback CIVIX, cache local, monitoring |
| Matching HATVP imparfait (homonymes) | Moyenne | Moyen | Matching par uid AN si disponible, sinon fuzzy + validation manuelle |
| Scraping trop agressif = ban IP | Faible | Moyen | Rate limiting, headers polis, cache agressif |
| Hallucinations LLM dans analyses | Haute | Critique | Prompt contraint aux donnees fournies, validation humaine obligatoire |
| Volume de scrutins trop important pour SQLite | Faible | Faible | ~1000 scrutins/legislature = trivial pour SQLite |
| SvelteKit + D3.js integration complexe | Moyenne | Moyen | Composants D3 isoles, rendu client-only pour viz |
| Temps de dev sous-estime (frontend viz) | Haute | Moyen | Commencer par viz simples (barres), hemicycle en P2 |

---

## 7. Ordre d'execution recommande

```
Semaine 1 : Phase 0 (setup) + Phase 1 (ETL)
            → A la fin : base remplie, donnees exploitables

Semaine 2 : Phase 2 (API backend)
            → A la fin : API fonctionnelle, testable via curl

Semaine 3-4 : Phase 3 (frontend socle)
              → A la fin : site navigable, fiches consultables

Semaine 4-5 : Phase 4 (visualisations) + Phase 5 (editorial IA)
              → A la fin : site complet avec visuels et analyses

Semaine 6 : Phase 6 (polish + deploiement)
            → A la fin : MVP en production
```

**Point de controle critique : fin de semaine 1.**
Si le pipeline est solide et la base remplie, tout le reste suit naturellement.
Si les APIs posent probleme, on ajuste avant d'investir dans le front.

---

## 8. Premiere tache pour Pablo

Commencer par **US-01 + US-02** (Phase 1) :
1. Creer la structure backend (`backend/`, FastAPI, SQLAlchemy, schema)
2. Implementer `etl/sync_deputes.py`
3. Implementer `etl/sync_scrutins.py`
4. Valider avec tests

C'est le socle de tout. Pas de front sans data.
