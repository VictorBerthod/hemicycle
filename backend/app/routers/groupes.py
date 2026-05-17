from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Groupe
from app.schemas import GroupeOut

router = APIRouter(prefix="/api/groupes", tags=["groupes"])


@router.get("", response_model=list[GroupeOut])
def list_groupes(db: Session = Depends(get_db)):
    return db.query(Groupe).order_by(Groupe.nom).all()
