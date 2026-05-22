from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Depute, DeputeTag, Groupe, Scrutin, Tag, Vote
from app.schemas import DeputeDetail, DeputeListItem, DeputeVoteItem

router = APIRouter(prefix="/api/deputes", tags=["deputes"])


@router.get("", response_model=list[DeputeListItem])
def list_deputes(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    groupe: str | None = Query(None, description="Filter by groupe acronyme"),
    search: str | None = Query(None, description="Search by name"),
    tag: list[str] | None = Query(None, description="Filter by tag slug (repeatable)"),
    tag_categorie: str | None = Query(None, description="Filter by tag categorie"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Depute)
        .options(joinedload(Depute.groupe), selectinload(Depute.tags))
    )

    if groupe:
        query = query.join(Depute.groupe).filter(
            func.upper(Groupe.acronyme) == groupe.upper()
        )
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Depute.nom.ilike(pattern)) | (Depute.prenom.ilike(pattern))
        )

    if tag:
        slugs = [t for t in tag if t]
        if slugs:
            query = (
                query.join(DeputeTag, DeputeTag.depute_id == Depute.id)
                .join(Tag, Tag.id == DeputeTag.tag_id)
                .filter(Tag.slug.in_(slugs))
                .group_by(Depute.id)
                .having(func.count(func.distinct(Tag.slug)) == len(slugs))
            )

    if tag_categorie:
        query = (
            query.join(DeputeTag, DeputeTag.depute_id == Depute.id, isouter=False)
            .join(Tag, Tag.id == DeputeTag.tag_id)
            .filter(Tag.categorie == tag_categorie)
            .distinct()
        )

    query = query.order_by(Depute.nom, Depute.prenom)
    return query.offset((page - 1) * limit).limit(limit).all()


@router.get("/{uid}", response_model=DeputeDetail)
def get_depute(uid: str, db: Session = Depends(get_db)):
    depute = (
        db.query(Depute)
        .options(joinedload(Depute.groupe), selectinload(Depute.tags))
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
        profession=depute.profession,
        mandats_anterieurs=depute.mandats_anterieurs,
        bio_short=depute.bio_short,
        groupe=depute.groupe,
        tags=depute.tags,
        recent_votes=recent_votes,
    )


@router.get("/{uid}/dissidences")
def get_dissidences(uid: str, db: Session = Depends(get_db)):
    """Find votes where this deputy voted against the majority of their group."""
    depute = db.query(Depute).filter(Depute.uid == uid).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")
    if not depute.groupe_id:
        return {"dissidences": [], "total_votes": 0, "taux_dissidence": 0}

    # Get all votes by this deputy
    depute_votes = (
        db.query(Vote.scrutin_id, Vote.position)
        .filter(Vote.depute_id == depute.id)
        .all()
    )

    if not depute_votes:
        return {"dissidences": [], "total_votes": 0, "taux_dissidence": 0}

    # For each scrutin, find the majority position of the group
    group_members = (
        db.query(Depute.id)
        .filter(Depute.groupe_id == depute.groupe_id)
        .all()
    )
    group_member_ids = [m[0] for m in group_members]

    dissidences = []
    for scrutin_id, position in depute_votes:
        # Count group votes for this scrutin
        group_votes = (
            db.query(Vote.position, func.count(Vote.id))
            .filter(
                Vote.scrutin_id == scrutin_id,
                Vote.depute_id.in_(group_member_ids),
            )
            .group_by(Vote.position)
            .all()
        )
        if not group_votes:
            continue

        # Majority = position with most votes in the group
        majority_position = max(group_votes, key=lambda x: x[1])[0]

        if position != majority_position:
            scrutin = db.query(Scrutin).filter(Scrutin.id == scrutin_id).first()
            if scrutin:
                dissidences.append({
                    "scrutin_numero": scrutin.numero,
                    "scrutin_titre": scrutin.titre,
                    "scrutin_date": scrutin.date_scrutin,
                    "depute_position": position,
                    "groupe_position": majority_position,
                })

    total = len(depute_votes)
    return {
        "dissidences": dissidences,
        "total_votes": total,
        "taux_dissidence": round(len(dissidences) / total * 100, 1) if total > 0 else 0,
    }
