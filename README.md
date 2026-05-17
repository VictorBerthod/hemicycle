# hemicycle

> Site web éducatif rendant lisibles les structures et mouvements de pouvoir à l'Assemblée nationale française.

Un outil de transparence démocratique, sourcé et nuancé, qui s'adresse aux citoyens, journalistes et chercheurs souhaitant confronter le discours politique à l'acte législatif.

> ⚠️ **Projet en phase exploratoire (v0.1).** L'API, la base de données et l'interface sont en cours de construction. Les choix techniques peuvent encore évoluer.

---

## Objectif

`hemicycle` exploite l'écosystème open data français (Assemblée nationale, Sénat, HATVP, Vie-publique.fr, NosDéputés.fr) pour cartographier la vie parlementaire selon trois niveaux d'analyse imbriqués :

- **Individuel** — votes nominatifs, co-signatures d'amendements, interventions en séance, déclarations publiques.
- **Groupe parlementaire** — ligne de vote dominante, cohésion, communiqués officiels.
- **Parti politique** — programme électoral, communication publique, prises de position.

Le cas d'usage phare est la **détection d'incohérences entre votes parlementaires et prises de parole publiques** d'environ 50 à 80 personnalités politiques majeures (membres du gouvernement, présidents de groupes, candidats à la présidentielle, présidents de partis). La méthodologie complète est documentée dans le [whitepaper](./docs/).

### Ce que le projet n'est pas

- Un tribunal moral — une divergence apparente peut avoir une justification légitime (discipline de groupe, évolution de position, contexte procédural).
- Un outil partisan — la méthodologie s'applique identiquement à toutes les sensibilités politiques.
- Un fact-checker — on ne vérifie pas la véracité d'affirmations factuelles, on confronte des positions à des actes.

---

## Stack

| Couche       | Technologie                            |
| ------------ | -------------------------------------- |
| Backend      | Python + FastAPI + SQLite              |
| Frontend     | SvelteKit + D3.js *(à venir)*          |
| Données      | API Assemblée nationale, HATVP, NosDéputés.fr |
| Infra        | Docker Compose                         |

Le backend expose une API REST sur le port `8047`. Le schéma de données suit le modèle hiérarchique `Personne → Groupe parlementaire → Parti`, avec des entités dédiées aux scrutins, textes législatifs et prises de parole.

---

## Démarrage rapide

Prérequis : Docker et Docker Compose installés.

```bash
git clone https://github.com/VictorBerthod/hemicycle.git
cd hemicycle
docker compose up -d
```

Le backend est accessible sur `http://localhost:8047`. La documentation OpenAPI auto-générée par FastAPI se trouve sur `http://localhost:8047/docs`.

Pour arrêter les services :

```bash
docker compose down
```

---

## Structure du dépôt

```
hemicycle/
├── backend/              # API FastAPI, modèles SQLite, scripts d'ingestion
├── docs/                 # Whitepaper, méthodologie, taxonomie thématique
├── docker-compose.yml    # Orchestration des services
└── README.md
```

---

## Sources de données

### Officielles

- **[data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/)** — scrutins, amendements, organes, acteurs (XML/JSON, mise à jour quotidienne).
- **[data.senat.fr](https://data.senat.fr/)** — scrutins publics, sénateurs, amendements.
- **[hatvp.fr](https://www.hatvp.fr/)** — déclarations d'intérêts et de patrimoine.
- **[vie-publique.fr](https://www.vie-publique.fr/)** — discours officiels du gouvernement.

### Réutilisateurs

- **[NosDéputés.fr](https://www.nosdeputes.fr/) / [NosSénateurs.fr](https://www.nossenateurs.fr/)** (Regards Citoyens) — données indexées, API publique.
- **[Datan.fr](https://datan.fr/)** — scores calculés (loyauté, cohésion, participation).
- **[CIVIX](https://www.data.gouv.fr/)** — datasets CSV restructurés.

### Limites de couverture

- Les **votes à main levée** ne sont pas obtenables nominativement (limite structurelle).
- Les **votes en commission** sont partiellement disponibles.
- Les **ministres non parlementaires** ne sont analysables que via leur groupe d'origine.

---

## Méthodologie (résumé)

Le pipeline de détection d'incohérences suit six étapes :

1. **Collecte** — ingestion des votes, signatures et prises de parole.
2. **Classification thématique** — tagging sur une taxonomie fermée (fiscalité, immigration, climat, retraites, etc.).
3. **Extraction de position** — pour / contre / nuancée, par LLM ou modèle fine-tuné.
4. **Mise en correspondance** — appariement vote ↔ déclaration sur même thématique dans une fenêtre temporelle pertinente.
5. **Évaluation** — qualification de l'incohérence (forte / nuancée / explicable).
6. **Restitution** — présentation contextualisée, sourcée, datée et réfutable.

Chaque incohérence affichée doit être **sourcée** (lien vers le scrutin et la déclaration originale), **contextualisée** (type de scrutin, ligne de groupe, score de loyauté), **datée** et **réfutable** (mécanisme de droit de réponse pour les personnes concernées).

Le détail de la méthodologie, des faux positifs filtrés et de la typologie des incohérences se trouve dans le [whitepaper](./docs/).

---

## Feuille de route

- [ ] **Phase 1 — MVP exploratoire** : une personnalité, une thématique, exercice manuel sur 20 votes et 20 prises de parole.
- [ ] **Phase 2 — Pipeline automatisée** : ingestion AN + Sénat + Datan, classification thématique, extension à 5–10 personnalités.
- [ ] **Phase 3 — Extension du périmètre** : 50–80 personnalités, 2–3 thématiques supplémentaires, co-signatures d'amendements.
- [ ] **Phase 4 — Restitution publique** : interface SvelteKit, API ouverte, mécanisme de contribution.

---

## Principes éthiques et gouvernance

- **Code source ouvert** — toute la base de code est publiée sous licence libre.
- **Données ouvertes** — les données dérivées sont republiées sous licence ouverte, dans le respect des licences amont.
- **Méthodologie publique** — tous les choix de classification et de détection sont documentés.
- **Symétrie politique** — la méthodologie s'applique identiquement à toutes les sensibilités.
- **Droit de réponse** — les personnes concernées peuvent contribuer un contexte ou une réfutation.
- **Indépendance** — pas de financement par un parti ou un mouvement politique.

Le ton de l'interface doit rester factuel (« position A en mars / vote B en juin ») et non interprétatif, afin d'éviter toute qualification diffamatoire.

---

## Contribuer

Le projet est en phase exploratoire ; les contributions, retours méthodologiques et signalements d'erreurs sont les bienvenus via les [issues](https://github.com/VictorBerthod/hemicycle/issues).

Pour proposer une modification : fork → branche dédiée → pull request avec description claire de la motivation.

---

## Licence

À définir. Une licence libre compatible avec les licences des sources amont (Etalab 2.0, ODbL) sera retenue.

---

## Remerciements

Ce projet s'inscrit dans la continuité du travail des communautés open data françaises, notamment **Regards Citoyens** (NosDéputés.fr, NosSénateurs.fr) et **Datan**, sans lesquels la donnée parlementaire française ne serait pas accessible dans cette qualité.
