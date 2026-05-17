from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Depute, Scrutin
from app.schemas import DeputeListItem, ScrutinListItem

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"

    deputes = (
        db.query(Depute)
        .options(joinedload(Depute.groupe))
        .filter((Depute.nom.ilike(pattern)) | (Depute.prenom.ilike(pattern)))
        .limit(limit)
        .all()
    )

    scrutins = (
        db.query(Scrutin)
        .filter(Scrutin.titre.ilike(pattern))
        .order_by(Scrutin.date_scrutin.desc())
        .limit(limit)
        .all()
    )

    return {
        "deputes": [DeputeListItem.model_validate(d) for d in deputes],
        "scrutins": [ScrutinListItem.model_validate(s) for s in scrutins],
    }
