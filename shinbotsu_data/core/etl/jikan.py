import logging
from typing import TypeVar, Type

from pydantic import ValidationError

from shinbotsu_data.api.jikan import JikanApiExtractor, JikanEndpoints
from shinbotsu_data.core.schemas import (
    TagModel,
    BaseDataModel,
    MagazineModel,
    PeopleModel,
    ProducerModel,
    AnimeModel,
    MangaModel,
)
from shinbotsu_data.database.database import Database

logger = logging.getLogger(__name__)

ValidationModel = TypeVar("ValidationModel", bound=BaseDataModel)

# TODO add scrapping for anime currently airing
# TODO add scrapping from last page scrapped


def extract_data(
    db: Database,
    api_extractor: JikanApiExtractor,
    endpoint: str,
    validation_model: Type[ValidationModel],
) -> None:
    """Function to extract"""
    page = 1
    while True:
        # TODO Add progress logic (progress bar + save progress in case of interruption)
        # TODO Add update logic (check if number of items is different in response and database)
        response = api_extractor.fetch_data(endpoint, {"page": page})
        if "data" in response:
            validated_items: list[ValidationModel] = []
            for item in response["data"]:
                try:
                    validated_items.append(validation_model.model_validate(item))
                except ValidationError as e:
                    logger.error(
                        f"Failed to validate response data (id: {item['mal_id']}): {e}"
                    )
                    # add logic to keep log somewhere to refetch data later
            # database logic
        if "pagination" not in response or not response["pagination"].get(
            "has_next_page"
        ):
            break
        page += 1


def etl_jikan(db: Database, api_extractor: JikanApiExtractor) -> None:
    extract_data(db, api_extractor, JikanEndpoints.TAG_ANIME.value, TagModel)
    extract_data(db, api_extractor, JikanEndpoints.TAG_MANGA.value, TagModel)
    extract_data(db, api_extractor, JikanEndpoints.PRODUCERS.value, ProducerModel)
    extract_data(db, api_extractor, JikanEndpoints.MAGAZINES.value, MagazineModel)
    extract_data(db, api_extractor, JikanEndpoints.ANIME.value, AnimeModel)
    extract_data(db, api_extractor, JikanEndpoints.MANGA.value, MangaModel)
    extract_data(db, api_extractor, JikanEndpoints.PEOPLE.value, PeopleModel)
