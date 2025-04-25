import datetime
from typing import Optional, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AliasPath,
    field_validator,
    AliasChoices,
)


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


class PeopleModel(BaseDataModel):
    id_mal: int = Field(validation_alias="mal_id")
    name: str
    given_name: Optional[str]
    family_name: Optional[str]
    url_mal: str = Field(validation_alias="url")
    url_img: Optional[str] = Field(
        validation_alias=AliasPath("images", "jpg", "image_url")
    )


class MagazineModel(BaseDataModel):
    id_mal: int = Field(validation_alias="mal_id")
    name: str
    url_mal: str = Field(validation_alias="url")


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


class MangaModel(BaseDataModel):
    id_mal: int = Field(validation_alias="mal_id")
    title: str
    title_jp: str = Field(validation_alias="title_japanese")
    type: str
    chapters: Optional[int]
    volumes: Optional[int]
    status: str
    published_from: Optional[datetime.date] = Field(
        validation_alias=AliasPath("published", "from")
    )
    published_to: Optional[datetime.date] = Field(
        validation_alias=AliasPath("published", "to")
    )
    synopsis: str
    url_mal: Optional[str] = Field(validation_alias="url")
    url_img_jpg: Optional[str] = Field(
        validation_alias=AliasPath("images", "jpg", "image_url")
    )
    url_img_jpg_small: Optional[str] = Field(
        validation_alias=AliasPath("images", "jpg", "small_image_url")
    )
    url_img_jpg_large: Optional[str] = Field(
        validation_alias=AliasPath("images", "jpg", "large_image_url")
    )
    url_img_webp: Optional[str] = Field(
        validation_alias=AliasPath("images", "webp", "image_url")
    )
    url_img_webp_small: Optional[str] = Field(
        validation_alias=AliasPath("images", "webp", "small_image_url")
    )
    url_img_webp_large: Optional[str] = Field(
        validation_alias=AliasPath("images", "webp", "large_image_url")
    )

    genres_ids: Optional[list[int]] = Field(validation_alias="genres")
    themes_ids: Optional[list[int]] = Field(validation_alias="themes")
    demographics_ids: Optional[list[int]] = Field(validation_alias="demographics")
    authors_ids: list[int] = Field(validation_alias="authors")
    magazines_ids: Optional[list[int]] = Field(validation_alias="serializations")

    @field_validator(
        "genres_ids",
        "themes_ids",
        "demographics_ids",
        "authors_ids",
        "magazines_ids",
        mode="before",
    )
    @classmethod
    def extract_ids_from_dict(cls, val: Any) -> Any:
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
