"""Tests for /api/ecarts and /api/themes endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Ecart, Theme

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
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(engine)
    db = TestSession()

    # 5 seed ecarts
    db.add_all([
        Ecart(
            depute_nom="Personnalité A",
            role="Présidente de groupe",
            groupe_acronyme="EPR",
            quote_said="« Nous sommes pleinement engagés en faveur d'une fiscalité plus juste. »",
            quote_said_when="Plateau LCI · 14 mars 2024",
            vote_label="Contre — amendement n°4128",
            vote_position="contre",
            vote_when="Scrutin n°2361 · 02 mai 2026",
        ),
        Ecart(
            depute_nom="Personnalité B",
            role="Ministre",
            groupe_acronyme="HOR",
            quote_said="« La planification écologique est notre boussole. »",
            quote_said_when="Tribune Le Monde · 4 avril 2025",
            vote_label="Abstention — loi-cadre planification",
            vote_position="abst",
            vote_when="Scrutin n°2368 · 06 mai 2026",
        ),
        Ecart(
            depute_nom="Personnalité C",
            role="Député",
            groupe_acronyme="PS",
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
            quote_said_when="Itw RFI · 28 mars 2025",
            vote_label="Pour — article 7 loi sécurité globale",
            vote_position="pour",
            vote_when="Scrutin Sénat n°142 · 23 avr. 2026",
        ),
        Ecart(
            depute_nom="Personnalité E",
            role="Vice-président de l'Assemblée",
            groupe_acronyme="LFI",
            quote_said="« L'impôt sur le capital est une priorité absolue. »",
            quote_said_when="France Inter · 3 janvier 2026",
            vote_label="Absent — vote ISF",
            vote_position="absent",
            vote_when="Scrutin n°2355 · 28 avr. 2026",
        ),
    ])

    # 8 seed themes
    db.add_all([
        Theme(slug="fiscalite",    nom="Fiscalité",            nb_scrutins=48),
        Theme(slug="climat",       nom="Climat · énergie",     nb_scrutins=36),
        Theme(slug="libertes",     nom="Libertés publiques",   nb_scrutins=29),
        Theme(slug="social",       nom="Social · travail",     nb_scrutins=42),
        Theme(slug="logement",     nom="Logement",             nb_scrutins=14),
        Theme(slug="sante",        nom="Santé",                nb_scrutins=22),
        Theme(slug="justice",      nom="Justice",              nb_scrutins=18),
        Theme(slug="international",nom="International",        nb_scrutins=31),
    ])

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(engine)
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


# ── /api/ecarts ──────────────────────────────────────────────────────────────

def test_ecarts_returns_list():
    resp = client.get("/api/ecarts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_ecarts_limit():
    resp = client.get("/api/ecarts?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_ecarts_fields():
    resp = client.get("/api/ecarts")
    item = resp.json()[0]
    assert "id" in item
    assert "depute_nom" in item
    assert "quote_said" in item
    assert "vote_label" in item
    assert "vote_position" in item


def test_ecarts_ordered_by_date_desc():
    resp = client.get("/api/ecarts")
    data = resp.json()
    # Most recently inserted (last seed) should come first
    assert data[0]["depute_nom"] == "Personnalité E"


# ── /api/themes ──────────────────────────────────────────────────────────────

def test_themes_returns_list():
    resp = client.get("/api/themes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 8


def test_themes_fields():
    resp = client.get("/api/themes")
    item = resp.json()[0]
    assert "id" in item
    assert "slug" in item
    assert "nom" in item
    assert "nb_scrutins" in item


def test_themes_ordered_alphabetically():
    resp = client.get("/api/themes")
    noms = [t["nom"] for t in resp.json()]
    assert noms == sorted(noms)


def test_theme_by_slug():
    resp = client.get("/api/themes/fiscalite")
    assert resp.status_code == 200
    data = resp.json()
    assert data["nom"] == "Fiscalité"
    assert data["nb_scrutins"] == 48


def test_theme_not_found():
    resp = client.get("/api/themes/inexistant")
    assert resp.status_code == 404
