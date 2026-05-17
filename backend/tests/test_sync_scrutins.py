"""Tests for the scrutins ETL pipeline."""

import pytest

from app.models import Depute, Groupe, Scrutin, Vote
from etl.sync_scrutins import parse_votes_from_html, sync_scrutins


SAMPLE_SCRUTINS = [
    {
        "uid": "VTANR5L17V6645",
        "numero": 6645,
        "titre": "proposition de loi pour une montagne vivante",
        "date_scrutin": "2026-05-13T00:00:00+00:00",
        "sort": {"code": "adopte", "libelle": "adopte"},
        "objet_libelle": "proposition de loi pour une montagne vivante",
    },
    {
        "uid": "VTANR5L17V6644",
        "numero": 6644,
        "titre": "amendement n42",
        "date_scrutin": "2026-05-12T00:00:00+00:00",
        "sort": {"code": "rejete", "libelle": "rejete"},
    },
]

SAMPLE_HTML = """
<div class="scrutin-groupe">
    <div class="_align-self-start _pa-xs _mb-xs">
        <span class="h6 _colored-travaux">Pour</span>
        <span>: 2</span>
    </div>
    <ul class="_2-columns @FocusableList">
        <li class="_no-border" data-acteur-id="PA795228 - PM843062">
            <a href="/dyn/deputes/PA795228" class="link _small">Mme Nadege Abomangoli</a>
        </li>
        <li class="_no-border" data-acteur-id="PA793912 - PM843100">
            <a href="/dyn/deputes/PA793912" class="link _small">M. Sylvain Carriere</a>
        </li>
    </ul>
</div>
<div class="scrutin-groupe">
    <div class="_align-self-start _pa-xs _mb-xs">
        <span class="h6 _colored-travaux">Contre</span>
        <span>: 1</span>
    </div>
    <ul class="_2-columns @FocusableList">
        <li class="_no-border" data-acteur-id="PA793146 - PM843050">
            <a href="/dyn/deputes/PA793146" class="link _small">M. Nicolas Dragon</a>
        </li>
    </ul>
</div>
<div class="scrutin-groupe">
    <div class="_align-self-start _pa-xs _mb-xs">
        <span class="h6 _colored-travaux">Abstention</span>
        <span>: 1</span>
    </div>
    <ul class="_2-columns @FocusableList">
        <li class="_no-border" data-acteur-id="PA719938 - PM843010">
            <a href="/dyn/deputes/PA719938" class="link _small">M. Marc Fesneau</a>
        </li>
    </ul>
</div>
<div class="scrutin-groupe">
    <div class="_align-self-start _pa-xs _mb-xs">
        <span class="h6 _colored-travaux">Non-votant</span>
        <span>: 1</span>
    </div>
    <ul class="_2-columns @FocusableList">
        <li class="_no-border" data-acteur-id="PA999999 - PM843999">
            <a href="/dyn/deputes/PA999999" class="link _small">Mme Presidente</a>
        </li>
    </ul>
</div>
"""


def test_sync_scrutins_incremental(db):
    """Verify incremental sync - existing scrutins are not re-created."""
    # First sync
    created, skipped = sync_scrutins(db, SAMPLE_SCRUTINS)
    assert created == 2
    assert skipped == 0
    assert db.query(Scrutin).count() == 2

    # Second sync with same data
    created, skipped = sync_scrutins(db, SAMPLE_SCRUTINS)
    assert created == 0
    assert skipped == 2
    assert db.query(Scrutin).count() == 2  # No duplicates


def test_scrutin_fields_stored(db):
    """Verify scrutin fields are correctly stored."""
    sync_scrutins(db, SAMPLE_SCRUTINS)

    s = db.query(Scrutin).filter(Scrutin.numero == 6645).first()
    assert s.titre == "proposition de loi pour une montagne vivante"
    assert s.date_scrutin == "2026-05-13"
    assert s.sort == "adopte"
    assert s.source == "civix.fr"


def test_parse_votes_from_html():
    """Verify HTML parsing extracts correct vote positions."""
    votes = parse_votes_from_html(SAMPLE_HTML)

    assert len(votes) == 4  # 2 pour + 1 contre + 1 abstention
    uids = {v["uid"]: v["position"] for v in votes}

    assert uids["PA795228"] == "pour"
    assert uids["PA793912"] == "pour"
    assert uids["PA793146"] == "contre"
    assert uids["PA719938"] == "abstention"
    # Non-votant should be excluded
    assert "PA999999" not in uids


def test_scrutin_without_detail_skipped(db):
    """Verify scrutins with empty votes don't cause errors."""
    # An empty HTML page (e.g., hand vote)
    votes = parse_votes_from_html("<html><body>No vote detail</body></html>")
    assert votes == []


def test_vote_positions_complete(db):
    """Verify each vote has a valid position."""
    votes = parse_votes_from_html(SAMPLE_HTML)
    valid_positions = {"pour", "contre", "abstention"}

    for v in votes:
        assert v["position"] in valid_positions
        assert v["uid"].startswith("PA")
