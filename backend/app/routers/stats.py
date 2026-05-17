from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Depute, Groupe, Scrutin, Vote
from app.schemas import StatsOut

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    derniere_sync = db.query(func.max(Depute.synced_at)).scalar()

    return StatsOut(
        total_deputes=db.query(Depute).count(),
        total_groupes=db.query(Groupe).count(),
        total_scrutins=db.query(Scrutin).count(),
        total_votes=db.query(Vote).count(),
        derniere_sync=str(derniere_sync) if derniere_sync else None,
    )
