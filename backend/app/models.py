from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Groupe(Base):
    __tablename__ = "groupes"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    nom: Mapped[str] = mapped_column(String)
    acronyme: Mapped[str] = mapped_column(String)
    couleur: Mapped[str | None] = mapped_column(String, nullable=True)

    deputes: Mapped[list["Depute"]] = relationship(back_populates="groupe")

    # metadata
    source: Mapped[str] = mapped_column(String, default="nosdeputes.fr")
    synced_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Depute(Base):
    __tablename__ = "deputes"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    nom: Mapped[str] = mapped_column(String)
    prenom: Mapped[str] = mapped_column(String)
    sexe: Mapped[str | None] = mapped_column(String, nullable=True)
    date_naissance: Mapped[str | None] = mapped_column(String, nullable=True)
    circo_departement: Mapped[str | None] = mapped_column(String, nullable=True)
    circo_numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_mandat_debut: Mapped[str | None] = mapped_column(String, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    url_an: Mapped[str | None] = mapped_column(String, nullable=True)

    groupe_id: Mapped[int | None] = mapped_column(ForeignKey("groupes.id"), nullable=True)
    groupe: Mapped["Groupe | None"] = relationship(back_populates="deputes")

    votes: Mapped[list["Vote"]] = relationship(back_populates="depute")

    # metadata
    source: Mapped[str] = mapped_column(String, default="nosdeputes.fr")
    synced_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Scrutin(Base):
    __tablename__ = "scrutins"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    titre: Mapped[str] = mapped_column(String)
    date_scrutin: Mapped[str] = mapped_column(String, index=True)
    sort: Mapped[str] = mapped_column(String)  # "adopté" / "rejeté"
    nb_pour: Mapped[int] = mapped_column(Integer, default=0)
    nb_contre: Mapped[int] = mapped_column(Integer, default=0)
    nb_abstention: Mapped[int] = mapped_column(Integer, default=0)
    nb_votants: Mapped[int] = mapped_column(Integer, default=0)

    votes: Mapped[list["Vote"]] = relationship(back_populates="scrutin")

    # metadata
    source: Mapped[str] = mapped_column(String, default="nosdeputes.fr")
    synced_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[str] = mapped_column(String)  # "pour" / "contre" / "abstention"

    scrutin_id: Mapped[int] = mapped_column(ForeignKey("scrutins.id"), index=True)
    scrutin: Mapped["Scrutin"] = relationship(back_populates="votes")

    depute_id: Mapped[int] = mapped_column(ForeignKey("deputes.id"), index=True)
    depute: Mapped["Depute"] = relationship(back_populates="votes")

    # metadata
    source: Mapped[str] = mapped_column(String, default="nosdeputes.fr")
    synced_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Ecart(Base):
    """Documented discrepancy between a public statement and a parliamentary vote."""

    __tablename__ = "ecarts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Who said it
    depute_nom: Mapped[str] = mapped_column(String)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    groupe_acronyme: Mapped[str | None] = mapped_column(String, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # What was said
    quote_said: Mapped[str] = mapped_column(Text)
    quote_said_when: Mapped[str | None] = mapped_column(String, nullable=True)

    # What was voted
    vote_label: Mapped[str] = mapped_column(String)
    vote_position: Mapped[str | None] = mapped_column(String, nullable=True)
    vote_when: Mapped[str | None] = mapped_column(String, nullable=True)

    # Optional FK to actual scrutin/depute records
    scrutin_id: Mapped[int | None] = mapped_column(ForeignKey("scrutins.id"), nullable=True, index=True)
    depute_id: Mapped[int | None] = mapped_column(ForeignKey("deputes.id"), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Theme(Base):
    """Editorial thematic category for scrutins."""

    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    nom: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    nb_scrutins: Mapped[int] = mapped_column(Integer, default=0)
