"""Tests for the deputes ETL pipeline."""

import pytest

from app.models import Depute, Groupe
from etl.sync_deputes import sync_deputes, sync_groupes


SAMPLE_GROUPES = [
    {"uid": "PO845413", "abbr": "LFI-NFP", "libelle": "La France insoumise - Nouveau Front Populaire"},
    {"uid": "PO845419", "abbr": "RN", "libelle": "Rassemblement National"},
]

SAMPLE_DEPUTES = [
    {
        "uid": "PA795228",
        "prenom": "Nadege",
        "nom": "Abomangoli",
        "circ_departement": "Seine-Saint-Denis",
        "circ_num": 10,
        "groupe_uid": "PO845413",
        "urls": {"assemblee": "https://www.assemblee-nationale.fr/dyn/deputes/PA795228"},
    },
    {
        "uid": "PA793146",
        "prenom": "Nicolas",
        "nom": "Dragon",
        "circ_departement": "Var",
        "circ_num": 3,
        "groupe_uid": "PO845419",
        "urls": {"assemblee": "https://www.assemblee-nationale.fr/dyn/deputes/PA793146"},
    },
]


def test_sync_deputes_creates_records(db):
    """Verify insertion from mock API data."""
    groupe_map = sync_groupes(db, SAMPLE_GROUPES)
    created, updated = sync_deputes(db, SAMPLE_DEPUTES, groupe_map)

    assert created == 2
    assert updated == 0
    assert db.query(Depute).count() == 2

    dep = db.query(Depute).filter(Depute.uid == "PA795228").first()
    assert dep.nom == "Abomangoli"
    assert dep.prenom == "Nadege"
    assert dep.circo_departement == "Seine-Saint-Denis"
    assert dep.groupe_id == groupe_map["PO845413"]
    assert dep.source == "civix.fr"


def test_sync_deputes_updates_existing(db):
    """Verify upsert - no duplicates on re-sync."""
    groupe_map = sync_groupes(db, SAMPLE_GROUPES)

    # First sync
    sync_deputes(db, SAMPLE_DEPUTES, groupe_map)
    assert db.query(Depute).count() == 2

    # Second sync with updated data
    updated_deputes = [
        {**SAMPLE_DEPUTES[0], "circ_num": 11},  # Changed circo
        SAMPLE_DEPUTES[1],
    ]
    created, updated = sync_deputes(db, updated_deputes, groupe_map)

    assert created == 0
    assert updated == 2
    assert db.query(Depute).count() == 2  # No duplicates


def test_sync_deputes_api_failure(db):
    """Verify database is not corrupted if sync fails mid-way."""
    groupe_map = sync_groupes(db, SAMPLE_GROUPES)

    # First successful sync
    sync_deputes(db, SAMPLE_DEPUTES, groupe_map)
    assert db.query(Depute).count() == 2

    # Simulate partial bad data (missing uid)
    bad_deputes = [{"prenom": "Bad", "nom": "Data"}]  # No uid
    sync_deputes(db, bad_deputes, groupe_map)

    # Original data preserved
    assert db.query(Depute).count() == 2


def test_sync_groupes(db):
    """Verify group creation and mapping."""
    groupe_map = sync_groupes(db, SAMPLE_GROUPES)

    assert len(groupe_map) == 2
    assert "PO845413" in groupe_map
    assert "PO845419" in groupe_map
    assert db.query(Groupe).count() == 2

    lfi = db.query(Groupe).filter(Groupe.slug == "PO845413").first()
    assert lfi.acronyme == "LFI-NFP"
