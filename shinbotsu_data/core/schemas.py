import logging
import datetime
from typing import Optional, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AliasPath,
    ValidationError,
    field_validator,
    AliasChoices,
)

logger = logging.getLogger(__name__)


class BaseDataModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")


# JIKAN models
class ProducerModel(BaseDataModel):
    id_mal: int = Field(validation_alias=AliasChoices("mal_id", "id_mal"))
    title: str = Field(
        validation_alias=AliasChoices(AliasPath("titles", 0, "title"), "title")
    )
    title_jp: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(AliasPath("titles", 1, "title"), "title_jp"),
    )
    url_mal: str = Field(validation_alias=AliasChoices("url", "url_mal"))
    url_img: str = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "jpg", "image_url"), "url_img"
        )
    )
    about: Optional[str]
    established: Optional[datetime.date]


class TagModel(BaseDataModel):
    id_mal: int = Field(validation_alias=AliasChoices("mal_id", "id_mal"))
    name: str


class AnimeModel(BaseDataModel):
    id_mal: int = Field(validation_alias=AliasChoices("mal_id", "id_mal"))
    title: str
    title_jp: Optional[str] = Field(
        validation_alias=AliasChoices("title_japanese", "title_jp")
    )
    type: Optional[str]
    source: Optional[str]
    episodes: Optional[int]
    status: Optional[str]
    aired_from: Optional[datetime.date] = Field(
        validation_alias=AliasChoices(AliasPath("aired", "from"), "aired_from")
    )
    aired_to: Optional[datetime.date] = Field(
        validation_alias=AliasChoices(AliasPath("aired", "to"), "aired_to")
    )
    rating: Optional[str]
    synopsis: Optional[str]
    season: Optional[str]
    year: Optional[int]
    url_mal: Optional[str] = Field(validation_alias=AliasChoices("url", "url_mal"))
    url_img_jpg: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "jpg", "image_url"), "url_img_jpg"
        )
    )
    url_img_jpg_small: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "jpg", "small_image_url"), "url_img_jpg_small"
        )
    )
    url_img_jpg_large: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "jpg", "large_image_url"), "url_img_jpg_large"
        )
    )
    url_img_webp: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "webp", "image_url"), "url_img_webp"
        )
    )
    url_img_webp_small: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "webp", "small_image_url"), "url_img_webp_small"
        )
    )
    url_img_webp_large: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("images", "webp", "large_image_url"), "url_img_webp_large"
        )
    )
    youtube_trailer_id: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("trailer", "youtube_id"), "youtube_trailer_id"
        )
    )

    producers_ids: list[Optional[int]] = Field(validation_alias="producers")
    licensors_ids: list[Optional[int]] = Field(validation_alias="licensors")
    studios_ids: list[Optional[int]] = Field(validation_alias="studios")
    genres_ids: Optional[list[int]] = Field(validation_alias="genres")
    themes_ids: Optional[list[int]] = Field(validation_alias="themes")
    demographics_ids: Optional[list[int]] = Field(validation_alias="demographics")

    @field_validator(
        "producers_ids",
        "licensors_ids",
        "studios_ids",
        "genres_ids",
        "themes_ids",
        "demographics_ids",
        mode="before",
    )
    @classmethod
    def extract_ids_from_dict(cls, val: Any) -> Any:
        if isinstance(val, list) and all(isinstance(item, dict) for item in val):
            val = [v["mal_id"] for v in val if "mal_id" in v]
        return val


class AnimeTagModel(BaseDataModel):
    id_anime: int
    id_tag: int
    relation: str


class AnimeProducerModel(BaseDataModel):
    id_anime: int
    id_producer: int
    relation: str


# MangaModel
class MangaRelationModel(BaseDataModel):
    id_manga: str
    id_manga_related: str
    relation: str


class MangaAuthorModel(BaseDataModel):
    id_manga: str
    id_author: str
    relation: str


class MangaModel(BaseDataModel):
    id: str
    title: str = Field(validation_alias=AliasPath("title", "en"))
    title_jp: Optional[str]
    synopsis: Optional[str] = Field(validation_alias=AliasPath("description", "en"))
    synopsis_jp: Optional[str] = Field(validation_alias=AliasPath("description", "ja"))
    last_volume: Optional[int] = Field(validation_alias="lastVolume")
    last_chapter: Optional[int] = Field(validation_alias="lastChapter")
    demographic: Optional[str] = Field(validation_alias="publicationDemographic")
    status: Optional[str]
    publication_year: Optional[int] = Field(validation_alias="year")
    rating: Optional[str] = Field(validation_alias="contentRating")
    id_anilist: Optional[int] = Field(validation_alias=AliasPath("links", "al"))
    id_amazon: Optional[int] = Field(validation_alias=AliasPath("links", "amz"))
    id_bookwalker: Optional[str] = Field(validation_alias=AliasPath("links", "bw"))
    id_mal: Optional[int] = Field(validation_alias=AliasPath("links", "mal"))
    id_cover_art: Optional[str] = ""
    manga_relations: list[Optional[MangaRelationModel]] = []
    authors_relations: list[Optional[MangaAuthorModel]] = []

    @field_validator("id_cover_art", mode="before")
    @classmethod
    def extract_covert_art_id(cls, val: Any) -> Any:
        for relation in val["relationships"]:
            if relation["type"] == "cover_art":
                return relation["id"]

    @field_validator("manga_relations", mode="before")
    @classmethod
    def extract_manga_relations(cls, val: Any) -> Any:
        manga_relations = []
        for relation in val["relationships"]:
            if relation["type"] == "manga":
                try:
                    manga_relations.append(
                        MangaRelationModel(
                            id_manga=val["id"],
                            id_manga_related=relation["id"],
                            relation=relation["related"],
                        )
                    )
                except (KeyError, ValidationError) as e:
                    logger.warning(f"MangaModel validation failed: {e}")
        return manga_relations

    @field_validator("authors_relations", mode="before")
    @classmethod
    def extract_authors_relations(cls, val: Any) -> Any:
        authors_relations = []
        for relation in val["relationships"]:
            if relation["type"] in ["artist", "author"]:
                try:
                    authors_relations.append(
                        MangaAuthorModel(
                            id_manga=val["id"],
                            id_author=relation["id"],
                            relation=relation["type"],
                        )
                    )
                except (KeyError, ValidationError) as e:
                    logger.warning(f"MangaModel validation failed: {e}")
        return authors_relations


class AuthorModel(BaseDataModel):
    id: str
    name: str


class TagMangadexModel(BaseDataModel):
    id: str
    name: str
    type: str


class MangaTagModel(BaseDataModel):
    id_manga: str
    id_tag: str
