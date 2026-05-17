# Whitepaper — Détection d'incohérences entre votes parlementaires et prises de parole publiques

## Projet de transparence démocratique appliqué à la vie politique française

*Document de cadrage — Version 0.1*

---

## 1. Résumé exécutif

Ce projet vise à construire un outil capable de **détecter et documenter les incohérences entre les votes parlementaires et les prises de parole publiques** des figures politiques majeures françaises (ministres, présidents de groupe, candidats à la présidentielle, présidents de partis).

L'enjeu n'est pas de produire un classement moralisateur, mais de fournir une base de données factuelle, sourcée et nuancée, permettant aux citoyens, journalistes et chercheurs de confronter le discours public à l'acte législatif.

Le projet exploite l'écosystème open data français (Assemblée nationale, Sénat, Vie-publique.fr) et propose un croisement systématique entre trois niveaux d'analyse : individuel, groupe parlementaire, et parti politique.

---

## 2. Contexte et motivation

### 2.1 Le constat

Le discours politique et l'acte législatif sont rarement confrontés de manière systématique. Un responsable politique peut tenir un discours médiatique sur une thématique tout en votant — ou en faisant voter son groupe — dans un sens contraire, sans que cette divergence ne soit nécessairement portée à l'attention du public.

Les outils existants (NosDéputés.fr, Datan.fr, CIVIX) documentent remarquablement les votes, mais ne les confrontent pas systématiquement aux prises de parole hors hémicycle.

### 2.2 La promesse

Offrir un outil qui réponde, pour une figure politique donnée et une thématique donnée, à la question : **« Ce qu'elle dit publiquement est-il cohérent avec ce qu'elle vote ? »**

### 2.3 Ce que le projet n'est pas

- Un tribunal moral : une incohérence apparente peut avoir une justification légitime (discipline de groupe, évolution de position, contexte procédural).
- Un outil partisan : la méthodologie doit s'appliquer identiquement à toutes les sensibilités politiques.
- Un fact-checker : on ne vérifie pas la véracité des affirmations factuelles, on confronte des positions à des actes.

---

## 3. Périmètre

### 3.1 Périmètre institutionnel

- **Parlement français** : Assemblée nationale et Sénat
- **Gouvernement** : ministres en exercice
- **Vie partisane** : présidents de partis, candidats à la présidentielle

### 3.2 Périmètre humain

Approximativement **50 à 80 personnalités** simultanément suivies :

- ~30-40 membres du gouvernement
- ~15 présidents et co-présidents de groupes parlementaires (AN + Sénat)
- ~10-15 candidats déclarés ou pressentis à la présidentielle
- Quelques présidents de partis non couverts par les catégories ci-dessus

### 3.3 Périmètre thématique (MVP)

Pour le démarrage, le projet se concentre sur **une thématique clivante** (à choisir : immigration, fiscalité, climat, ou retraites) afin de valider la pipeline complète avant élargissement.

### 3.4 Périmètre temporel

Législature en cours (17e législature ouverte en 2024) avec capacité d'extension rétrospective sur les législatures précédentes.

---

## 4. Sources de données

### 4.1 Couche 1 — Votes et activité parlementaire

#### Sources primaires (officielles)

| Source | Contenu | Format | Fréquence |
|--------|---------|--------|-----------|
| data.assemblee-nationale.fr | Scrutins, amendements, organes, acteurs, comptes rendus | XML / JSON | Quotidienne |
| data.senat.fr | Scrutins publics, sénateurs, amendements | XML / JSON | Quotidienne |
| Vie-publique.fr | Discours officiels du gouvernement | HTML (scraping) | Quotidienne |

#### Sources secondaires (réutilisateurs)

| Source | Apport | Statut |
|--------|--------|--------|
| Datan.fr | Données restructurées + scores calculés (loyauté, cohésion, participation) | Actif, mis à jour |
| NosDéputés.fr / NosSénateurs.fr (Regards Citoyens) | API XML/JSON, indexation textuelle | Actif via ParlAPI.fr |
| CIVIX (data.gouv.fr) | CSV restructurés | Actif (mises à jour 2026) |

