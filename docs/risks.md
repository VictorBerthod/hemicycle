# Risques identifies

## Matrice des risques

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|------------|
| Accusation de manipulation (ligne engagee + donnees) | Haute | Fort | Sourcing irreprochable, separation claire donnees/editorial, methodologie publique |
| Diffamation (erreur dans une fiche depute) | Moyenne | Critique | Donnees 100% issues d'API officielles, pas de saisie manuelle, mentions legales |
| Proces-baillon (pression juridique d'un elu) | Moyenne | Fort | Assurance juridique, statut associatif, tout est donnee publique |
| Biais de confirmation (LLM amplifie un biais) | Haute | Fort | Prompt engineering rigoureux, validation humaine obligatoire, diversite relecteurs |
| API AN indisponible/changee | Faible | Moyen | Cache local complet, monitoring, fallback NosDéputés.fr |
| Burnout editorial (validation humaine = goulot) | Moyenne | Moyen | Prioriser qualite sur quantite, automatiser le maximum |
| Recuperation politique (un parti s'approprie le site) | Moyenne | Fort | Charte d'independance publique, refus financement partisan |
| RGPD (donnees personnelles deputees) | Faible | Moyen | Uniquement donnees publiques liees a la fonction, pas de vie privee |

## Parties prenantes a mobiliser

| Role | Pourquoi | Quand |
|------|----------|-------|
| Juriste droit de la presse | Valider legalite des publications | Avant publication |
| Designer UX/accessibilite | Garantir RGAA AA, tests publics non-experts | J3-J4 |
| Politologue / fact-checker | Valider methodologie d'analyse | J5 |
| Community manager | Strategie virale, ton des titres, reseaux sociaux | Pre-lancement |
| Beta-testeurs non-experts | Verifier comprehension reelle | J7 |

## Questions ouvertes

1. Hebergement prod : VPS (Hetzner/OVH) ou autre ?
2. Qui valide les analyses au debut ? Solo ou comite ?
3. Strategie d'acquisition : reseaux sociaux cibles ?
4. Statut juridique : association loi 1901 ? Media en ligne ?
5. Nom definitif du projet ?
