import logging
from typing import TypeVar, Type, cast

from pydantic import ValidationError

from shinbotsu_data.utils import JikanEndpoints
from shinbotsu_data.api.jikan import JikanApiExtractor
from shinbotsu_data.core.schemas import (
    TagModel,
    BaseDataModel,
    ProducerModel,
    AnimeModel,
    AnimeTagModel,
    AnimeProducerModel,
)
from shinbotsu_data.database.database import Database
from shinbotsu_data.utils import ProgressBar

logger = logging.getLogger(__name__)

ValidationModel = TypeVar("ValidationModel", bound=BaseDataModel)


# TODO add scrapping from last page scrapped
def extract_genres_and_producers(
    anime_list: list[AnimeModel],
) -> tuple[list[AnimeTagModel], list[AnimeProducerModel]]:
    anime_genres = []
    anime_producers = []
    for ani in anime_list:
        anime = ani
        if anime.genres_ids is not None:
            anime_genres.extend(
                [
                    AnimeTagModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_tag": id_genre,
                            "relation": "genre",
                        }
                    )
                    for id_genre in anime.genres_ids
                ]
            )
        if anime.themes_ids is not None:
            anime_genres.extend(
                [
                    AnimeTagModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_tag": id_genre,
                            "relation": "theme",
                        }
                    )
                    for id_genre in anime.themes_ids
                ]
            )
        if anime.demographics_ids is not None:
            anime_genres.extend(
                [
                    AnimeTagModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_tag": id_genre,
                            "relation": "demographic",
                        }
                    )
                    for id_genre in anime.demographics_ids
                ]
            )
        if anime.producers_ids is not None:
            anime_producers.extend(
                [
                    AnimeProducerModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_producer": id_producer,
                            "relation": "producer",
                        }
                    )
                    for id_producer in anime.producers_ids
                ]
            )
        if anime.licensors_ids is not None:
            anime_producers.extend(
                [
                    AnimeProducerModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_producer": id_producer,
                            "relation": "licensor",
                        }
                    )
                    for id_producer in anime.licensors_ids
                ]
            )
        if anime.studios_ids is not None:
            anime_producers.extend(
                [
                    AnimeProducerModel.model_validate(
                        {
                            "id_anime": anime.id_mal,
                            "id_producer": id_producer,
                            "relation": "studio",
                        }
                    )
                    for id_producer in anime.studios_ids
                ]
            )
    return anime_genres, anime_producers


def extract_data(
    db: Database,
    api_extractor: JikanApiExtractor,
    endpoint: str,
    validation_model: Type[ValidationModel],
    prefix: str,
) -> None:
    """Function to extract"""

    existing_producer_ids: list[int] = []
    if endpoint == JikanEndpoints.ANIME.value:
        existing_producer_ids = db.producer_controller.get_all_ids()
    state = db.scraper_state_controller.get_state_by_endpoint(endpoint)
    page = state.get("page", 1)

    total_pages = (
        api_extractor.fetch_data(endpoint, {"page": page})
        .get("pagination", {})
        .get("last_visible_page", 1)
    )
    progress_bar = ProgressBar(total_pages, prefix=f"JIKAN - {prefix} ")
    progress_bar.update_progress(page - 1)

    while True:
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
            match endpoint:
                case JikanEndpoints.TAG_MANGA.value | JikanEndpoints.TAG_ANIME.value:
                    db.tag_controller.upsert_all(cast(list[TagModel], validated_items))
                case JikanEndpoints.PRODUCERS.value:
                    db.producer_controller.upsert_all(
                        cast(list[ProducerModel], validated_items)
                    )
                case JikanEndpoints.ANIME.value:
                    db.anime_controller.upsert_all(
                        cast(list[AnimeModel], validated_items)
                    )
                    anime_genres, anime_producers = extract_genres_and_producers(
                        cast(list[AnimeModel], validated_items)
                    )
                    producer_ids = [ap.id_producer for ap in anime_producers]
                    missing_producer_ids = list(
                        set(producer_ids) - set(existing_producer_ids)
                    )
                    missing_producers: list[ProducerModel] = []
                    for prod_id in missing_producer_ids:
                        res = api_extractor.fetch_data(
                            JikanEndpoints.PRODUCERS.value + f"/{prod_id}"
                        )
                        if "data" in res:
                            try:
                                missing_producers.append(
                                    ProducerModel.model_validate(res["data"])
                                )
                            except ValidationError as e:
                                logger.error(
                                    f"Failed to validate missing producer (id: {prod_id}): {e}"
                                )
                    if len(missing_producers) > 0:
                        db.producer_controller.upsert_all(missing_producers)
                        existing_producer_ids = db.producer_controller.get_all_ids()
                    if len(anime_genres) > 0:
                        db.anime_tag_controller.upsert_all(anime_genres)
                    if len(anime_producers) > 0:
                        db.anime_producer_controller.upsert_all(anime_producers)

        progress_bar.update_progress(page)
        db.scraper_state_controller.upsert(endpoint=endpoint, state={"page": page})

        if "pagination" not in response or not response["pagination"].get(
            "has_next_page"
        ):
            break
        page += 1


def etl_jikan(db: Database, api_extractor: JikanApiExtractor) -> None:
    extract_data(
        db, api_extractor, JikanEndpoints.TAG_MANGA.value, TagModel, "TAG MANGA"
    )
    extract_data(
        db, api_extractor, JikanEndpoints.TAG_ANIME.value, TagModel, "TAG ANIME"
    )
    extract_data(
        db, api_extractor, JikanEndpoints.PRODUCERS.value, ProducerModel, "PRODUCERS"
    )
    extract_data(db, api_extractor, JikanEndpoints.ANIME.value, AnimeModel, "ANIME")
