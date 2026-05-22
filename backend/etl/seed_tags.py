"""Seed the tag taxonomy: political parties + standard parliamentary roles.

Each tag carries a categorie (parti, poste, commission, profession, mandat, libre).
The party seed also wires a default groupe_acronyme -> parti mapping so deputies
already loaded via the CIVIX ETL get pre-tagged with their most likely party.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import Depute, DeputeTag, Groupe, Tag


# Catalogue de partis présents à l'AN 17e législature, avec couleur indicative
# (codes hex purement informatifs, surchargeables côté frontend).
PARTIS: list[dict] = [
    {"slug": "parti-renaissance",       "libelle": "Renaissance",                "couleur": "#FFC800"},
    {"slug": "parti-modem",             "libelle": "MoDem",                      "couleur": "#FF9933"},
    {"slug": "parti-horizons",          "libelle": "Horizons",                   "couleur": "#0066CC"},
    {"slug": "parti-udi",               "libelle": "UDI",                        "couleur": "#0099CC"},
    {"slug": "parti-lr",                "libelle": "Les Républicains",           "couleur": "#0066AA"},
    {"slug": "parti-ps",                "libelle": "Parti socialiste",           "couleur": "#E91E63"},
    {"slug": "parti-eelv",              "libelle": "Les Écologistes",            "couleur": "#4CAF50"},
    {"slug": "parti-pcf",               "libelle": "PCF",                        "couleur": "#CC0000"},
    {"slug": "parti-lfi",               "libelle": "La France insoumise",        "couleur": "#BB1840"},
    {"slug": "parti-place-publique",    "libelle": "Place publique",             "couleur": "#9C27B0"},
    {"slug": "parti-rn",                "libelle": "Rassemblement national",     "couleur": "#0D3C75"},
    {"slug": "parti-reconquete",        "libelle": "Reconquête",                 "couleur": "#222F5B"},
    {"slug": "parti-udr",               "libelle": "UDR",                        "couleur": "#003366"},
    {"slug": "parti-divers",            "libelle": "Divers / sans étiquette",    "couleur": "#888888"},
]

# Mapping rapide groupe parlementaire -> parti par défaut.
# Plusieurs partis peuvent coexister dans un même groupe; ce mapping ne couvre
# que le parti dominant. L'ajustement fin se fait ensuite à la main via l'API tags.
GROUPE_TO_PARTI: dict[str, str] = {
    "EPR":      "parti-renaissance",      # Ensemble pour la République
    "REN":      "parti-renaissance",
    "MODEM":    "parti-modem",
    "DEM":      "parti-modem",
    "HOR":      "parti-horizons",
    "LIOT":     "parti-divers",
    "DR":       "parti-lr",               # Droite Républicaine
    "LR":       "parti-lr",
    "SOC":      "parti-ps",
    "EST":      "parti-eelv",             # Écologiste et social
    "ECOS":     "parti-eelv",
    "GDR":      "parti-pcf",              # Gauche démocrate et républicaine
    "LFI":      "parti-lfi",
    "LFI-NFP":  "parti-lfi",              # 17e legislature actual acronym
    "RN":       "parti-rn",
    "UDR":      "parti-udr",
    "UDDPLR":   "parti-udr",              # Union des droites pour la République
    "NI":       "parti-divers",
}

# Postes parlementaires standards (catégorie = poste).
POSTES: list[dict] = [
    {"slug": "poste-president-assemblee",      "libelle": "Président·e de l'Assemblée"},
    {"slug": "poste-vice-president-assemblee", "libelle": "Vice-président·e de l'Assemblée"},
    {"slug": "poste-questeur",                 "libelle": "Questeur·rice"},
    {"slug": "poste-secretaire-bureau",        "libelle": "Secrétaire du Bureau"},
    {"slug": "poste-president-groupe",         "libelle": "Président·e de groupe"},
    {"slug": "poste-rapporteur-general",       "libelle": "Rapporteur·rice général·e"},
    {"slug": "poste-president-commission",     "libelle": "Président·e de commission"},
    {"slug": "poste-ministre",                 "libelle": "Ministre"},
    {"slug": "poste-secretaire-etat",          "libelle": "Secrétaire d'État"},
]

# Commissions permanentes de l'AN (catégorie = commission).
COMMISSIONS: list[dict] = [
    {"slug": "commission-affaires-culturelles",    "libelle": "Affaires culturelles et éducation"},
    {"slug": "commission-affaires-economiques",    "libelle": "Affaires économiques"},
    {"slug": "commission-affaires-etrangeres",     "libelle": "Affaires étrangères"},
    {"slug": "commission-affaires-sociales",       "libelle": "Affaires sociales"},
    {"slug": "commission-defense",                 "libelle": "Défense et forces armées"},
    {"slug": "commission-developpement-durable",   "libelle": "Développement durable"},
    {"slug": "commission-finances",                "libelle": "Finances"},
    {"slug": "commission-lois",                    "libelle": "Lois constitutionnelles, législation"},
]


def _upsert_tag(db: Session, slug: str, libelle: str, categorie: str, couleur: str | None = None) -> Tag:
    tag = db.query(Tag).filter(Tag.slug == slug).first()
    if tag:
        tag.libelle = libelle
        tag.categorie = categorie
        if couleur:
            tag.couleur = couleur
        return tag
    tag = Tag(slug=slug, libelle=libelle, categorie=categorie, couleur=couleur)
    db.add(tag)
    db.flush()
    return tag


def seed_partis(db: Session) -> dict[str, Tag]:
    by_slug: dict[str, Tag] = {}
    for p in PARTIS:
        tag = _upsert_tag(db, p["slug"], p["libelle"], "parti", p.get("couleur"))
        by_slug[p["slug"]] = tag
    print(f"Seeded {len(by_slug)} parti tags.")
    return by_slug


def seed_postes(db: Session) -> None:
    for p in POSTES:
        _upsert_tag(db, p["slug"], p["libelle"], "poste")
    print(f"Seeded {len(POSTES)} poste tags.")


def seed_commissions(db: Session) -> None:
    for c in COMMISSIONS:
        _upsert_tag(db, c["slug"], c["libelle"], "commission")
    print(f"Seeded {len(COMMISSIONS)} commission tags.")


def attach_parti_from_groupe(db: Session, parti_tags: dict[str, Tag]) -> None:
    """Attach a default parti tag to each deputy based on their groupe acronyme."""
    deputes = (
        db.query(Depute)
        .join(Depute.groupe)
        .all()
    )
    if not deputes:
        print("No deputies in DB — skipping parti auto-attachment. Run sync_deputes first.")
        return

    attached = 0
    skipped = 0
    for d in deputes:
        if not d.groupe:
            continue
        parti_slug = GROUPE_TO_PARTI.get(d.groupe.acronyme.upper())
        if not parti_slug:
            skipped += 1
            continue
        tag = parti_tags.get(parti_slug)
        if not tag:
            skipped += 1
            continue
        # Skip if already attached
        existing = (
            db.query(DeputeTag)
            .filter(DeputeTag.depute_id == d.id, DeputeTag.tag_id == tag.id)
            .first()
        )
        if existing:
            continue
        db.add(DeputeTag(depute_id=d.id, tag_id=tag.id, source="etl-mapping"))
        attached += 1

    print(f"Auto-attached parti to {attached} deputies (skipped {skipped}).")


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        parti_tags = seed_partis(db)
        seed_postes(db)
        seed_commissions(db)
        db.commit()
        attach_parti_from_groupe(db, parti_tags)
        db.commit()
        print("Tag seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
