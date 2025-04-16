import logging
from typing import TypeVar, Type, cast

from pydantic import ValidationError

from shinbotsu_data.api.jikan import JikanApiExtractor, JikanEndpoints
from shinbotsu_data.core.schemas import (
    TagModel,
    BaseDataModel,
    ProducerModel,
    AnimeModel,
    AnimeTagModel,
    AnimeProducerModel,
)
from shinbotsu_data.database.database import Database
from shinbotsu_data.utils.progress_bar_helpers import ProgressBar

logger = logging.getLogger(__name__)

ValidationModel = TypeVar("ValidationModel", bound=BaseDataModel)

# TODO add scrapping for anime currently airing
# TODO add scrapping from last page scrapped


def extract_data(
    db: Database,
    api_extractor: JikanApiExtractor,
    endpoint: str,
    validation_model: Type[ValidationModel],
    prefix: str,
) -> None:
    """Function to extract"""
    page = 1
    while True:
        # TODO Add progress logic (progress bar + save progress in case of interruption)
        # TODO Add update logic (check if number of items is different in response and database)
        response = api_extractor.fetch_data(endpoint, {"page": page})
        total_pages = (
            response["pagination"].get("last_visible_page")
            if "pagination" in response
            else 1
        )
        progress_bar = ProgressBar(total_pages, prefix=f"JIKAN - {prefix} ")
        progress_bar.update_progress(0)
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
            match endpoint:
                case JikanEndpoints.TAG_MANGA.value:
                    db.tag_controller.upsert_all(cast(list[TagModel], validated_items))
                case JikanEndpoints.PRODUCERS.value:
                    db.producer_controller.upsert_all(
                        cast(list[ProducerModel], validated_items)
                    )
                case JikanEndpoints.ANIME.value:
                    db.anime_controller.upsert_all(
                        cast(list[AnimeModel], validated_items)
                    )
                    anime_genres = []
                    anime_producers = []
                    for ani in validated_items:
                        anime = cast(AnimeModel, ani)
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
                    db.anime_tag_controller.upsert_all(anime_genres)
                    db.anime_producer_controller.upsert_all(anime_producers)
        progress_bar.update_progress(page)
        if "pagination" not in response or not response["pagination"].get(
            "has_next_page"
        ):
            break
        page += 1


def etl_jikan(db: Database, api_extractor: JikanApiExtractor) -> None:
    extract_data(db, api_extractor, JikanEndpoints.TAG_MANGA.value, TagModel, "TAG")
    extract_data(
        db, api_extractor, JikanEndpoints.PRODUCERS.value, ProducerModel, "PRODUCERS"
    )
    extract_data(db, api_extractor, JikanEndpoints.ANIME.value, AnimeModel, "ANIME")
