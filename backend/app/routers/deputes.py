from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Depute, Scrutin, Vote
from app.schemas import DeputeDetail, DeputeListItem, DeputeVoteItem

router = APIRouter(prefix="/api/deputes", tags=["deputes"])


@router.get("", response_model=list[DeputeListItem])
def list_deputes(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    groupe: str | None = Query(None, description="Filter by groupe acronyme"),
    search: str | None = Query(None, description="Search by name"),
    db: Session = Depends(get_db),
):
    query = db.query(Depute).options(joinedload(Depute.groupe))

    if groupe:
        query = query.join(Depute.groupe).filter(
            func.upper(Depute.groupe.property.mapper.class_.acronyme) == groupe.upper()
        )
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Depute.nom.ilike(pattern)) | (Depute.prenom.ilike(pattern))
        )

    query = query.order_by(Depute.nom, Depute.prenom)
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{uid}", response_model=DeputeDetail)
def get_depute(uid: str, db: Session = Depends(get_db)):
    depute = (
        db.query(Depute)
        .options(joinedload(Depute.groupe))
        .filter(Depute.uid == uid)
        .first()
    )
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")

    # Fetch 10 most recent votes with scrutin info
    recent_votes_raw = (
        db.query(Vote, Scrutin)
        .join(Scrutin, Vote.scrutin_id == Scrutin.id)
        .filter(Vote.depute_id == depute.id)
        .order_by(Scrutin.date_scrutin.desc())
        .limit(10)
        .all()
    )

    recent_votes = [
        DeputeVoteItem(
            position=vote.position,
            scrutin_numero=scrutin.numero,
            scrutin_titre=scrutin.titre,
            scrutin_date=scrutin.date_scrutin,
            scrutin_sort=scrutin.sort,
        )
        for vote, scrutin in recent_votes_raw
    ]

    return DeputeDetail(
        uid=depute.uid,
        slug=depute.slug,
        nom=depute.nom,
        prenom=depute.prenom,
        sexe=depute.sexe,
        date_naissance=depute.date_naissance,
        circo_departement=depute.circo_departement,
        circo_numero=depute.circo_numero,
        date_mandat_debut=depute.date_mandat_debut,
        photo_url=depute.photo_url,
        url_an=depute.url_an,
        groupe=depute.groupe,
        recent_votes=recent_votes,
    )
