from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Depute, Scrutin, Vote
from app.schemas import ScrutinDetail, ScrutinListItem, VoteOut

router = APIRouter(prefix="/api/scrutins", tags=["scrutins"])


@router.get("", response_model=list[ScrutinListItem])
def list_scrutins(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, description="Filter by result: adopte/rejete"),
    db: Session = Depends(get_db),
):
    query = db.query(Scrutin)

    if sort:
        query = query.filter(Scrutin.sort == sort)

    query = query.order_by(Scrutin.date_scrutin.desc(), Scrutin.numero.desc())
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{numero}", response_model=ScrutinDetail)
def get_scrutin(numero: int, db: Session = Depends(get_db)):
    scrutin = db.query(Scrutin).filter(Scrutin.numero == numero).first()
    if not scrutin:
        raise HTTPException(status_code=404, detail="Scrutin not found")

    votes_raw = (
        db.query(Vote, Depute)
        .join(Depute, Vote.depute_id == Depute.id)
        .options(joinedload(Depute.groupe))
        .filter(Vote.scrutin_id == scrutin.id)
        .all()
    )

    votes = [
        VoteOut(
            position=vote.position,
            depute_uid=depute.uid,
            depute_nom=depute.nom,
            depute_prenom=depute.prenom,
            groupe_acronyme=depute.groupe.acronyme if depute.groupe else None,
        )
        for vote, depute in votes_raw
    ]

    return ScrutinDetail(
        id=scrutin.id,
        numero=scrutin.numero,
        titre=scrutin.titre,
        date_scrutin=scrutin.date_scrutin,
        sort=scrutin.sort,
        nb_pour=scrutin.nb_pour,
        nb_contre=scrutin.nb_contre,
        nb_abstention=scrutin.nb_abstention,
        nb_votants=scrutin.nb_votants,
        votes=votes,
    )
