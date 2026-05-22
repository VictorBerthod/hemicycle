import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TAG_CATEGORIES, Depute, DeputeTag, Tag
from app.schemas import TagAttach, TagCreate, TagOut, TagUpdate

router = APIRouter(prefix="/api/tags", tags=["tags"])


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value)
    return value.strip("-") or "tag"


def _validate_categorie(categorie: str) -> str:
    if categorie not in TAG_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"categorie must be one of {TAG_CATEGORIES}",
        )
    return categorie


@router.get("", response_model=list[TagOut])
def list_tags(
    categorie: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Tag)
    if categorie:
        query = query.filter(Tag.categorie == categorie)
    if search:
        pattern = f"%{search}%"
        query = query.filter(Tag.libelle.ilike(pattern))
    return query.order_by(Tag.categorie, Tag.libelle).all()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    _validate_categorie(payload.categorie)
    slug = payload.slug or _slugify(f"{payload.categorie}-{payload.libelle}")

    if db.query(Tag).filter(Tag.slug == slug).first():
        raise HTTPException(status_code=409, detail=f"Tag with slug '{slug}' already exists")

    tag = Tag(
        slug=slug,
        libelle=payload.libelle.strip(),
        categorie=payload.categorie,
        couleur=payload.couleur,
        description=payload.description,
    )
    db.add(tag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tag conflict")
    db.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, payload: TagUpdate, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if payload.categorie is not None:
        _validate_categorie(payload.categorie)
        tag.categorie = payload.categorie
    if payload.libelle is not None:
        tag.libelle = payload.libelle.strip()
    if payload.couleur is not None:
        tag.couleur = payload.couleur
    if payload.description is not None:
        tag.description = payload.description

    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.query(DeputeTag).filter(DeputeTag.tag_id == tag_id).delete(synchronize_session=False)
    db.delete(tag)
    db.commit()
    return None


@router.get("/categories", response_model=list[dict])
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(Tag.categorie, func.count(Tag.id))
        .group_by(Tag.categorie)
        .all()
    )
    counts = {cat: nb for cat, nb in rows}
    return [{"categorie": c, "count": counts.get(c, 0)} for c in TAG_CATEGORIES]


# ── Attach / detach a tag to a deputy ──────────────────────────────────────


tag_attach_router = APIRouter(prefix="/api/deputes", tags=["tags"])


@tag_attach_router.post(
    "/{uid}/tags/{tag_id}",
    response_model=list[TagOut],
    status_code=status.HTTP_201_CREATED,
)
def attach_tag(uid: str, tag_id: int, payload: TagAttach | None = None, db: Session = Depends(get_db)):
    depute = db.query(Depute).filter(Depute.uid == uid).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    existing = (
        db.query(DeputeTag)
        .filter(DeputeTag.depute_id == depute.id, DeputeTag.tag_id == tag_id)
        .first()
    )
    if not existing:
        link = DeputeTag(
            depute_id=depute.id,
            tag_id=tag_id,
            source=(payload.source if payload else "manuel"),
        )
        db.add(link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    db.refresh(depute)
    return depute.tags


@tag_attach_router.delete(
    "/{uid}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def detach_tag(uid: str, tag_id: int, db: Session = Depends(get_db)):
    depute = db.query(Depute).filter(Depute.uid == uid).first()
    if not depute:
        raise HTTPException(status_code=404, detail="Depute not found")
    db.query(DeputeTag).filter(
        DeputeTag.depute_id == depute.id,
        DeputeTag.tag_id == tag_id,
    ).delete(synchronize_session=False)
    db.commit()
    return None
