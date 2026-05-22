from pydantic import BaseModel, Field


class GroupeOut(BaseModel):
    id: int
    slug: str
    nom: str
    acronyme: str
    couleur: str | None = None

    model_config = {"from_attributes": True}


class TagOut(BaseModel):
    id: int
    slug: str
    libelle: str
    categorie: str
    couleur: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    libelle: str = Field(min_length=1, max_length=80)
    categorie: str = Field(min_length=1, max_length=40)
    couleur: str | None = Field(default=None, max_length=20)
    description: str | None = None
    slug: str | None = Field(default=None, max_length=80)


class TagUpdate(BaseModel):
    libelle: str | None = Field(default=None, max_length=80)
    categorie: str | None = Field(default=None, max_length=40)
    couleur: str | None = Field(default=None, max_length=20)
    description: str | None = None


class TagAttach(BaseModel):
    source: str = Field(default="manuel", max_length=40)


class DeputeListItem(BaseModel):
    uid: str
    slug: str
    nom: str
    prenom: str
    circo_departement: str | None = None
    circo_numero: int | None = None
    photo_url: str | None = None
    groupe: GroupeOut | None = None
    tags: list[TagOut] = []

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
    profession: str | None = None
    mandats_anterieurs: str | None = None
    bio_short: str | None = None
    groupe: GroupeOut | None = None
    tags: list[TagOut] = []
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


class EcartOut(BaseModel):
    id: int
    depute_nom: str
    role: str | None = None
    groupe_acronyme: str | None = None
    photo_url: str | None = None
    quote_said: str
    quote_said_when: str | None = None
    vote_label: str
    vote_position: str | None = None
    vote_when: str | None = None

    model_config = {"from_attributes": True}


class ThemeOut(BaseModel):
    id: int
    slug: str
    nom: str
    description: str | None = None
    nb_scrutins: int = 0

    model_config = {"from_attributes": True}
