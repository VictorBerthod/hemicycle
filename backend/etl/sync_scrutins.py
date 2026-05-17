"""ETL script to sync scrutins and votes from CIVIX API + AN website."""

import logging
import re
import time

import httpx
from sqlalchemy.orm import Session

from app.config import AN_BASE_URL, CIVIX_API_BASE, CIVIX_PAGE_SIZE, LEGISLATURE, REQUEST_DELAY
from app.database import SessionLocal, init_db
from app.models import Depute, Scrutin, Vote

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def fetch_scrutins(client: httpx.Client, page: int = 1, page_size: int = CIVIX_PAGE_SIZE) -> tuple[list[dict], int | None]:
    """Fetch a page of scrutins from CIVIX API. Returns (results, next_page)."""
    url = f"{CIVIX_API_BASE}/scrutins?page={page}&page_size={page_size}"
    resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("data", {}).get("attributes", {}).get("results", [])
    pagination = data.get("meta", {}).get("pagination", {})
    next_page = pagination.get("next_page")
    return results, next_page


def fetch_all_scrutins(client: httpx.Client) -> list[dict]:
    """Fetch all scrutins with pagination."""
    all_scrutins = []
    page = 1

    while True:
        results, next_page = fetch_scrutins(client, page)
        if not results:
            break
        all_scrutins.extend(results)

        if not next_page:
            break
        page = next_page
        time.sleep(REQUEST_DELAY)

    return all_scrutins


def parse_votes_from_html(html: str) -> list[dict]:
    """Parse individual votes from AN scrutin HTML page.

    Returns list of {"uid": "PA...", "position": "pour|contre|abstention"}
    """
    votes = []
    current_position = None

    # Split by lines and track position headers
    # The structure is: <span class="h6 _colored-travaux">Pour</span>
    # followed by list items with deputy links
    lines = html.split("\n")

    for i, line in enumerate(lines):
        # Detect position header
        pos_match = re.search(r'<span class="h6[^"]*">(Pour|Contre|Abstention|Non-votant)', line, re.I)
        if pos_match:
            pos_text = pos_match.group(1).lower()
            if pos_text == "non-votant":
                current_position = None  # Skip non-votants
            else:
                current_position = pos_text
            continue

        # Detect deputy in current position section
        if current_position:
            dep_match = re.search(r'data-acteur-id="(PA\d+)', line)
            if dep_match:
                votes.append({"uid": dep_match.group(1), "position": current_position})

    return votes


def fetch_votes_for_scrutin(client: httpx.Client, numero: int) -> list[dict]:
    """Fetch individual votes by scraping the AN scrutin page."""
    url = f"{AN_BASE_URL}/dyn/{LEGISLATURE}/scrutins/{numero}"
    try:
        resp = client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            logger.warning(f"Scrutin {numero}: HTTP {resp.status_code}")
            return []
        return parse_votes_from_html(resp.text)
    except httpx.HTTPError as e:
        logger.warning(f"Scrutin {numero}: request failed: {e}")
        return []


def sync_scrutins(db: Session, scrutins_data: list[dict]) -> tuple[int, int]:
    """Upsert scrutins metadata. Returns (created, skipped) counts."""
    created = 0
    skipped = 0

    for s in scrutins_data:
        numero = s.get("numero")
        if not numero:
            continue

        # Check if already exists (incremental sync)
        existing = db.query(Scrutin).filter(Scrutin.numero == numero).first()
        if existing:
            skipped += 1
            continue

        # Parse sort code
        sort_info = s.get("sort", {})
        sort_code = sort_info.get("code", "") if isinstance(sort_info, dict) else str(sort_info)

        scrutin = Scrutin(
            numero=numero,
            titre=s.get("titre", s.get("objet_libelle", "")),
            date_scrutin=s.get("date_scrutin", "")[:10],  # Keep just date part
            sort=sort_code,
            source="civix.fr",
        )
        db.add(scrutin)
        created += 1

    db.commit()
    logger.info(f"Scrutins synced: {created} created, {skipped} already existed")
    return created, skipped


def sync_votes(db: Session, client: httpx.Client, limit: int | None = None) -> tuple[int, int]:
    """Fetch and sync individual votes for scrutins that don't have votes yet.

    Args:
        limit: Max number of scrutins to process (for testing/incremental)
    Returns (scrutins_processed, votes_created)
    """
    # Find scrutins without votes
    scrutins_without_votes = (
        db.query(Scrutin)
        .filter(Scrutin.nb_votants == 0)
        .order_by(Scrutin.numero.desc())
        .limit(limit)
        .all()
    )

    # Build uid -> depute_id map
    depute_map = {d.uid: d.id for d in db.query(Depute).all()}

    scrutins_processed = 0
    total_votes_created = 0

    for scrutin in scrutins_without_votes:
        votes_data = fetch_votes_for_scrutin(client, scrutin.numero)

        if not votes_data:
            # Mark as processed with 0 votes (might be a hand vote)
            scrutin.nb_votants = -1  # -1 = no detail available
            db.commit()
            continue

        votes_created = 0
        nb_pour = 0
        nb_contre = 0
        nb_abstention = 0

        for v in votes_data:
            depute_id = depute_map.get(v["uid"])
            if not depute_id:
                continue

            vote = Vote(
                scrutin_id=scrutin.id,
                depute_id=depute_id,
                position=v["position"],
                source="assemblee-nationale.fr",
            )
            db.add(vote)
            votes_created += 1

            if v["position"] == "pour":
                nb_pour += 1
            elif v["position"] == "contre":
                nb_contre += 1
            elif v["position"] == "abstention":
                nb_abstention += 1

        scrutin.nb_pour = nb_pour
        scrutin.nb_contre = nb_contre
        scrutin.nb_abstention = nb_abstention
        scrutin.nb_votants = nb_pour + nb_contre + nb_abstention
        db.commit()

        scrutins_processed += 1
        total_votes_created += votes_created
        logger.info(f"Scrutin {scrutin.numero}: {votes_created} votes ({nb_pour}P/{nb_contre}C/{nb_abstention}A)")

        time.sleep(REQUEST_DELAY)

    logger.info(f"Votes sync: {scrutins_processed} scrutins processed, {total_votes_created} votes created")
    return scrutins_processed, total_votes_created


def run(votes_limit: int | None = 50):
    """Main ETL entry point.

    Args:
        votes_limit: Max scrutins to fetch votes for per run (rate limiting)
    """
    init_db()
    db = SessionLocal()

    try:
        with httpx.Client(timeout=30.0) as client:
            # Step 1: Sync scrutin metadata from CIVIX
            logger.info("Fetching scrutins from CIVIX API...")
            scrutins_data = fetch_all_scrutins(client)
            logger.info(f"Fetched {len(scrutins_data)} scrutins")
            sync_scrutins(db, scrutins_data)

            # Step 2: Fetch individual votes from AN HTML pages
            logger.info(f"Syncing votes (limit={votes_limit} scrutins per run)...")
            sync_votes(db, client, limit=votes_limit)

    except httpx.HTTPError as e:
        logger.error(f"API request failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    run(votes_limit=limit)