#### Types de décisions parlementaires obtenables

- **Scrutins publics solennels** : votes nominatifs sur l'ensemble d'un texte. **Qualité : excellente.** Source principale pour le MVP.
- **Scrutins ordinaires (votes électroniques)** : votes nominatifs sur amendements. **Qualité : très bonne.**
- **Votes en commission** : partiellement disponibles nominativement, publication non systématique. **Qualité : variable.**
- **Votes à main levée** : **non obtenables nominativement** (limite structurelle).
- **Co-signatures d'amendements et de propositions de loi** : signal politique fort, obtenable.
- **Questions écrites et orales au gouvernement** : utiles pour identifier les préoccupations affichées.

### 4.2 Couche 2 — Prises de parole publiques

| Source | Contenu | Structuration | Difficulté technique |
|--------|---------|---------------|----------------------|
| Comptes rendus parlementaires (AN/Sénat) | Interventions en séance | Très structurée | Faible |
| Vie-publique.fr | Discours officiels gouvernement | Structurée | Faible |
| Élysée.fr | Discours présidentiels | Structurée | Faible |
| X / Twitter (comptes officiels) | Posts politiques | Semi-structurée | Moyenne (API payante) |
| Sites des partis | Communiqués, programmes | Hétérogène | Moyenne (scraping) |
| INA | Archives audiovisuelles | Partiellement structurée | Élevée |
| Médias TV/radio (France Inter, RTL, etc.) | Interviews | Hétérogène | Élevée (transcription) |
| Presse écrite | Tribunes, interviews | Souvent paywall | Élevée |

#### Approche recommandée pour les sources non structurées

Utilisation de transcription automatique (type Whisper) pour les contenus audiovisuels, combinée à une revue humaine pour les figures les plus suivies. La limitation du périmètre à 50-80 personnes rend cette approche tractable.

### 4.3 Couche 3 — Données contextuelles

