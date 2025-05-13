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
    model_validator,
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

    producers_ids: list[int] = Field(default=[], validation_alias="producers")
    licensors_ids: list[int] = Field(default=[], validation_alias="licensors")
    studios_ids: list[int] = Field(default=[], validation_alias="studios")
    genres_ids: list[int] = Field(default=[], validation_alias="genres")
    themes_ids: list[int] = Field(default=[], validation_alias="themes")
    demographics_ids: list[int] = Field(default=[], validation_alias="demographics")

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


# Mangadex
class AuthorModel(BaseDataModel):
    id: str
    name: str = Field(validation_alias=AliasPath("attributes", "name"))


class TagMangadexModel(BaseDataModel):
    id: str
    name: str = Field(validation_alias=AliasPath("attributes", "name", "en"))
    type: str = Field(validation_alias=AliasPath("attributes", "group"))


class MangaRelationModel(BaseDataModel):
    id_manga: str
    id_manga_related: str
    relation: str
    manga_related: "MangaModel"


class MangaAuthorModel(BaseDataModel):
    id_manga: str
    id_author: str
    relation: str
    author: AuthorModel


class MangaTagModel(BaseDataModel):
    id_manga: str
    id_tag: str


class MangaModel(BaseDataModel):
    id: str
    title: str
    title_jp: Optional[str] = ""
    synopsis: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "description", "en")
    )
    synopsis_jp: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "description", "ja")
    )
    last_volume: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "lastVolume")
    )
    last_chapter: Optional[str] = Field(
        validation_alias=AliasPath("attributes", "lastChapter")
    )
    demographic: Optional[str] = Field(
        validation_alias=AliasPath("attributes", "publicationDemographic")
    )
    status: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "status")
    )
    publication_year: Optional[int] = Field(
        default=None, validation_alias=AliasPath("attributes", "year")
    )
    rating: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "contentRating")
    )
    id_anilist: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "links", "al")
    )
    id_amazon: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "links", "amz")
    )
    id_bookwalker: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "links", "bw")
    )
    id_mal: Optional[str] = Field(
        default=None, validation_alias=AliasPath("attributes", "links", "mal")
    )
    id_cover_art: Optional[str] = Field(default=None)
    manga_relations: list[MangaRelationModel] = Field(default=[])
    manga_authors: list[MangaAuthorModel] = Field(default=[])
    manga_tags: list[MangaTagModel] = Field(default=[])

    @model_validator(mode="before")
    @classmethod
    def extract_relationships(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        data["manga_relations"] = []
        data["manga_authors"] = []
        data["manga_tags"] = []
        for relation in data.get("relationships", []):
            match relation["type"]:
                case "cover_art":
                    data["id_cover_art"] = relation["id"]
                case "author" | "artist":
                    data["manga_authors"].append(
                        {
                            "id_manga": data["id"],
                            "id_author": relation["id"],
                            "relation": relation["type"],
                            "author": relation,
                        }
                    )
                case "manga":
                    data["manga_relations"].append(
                        {
                            "id_manga": data["id"],
                            "id_manga_related": relation["id"],
                            "relation": relation["type"],
                            "manga_related": relation,
                        }
                    )
        for tag in data.get("attributes", {}).get("tags", []):
            data["manga_tags"].append({"id_manga": data["id"], "id_tag": tag["id"]})

        title: dict[str, str] = data.get("attributes", {}).get("title", {})
        altTitles = data.get("attributes", {}).get("altTitles", [])
        data["title"] = next(iter(title.values()), None)
        data["title_jp"] = None
        if "en" not in title:
            for altTitle in altTitles:
                if "en" in altTitle:
                    data["title"] = altTitle["en"]
                    break
        for altTitle in altTitles:
            if "ja" in altTitle:
                data["title_jp"] = altTitle["ja"]
                break
            if "ja-ro" in altTitle:
                data["title_jp"] = altTitle["ja-ro"]
        return data

    # example of manga with the following issue: 68b257db-f74b-47ff-946b-284f9fc47c17
    @field_validator("manga_relations", mode="before")
    @classmethod
    def remove_inexistant_manga_from_manga_relations(cls, v: Any) -> Any:
        updated_manga_relations = []
        for mr in v:
            try:
                MangaRelationModel.model_validate(mr)
                updated_manga_relations.append(mr)
            except ValidationError:
                pass
        return updated_manga_relations

    # example of manga with inexistant author: 1bbdc5f0-574d-4a49-819d-6d23f6b7a9a7
    @field_validator("manga_authors", mode="before")
    @classmethod
    def remove_inexistant_author_from_manga_authors(cls, v: Any) -> Any:
        updated_manga_authors = []
        for ma in v:
            try:
                MangaAuthorModel.model_validate(ma)
                updated_manga_authors.append(ma)
            except ValidationError:
                pass
        return updated_manga_authors
