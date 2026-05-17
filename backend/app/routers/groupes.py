from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Depute, Groupe
from app.schemas import GroupeOut

router = APIRouter(prefix="/api/groupes", tags=["groupes"])


@router.get("", response_model=list[GroupeOut])
def list_groupes(db: Session = Depends(get_db)):
    return db.query(Groupe).order_by(Groupe.nom).all()


@router.get("/composition")
def get_composition(db: Session = Depends(get_db)):
    """Returns deputy count per group for hemicycle visualization."""
    rows = (
        db.query(Groupe.acronyme, Groupe.nom, func.count(Depute.id))
        .join(Depute, Depute.groupe_id == Groupe.id)
        .group_by(Groupe.id)
        .order_by(Groupe.nom)
        .all()
    )
    return [
        {"acronyme": r[0], "nom": r[1], "count": r[2]}
        for r in rows
    ]
