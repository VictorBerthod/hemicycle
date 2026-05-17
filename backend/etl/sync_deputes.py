"""ETL script to sync deputies from CIVIX API into local database."""

import logging
import time

import httpx
from sqlalchemy.orm import Session

from app.config import CIVIX_API_BASE, CIVIX_PAGE_SIZE, REQUEST_DELAY
from app.database import SessionLocal, init_db
from app.models import Depute, Groupe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def fetch_groupes(client: httpx.Client) -> list[dict]:
    """Fetch all parliamentary groups from CIVIX API."""
    url = f"{CIVIX_API_BASE}/groupes"
    resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()
    attrs = data.get("data", {}).get("attributes", {})
    return attrs.get("groups", attrs.get("results", []))


def fetch_deputes(client: httpx.Client) -> list[dict]:
    """Fetch all deputies from CIVIX API with pagination."""
    all_deputes = []
    page = 1

    while True:
        url = f"{CIVIX_API_BASE}/deputes?page={page}&page_size={CIVIX_PAGE_SIZE}"
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("data", {}).get("attributes", {}).get("results", [])
        if not results:
            break

        all_deputes.extend(results)

        pagination = data.get("meta", {}).get("pagination", {})
        next_page = pagination.get("next_page")
        if not next_page:
            break

        page = next_page
        time.sleep(REQUEST_DELAY)

    return all_deputes


def sync_groupes(db: Session, groupes_data: list[dict]) -> dict[str, int]:
    """Upsert parliamentary groups. Returns mapping of groupe_uid -> db id."""
    uid_to_id = {}

    for g in groupes_data:
        uid = g.get("uid", "")
        abbr = g.get("abbr", g.get("acronyme", ""))
        nom = g.get("libelle", g.get("nom", ""))

        existing = db.query(Groupe).filter(Groupe.slug == uid).first()
        if existing:
            existing.nom = nom
            existing.acronyme = abbr
            uid_to_id[uid] = existing.id
        else:
            groupe = Groupe(slug=uid, nom=nom, acronyme=abbr, couleur=None)
            db.add(groupe)
            db.flush()
            uid_to_id[uid] = groupe.id

    db.commit()
    logger.info(f"Synced {len(uid_to_id)} groupes")
    return uid_to_id


def sync_deputes(db: Session, deputes_data: list[dict], groupe_map: dict[str, int]) -> tuple[int, int]:
    """Upsert deputies. Returns (created, updated) counts."""
    created = 0
    updated = 0

    for d in deputes_data:
        uid = d.get("uid", "")
        if not uid:
            continue

        groupe_uid = d.get("groupe_uid", "")
        groupe_id = groupe_map.get(groupe_uid)

        # Build slug from name
        slug = f"{d.get('prenom', '').lower()}-{d.get('nom', '').lower()}".replace(" ", "-")

        # Photo URL from AN
        photo_url = f"https://www.assemblee-nationale.fr/dyn/deputes/{uid}/photo"

        existing = db.query(Depute).filter(Depute.uid == uid).first()
        if existing:
            existing.nom = d.get("nom", existing.nom)
            existing.prenom = d.get("prenom", existing.prenom)
            existing.groupe_id = groupe_id
            existing.circo_departement = d.get("circ_departement")
            existing.circo_numero = d.get("circ_num")
            existing.photo_url = photo_url
            existing.url_an = d.get("urls", {}).get("assemblee", "")
            updated += 1
        else:
            depute = Depute(
                uid=uid,
                slug=slug,
                nom=d.get("nom", ""),
                prenom=d.get("prenom", ""),
                groupe_id=groupe_id,
                circo_departement=d.get("circ_departement"),
                circo_numero=d.get("circ_num"),
                photo_url=photo_url,
                url_an=d.get("urls", {}).get("assemblee", ""),
                source="civix.fr",
            )
            db.add(depute)
            created += 1

    db.commit()
    logger.info(f"Deputies synced: {created} created, {updated} updated")
    return created, updated


def run():
    """Main ETL entry point."""
    init_db()
    db = SessionLocal()

    try:
        with httpx.Client(timeout=30.0) as client:
            logger.info("Fetching groupes from CIVIX API...")
            groupes_data = fetch_groupes(client)
            groupe_map = sync_groupes(db, groupes_data)

            logger.info("Fetching deputes from CIVIX API...")
            deputes_data = fetch_deputes(client)
            logger.info(f"Fetched {len(deputes_data)} deputes")

            sync_deputes(db, deputes_data, groupe_map)
    except httpx.HTTPError as e:
        logger.error(f"API request failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
