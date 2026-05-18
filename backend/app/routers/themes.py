from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Theme
from app.schemas import ThemeOut

router = APIRouter(prefix="/api/themes", tags=["themes"])


@router.get("", response_model=list[ThemeOut])
def list_themes(db: Session = Depends(get_db)):
    return db.query(Theme).order_by(Theme.nom).all()


@router.get("/{slug}", response_model=ThemeOut)
def get_theme(slug: str, db: Session = Depends(get_db)):
    theme = db.query(Theme).filter(Theme.slug == slug).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme
