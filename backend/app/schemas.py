from pydantic import BaseModel


class GroupeOut(BaseModel):
    id: int
    slug: str
    nom: str
    acronyme: str
    couleur: str | None = None

    model_config = {"from_attributes": True}


class DeputeListItem(BaseModel):
    uid: str
    slug: str
    nom: str
    prenom: str
    circo_departement: str | None = None
    circo_numero: int | None = None
    photo_url: str | None = None
    groupe: GroupeOut | None = None

    model_config = {"from_attributes": True}


class VoteOut(BaseModel):
    position: str
    depute_uid: str
    depute_nom: str
    depute_prenom: str
    groupe_acronyme: str | None = None

    model_config = {"from_attributes": True}


class ScrutinListItem(BaseModel):
    id: int
    numero: int
    titre: str
    date_scrutin: str
    sort: str
    nb_pour: int
    nb_contre: int
    nb_abstention: int
    nb_votants: int

    model_config = {"from_attributes": True}


class ScrutinDetail(ScrutinListItem):
    votes: list[VoteOut] = []


class DeputeVoteItem(BaseModel):
    position: str
    scrutin_numero: int
    scrutin_titre: str
    scrutin_date: str
    scrutin_sort: str


class DeputeDetail(BaseModel):
    uid: str
    slug: str
    nom: str
    prenom: str
    sexe: str | None = None
    date_naissance: str | None = None
    circo_departement: str | None = None
    circo_numero: int | None = None
    date_mandat_debut: str | None = None
    photo_url: str | None = None
    url_an: str | None = None
    groupe: GroupeOut | None = None
    recent_votes: list[DeputeVoteItem] = []

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list


class StatsOut(BaseModel):
    total_deputes: int
    total_groupes: int
    total_scrutins: int
    total_votes: int
    derniere_sync: str | None = None
