"""Seed editorial data: ecarts and themes for development."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Ecart, Theme


def seed_themes(db):
    if db.query(Theme).count() > 0:
        print("Themes already seeded, skipping.")
        return

    themes = [
        Theme(slug="fiscalite",     nom="Fiscalité",           description="Impôts, taxes, niches fiscales, patrimoine.", nb_scrutins=48),
        Theme(slug="climat",        nom="Climat · énergie",    description="Transition énergétique, planification écologique.", nb_scrutins=36),
        Theme(slug="libertes",      nom="Libertés publiques",  description="Droits fondamentaux, surveillance, justice.", nb_scrutins=29),
        Theme(slug="social",        nom="Social · travail",    description="Retraites, droit du travail, protection sociale.", nb_scrutins=42),
        Theme(slug="logement",      nom="Logement",            description="Accès au logement, politique urbaine.", nb_scrutins=14),
        Theme(slug="sante",         nom="Santé",               description="Système de soins, médicaments, santé publique.", nb_scrutins=22),
        Theme(slug="justice",       nom="Justice",             description="Organisation judiciaire, pénal, civil.", nb_scrutins=18),
        Theme(slug="international", nom="International",       description="Traités, accords commerciaux, diplomatie.", nb_scrutins=31),
        Theme(slug="institutions",  nom="Institutions",        description="Constitution, Parlement, élections.", nb_scrutins=11),
        Theme(slug="education",     nom="Éducation",           description="École, université, recherche.", nb_scrutins=19),
        Theme(slug="securite",      nom="Sécurité",            description="Police, renseignement, ordre public.", nb_scrutins=26),
        Theme(slug="outre-mer",     nom="Outre-mer",           description="Territoires ultramarins, collectivités.", nb_scrutins=9),
    ]
    db.add_all(themes)
    print(f"Seeded {len(themes)} themes.")


def seed_ecarts(db):
    if db.query(Ecart).count() > 0:
        print("Ecarts already seeded, skipping.")
        return

    ecarts = [
        Ecart(
            depute_nom="Personnalité A",
            role="Présidente de groupe",
            groupe_acronyme="EPR",
            quote_said="« Nous sommes pleinement engagés en faveur d'une fiscalité plus juste, qui pèse sur les plus aisés. »",
            quote_said_when="Plateau LCI · 14 mars 2024",
            vote_label="Contre — amendement n°4128",
            vote_position="contre",
            vote_when="Scrutin n°2361 · 02 mai 2026",
        ),
        Ecart(
            depute_nom="Personnalité B",
            role="Ministre",
            groupe_acronyme="HOR",
            quote_said="« La planification écologique est notre boussole, sur tous les textes. »",
            quote_said_when="Tribune Le Monde · 4 avril 2025",
            vote_label="Abstention — loi-cadre planification",
            vote_position="abst",
            vote_when="Scrutin n°2368 · 06 mai 2026",
        ),
        Ecart(
            depute_nom="Personnalité C",
            role="Député",
            groupe_acronyme="SOC",
            quote_said="« Nous nous opposerons fermement à toute reconduction des subventions aux énergies fossiles. »",
            quote_said_when="Émission Quotidien · 12 février 2026",
            vote_label="Absent — vote sur niches fiscales",
            vote_position="absent",
            vote_when="Scrutin n°2374 · 10 mai 2026",
        ),
        Ecart(
            depute_nom="Personnalité D",
            role="Sénatrice",
            groupe_acronyme="DR",
            quote_said="« La défense des libertés publiques ne se négocie pas. »",
            quote_said_when="Interview RFI · 28 mars 2025",
            vote_label="Pour — article 7 loi sécurité globale",
            vote_position="pour",
            vote_when="Scrutin Sénat n°142 · 23 avr. 2026",
        ),
        Ecart(
            depute_nom="Personnalité E",
            role="Vice-président de l'Assemblée",
            groupe_acronyme="LFI",
            quote_said="« L'impôt sur le capital est une priorité absolue pour rééquilibrer les richesses. »",
            quote_said_when="France Inter · 3 janvier 2026",
            vote_label="Absent — vote contribution capital",
            vote_position="absent",
            vote_when="Scrutin n°2355 · 28 avr. 2026",
        ),
    ]
    db.add_all(ecarts)
    print(f"Seeded {len(ecarts)} ecarts.")


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_themes(db)
        seed_ecarts(db)
        db.commit()
        print("Editorial seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
