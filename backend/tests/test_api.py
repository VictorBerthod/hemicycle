"""Tests for the API endpoints."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Depute, Groupe, Scrutin, Vote

# Use StaticPool to share the same in-memory connection across threads
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables and seed data for each test."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(engine)
    db = TestSession()

    g1 = Groupe(slug="PO1", nom="La France insoumise", acronyme="LFI-NFP")
    g2 = Groupe(slug="PO2", nom="Rassemblement National", acronyme="RN")
    db.add_all([g1, g2])
    db.flush()

    d1 = Depute(uid="PA001", slug="jean-dupont", nom="Dupont", prenom="Jean",
                circo_departement="Paris", circo_numero=1, groupe_id=g1.id,
                photo_url="https://example.com/photo.jpg")
    d2 = Depute(uid="PA002", slug="marie-martin", nom="Martin", prenom="Marie",
                circo_departement="Lyon", circo_numero=2, groupe_id=g2.id)
    db.add_all([d1, d2])
    db.flush()

    s1 = Scrutin(numero=100, titre="Loi climat", date_scrutin="2026-05-01",
                 sort="adopte", nb_pour=300, nb_contre=200, nb_abstention=50, nb_votants=550)
    s2 = Scrutin(numero=101, titre="Budget 2027", date_scrutin="2026-05-10",
                 sort="rejete", nb_pour=100, nb_contre=400, nb_abstention=30, nb_votants=530)
    db.add_all([s1, s2])
    db.flush()

    v1 = Vote(scrutin_id=s1.id, depute_id=d1.id, position="pour")
    v2 = Vote(scrutin_id=s1.id, depute_id=d2.id, position="contre")
    v3 = Vote(scrutin_id=s2.id, depute_id=d1.id, position="contre")
    db.add_all([v1, v2, v3])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(engine)
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_list_deputes():
    resp = client.get("/api/deputes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["nom"] == "Dupont"


def test_list_deputes_filter_groupe():
    resp = client.get("/api/deputes?groupe=RN")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["nom"] == "Martin"


def test_list_deputes_search():
    resp = client.get("/api/deputes?search=jean")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["prenom"] == "Jean"


def test_get_depute():
    resp = client.get("/api/deputes/PA001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["nom"] == "Dupont"
    assert data["groupe"]["acronyme"] == "LFI-NFP"
    assert len(data["recent_votes"]) == 2


def test_get_depute_not_found():
    resp = client.get("/api/deputes/PA999")
    assert resp.status_code == 404


def test_list_scrutins():
    resp = client.get("/api/scrutins")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["numero"] == 101


def test_list_scrutins_filter_sort():
    resp = client.get("/api/scrutins?sort=adopte")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["numero"] == 100


def test_get_scrutin_with_votes():
    resp = client.get("/api/scrutins/100")
    assert resp.status_code == 200
    data = resp.json()
    assert data["titre"] == "Loi climat"
    assert len(data["votes"]) == 2
    positions = {v["depute_uid"]: v["position"] for v in data["votes"]}
    assert positions["PA001"] == "pour"
    assert positions["PA002"] == "contre"


def test_get_scrutin_not_found():
    resp = client.get("/api/scrutins/9999")
    assert resp.status_code == 404


def test_list_groupes():
    resp = client.get("/api/groupes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_search():
    resp = client.get("/api/search?q=dupont")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["deputes"]) == 1
    assert data["deputes"][0]["nom"] == "Dupont"


def test_search_scrutins():
    resp = client.get("/api/search?q=climat")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scrutins"]) == 1


def test_stats():
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_deputes"] == 2
    assert data["total_groupes"] == 2
    assert data["total_scrutins"] == 2
    assert data["total_votes"] == 3