- **Composition des groupes parlementaires** (jeu « Organes » de l'AN, équivalent Sénat) — essentielle car la composition évolue en cours de législature.
- **Programmes électoraux** des candidats et partis (présidentielle, législatives, européennes).
- **Communiqués officiels des partis et groupes parlementaires.**

---

## 5. Architecture des données

### 5.1 Modèle hiérarchique à trois niveaux

Le projet adopte une structure à trois niveaux d'analyse imbriqués :

#### Niveau 1 — Individuel

- Votes nominatifs
- Co-signatures d'amendements et de PPL
- Interventions personnelles en séance
- Déclarations publiques personnelles (interviews, posts, tribunes)

#### Niveau 2 — Groupe parlementaire

- Ligne de vote dominante (position majoritaire des membres)
- Consigne de vote officielle déclarée
- Cohésion (% de membres ayant suivi la ligne)
- Communiqués officiels du groupe

#### Niveau 3 — Parti politique

- Programme électoral
- Communication officielle (réseaux sociaux, communiqués)
- Motions de congrès
- Prises de position du président de parti

### 5.2 Distinction essentielle : parti ≠ groupe parlementaire

Le parti politique est une organisation extra-parlementaire sans existence officielle dans l'hémicycle. Le groupe parlementaire est l'unité institutionnelle de vote. Un groupe peut rassembler plusieurs partis, et inversement. **L'analyse doit toujours distinguer ces deux niveaux.**

### 5.3 Schéma entités-relations (vue conceptuelle)

```
PERSONNE ──── appartient à ────▶ GROUPE_PARLEMENTAIRE
   │                                   │
   │                                   │ affilié à
   │                                   ▼
   │                              PARTI
   │
   ├─── émet ────▶ PRISE_DE_PAROLE ──── porte sur ────▶ THÉMATIQUE
   │
   └─── vote sur ────▶ SCRUTIN ──── concerne ────▶ TEXTE_LÉGISLATIF
                          │                              │
                          └─── associé à ────────────────┘
                                                          │
                                                          ▼
                                                     THÉMATIQUE
```

Une **incohérence détectée** est un objet relationnel reliant au moins une `PRISE_DE_PAROLE` et un `SCRUTIN` (ou `CO_SIGNATURE`) portant sur la même `THÉMATIQUE` mais exprimant des positions divergentes.

---

## 6. Méthodologie de détection d'incohérences

### 6.1 Pipeline de traitement

1. **Collecte** : ingestion des votes, signatures, et prises de parole.
2. **Classification thématique** : tag de chaque vote et chaque déclaration sur une taxonomie de thématiques (fiscalité, immigration, climat, etc.). Modèle envisagé : CamemBERT fine-tuné, ou appel LLM avec taxonomie fixe.
3. **Extraction de position** : identification de la prise de position (pour / contre / nuancée) sur la mesure concernée. Étape la plus difficile techniquement.
4. **Mise en correspondance** : appariement d'un vote et d'une (ou plusieurs) déclaration(s) sur la même thématique dans une fenêtre temporelle pertinente.
5. **Évaluation** : qualification de l'incohérence apparente (forte / nuancée / explicable par le contexte).
6. **Restitution** : présentation contextualisée à l'utilisateur final, avec sources cliquables.

### 6.2 Typologie des incohérences détectables

| Type | Description | Exemple |
|------|-------------|---------|
| Individuelle directe | Discours d'un élu / son propre vote | Un député déclare défendre X et vote contre X |
| Individuelle / groupe | Discours d'un président de parti / vote de son groupe | Un président de parti défend X, son groupe vote contre |
| Programme / vote | Programme électoral / votes effectifs | Engagement de campagne contredit en législature |
| Consigne / vote effectif | Consigne du groupe / vote réel des membres | Fracture interne mise en évidence |
| Co-signature / discours | Amendement co-signé / discours postérieur | Un élu co-signe un amendement durcissant X, puis critique cette mesure |

### 6.3 Faux positifs à filtrer impérativement

La crédibilité du projet dépend du traitement rigoureux des cas suivants :

- **Discipline de groupe** : un vote « contraint » par la ligne ne reflète pas nécessairement la position personnelle. Le score de loyauté (Datan) permet de pondérer.
- **Vote sur amendement vs vote sur texte** : voter contre un amendement « trop faible » n'est pas voter contre le principe défendu.
- **Vote bloqué, 49.3, vote de confiance** : sens procédural, pas substantiel.
- **Évolution légitime dans le temps** : un changement d'avis sur plusieurs années n'est pas une incohérence en soi.
- **Nuance et contexte** : une déclaration peut être conditionnelle, ironique ou mal extraite.

### 6.4 Principe de présentation

Chaque incohérence affichée doit être :

- **Sourcée** : lien direct vers le scrutin officiel et la déclaration originale.
- **Contextualisée** : indication du type de scrutin, de la ligne de groupe, du score de loyauté.
- **Datée** : timeline visible pour permettre l'appréciation d'une éventuelle évolution.
- **Réfutable** : possibilité pour la personne concernée de contribuer une réponse ou un contexte.

---

## 7. Stack technique envisagée

### 7.1 Ingestion et stockage

- **Ingestion** : scripts Python orchestrés (Airflow ou alternative légère type Prefect).
- **Stockage brut** : data lake (fichiers JSON/XML horodatés).
- **Stockage structuré** : base relationnelle (PostgreSQL) pour les entités principales, avec extensions full-text search.
- **Stockage vectoriel** : pour la recherche sémantique sur prises de parole (pgvector ou base dédiée).

### 7.2 Traitement NLP

- Modèle de classification thématique fine-tuné sur corpus français (CamemBERT, ou DistilCamemBERT pour la vitesse).
- Extraction de positions via LLM avec prompt structuré (sortie JSON).
- Transcription audio via Whisper pour les contenus médiatiques.

### 7.3 Restitution

- Interface web (Next.js ou équivalent).
- Visualisations interactives (timeline, fiches personnelles, comparateurs).
- API publique en lecture (réutilisation par tiers encouragée, conformément à l'esprit open data).

---

## 8. Feuille de route

### 8.1 Phase 1 — MVP exploratoire (semaines 1-4)

- Choix d'**une personnalité** et d'**une thématique** test.
- Récupération manuelle de 20 votes et 20 prises de parole pertinents.
- Construction manuelle du tableau de correspondance.
- Définition empirique du critère « incohérence ».

### 8.2 Phase 2 — Pipeline automatisée (semaines 5-12)

- Ingestion automatique des datasets AN + Sénat + Datan.
- Pipeline de classification thématique sur les votes.
- Extension à 5-10 personnalités sur la thématique cible.

### 8.3 Phase 3 — Extension du périmètre (mois 4-6)

- Couverture des 50-80 personnalités cibles.
- Ajout de 2-3 thématiques supplémentaires.
- Intégration des co-signatures d'amendements.

### 8.4 Phase 4 — Restitution publique (mois 7-9)

- Interface web publique.
- Mécanisme de contribution / contestation par les personnes concernées.
- API ouverte.

---

## 9. Risques et limites

### 9.1 Risques techniques

- **Hétérogénéité des sources de parole** : les transcriptions et scrapings sont fragiles. Risque de citations tronquées ou décontextualisées.
- **Classification thématique imparfaite** : les modèles NLP commettent des erreurs sur les sujets ambigus ou nouveaux.
- **Extraction de position erronée** : l'ironie, la conditionnalité et la rhétorique politique compliquent l'extraction automatisée.

### 9.2 Risques juridiques et éthiques

- **Diffamation** : qualifier publiquement une personne d'« incohérente » sur la base d'une erreur d'analyse peut être attaquable. Le ton et le vocabulaire de l'interface doivent être factuels (« position A en mars / vote B en juin ») et non interprétatifs.
- **Droit à l'image et à la parole** : la réutilisation de citations doit respecter le cadre légal (courte citation, source identifiée, finalité d'information).
- **RGPD** : les données concernent des personnalités publiques dans l'exercice de leur fonction publique, ce qui relève largement de l'intérêt légitime, mais un cadre formalisé est nécessaire.

### 9.3 Risques politiques

- **Accusation de partialité** : tout outil de ce type sera scruté. La méthodologie doit être documentée publiquement, le code ouvert, et l'application symétrique à toutes les sensibilités.
- **Récupération polémique** : des cas isolés peuvent être instrumentalisés. La présentation doit toujours fournir le contexte.

### 9.4 Limites assumées

- Aucune donnée sur les votes à main levée.
- Couverture des prises de parole nécessairement incomplète (impossible de tout transcrire).
- Les ministres non parlementaires ne sont pas analysables sur l'axe « vote personnel » — seulement via leur groupe d'origine.

---

## 10. Gouvernance et ouverture

### 10.1 Principes

- **Code source ouvert** : publication sur dépôt public (licence libre).
- **Données ouvertes** : republication des données dérivées sous licence ouverte, conformément aux licences amont.
- **Méthodologie publique** : documentation accessible de tous les choix de classification et de détection.
- **Droit de réponse** : mécanisme pour que les personnes concernées contribuent un contexte ou une réfutation.

### 10.2 Indépendance

Le projet doit afficher une indépendance politique stricte. Pas de financement par un parti ou un mouvement politique. Modèles possibles : association loi 1901, structure adossée à une rédaction journalistique, ou projet académique.

---

## 11. Prochaines étapes immédiates

1. **Choisir la personnalité et la thématique du MVP.**
2. **Réaliser l'exercice manuel** sur 20 votes et 20 prises de parole, pour valider que la notion d'« incohérence » se laisse opérationnaliser de manière reproductible.
3. **Définir la taxonomie thématique** initiale (5-10 grandes catégories).
4. **Prototyper la pipeline d'ingestion** sur les datasets AN.
5. **Engager une discussion avec Regards Citoyens et Datan** pour identifier les complémentarités plutôt que les doublons.

---

*Document de travail. Version 0.1 — À itérer.*
