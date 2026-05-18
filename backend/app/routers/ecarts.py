from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ecart
from app.schemas import EcartOut

router = APIRouter(prefix="/api/ecarts", tags=["ecarts"])


@router.get("", response_model=list[EcartOut])
def list_ecarts(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return db.query(Ecart).order_by(Ecart.id.desc()).limit(limit).all()
