from datetime import datetime
import logging

from pydantic import ValidationError
from shinbotsu_data.api.jikan import JikanApiExtractor
from shinbotsu_data.core.schemas import (
    AuthorModel,
    MangaAuthorModel,
    MangaModel,
    MangaRelationModel,
    MangaTagModel,
    TagMangadexModel,
)
from shinbotsu_data.database.database import Database
from shinbotsu_data.utils.constants import MangadexEndpoints
from shinbotsu_data.utils.progress_bar_helpers import ProgressBar

logger = logging.getLogger(__name__)


def split_list_into_chunks(arr: list[str], size: int) -> list[list[str]]:
    return [arr[i : i + size] for i in range(0, len(arr), size)]


def extract_tag(db: Database, api_extractor: JikanApiExtractor) -> None:
    response = api_extractor.fetch_data(MangadexEndpoints.TAG.value)
    tags: list[TagMangadexModel] = []
    progress_bar = ProgressBar(1, prefix="MANGA TAG")
    progress_bar.update_progress(0)
    if "data" in response:
        for tag in response["data"]:
            try:
                tags.append(TagMangadexModel.model_validate(tag))
            except ValidationError as e:
                logger.error(f"Failed to validate response data (id: {tag['id']}): {e}")
    db.tag_mangadex_controller.upsert_all(tags)
    progress_bar.update_progress(1)


def extract_manga_and_authors(db: Database, api_extractor: JikanApiExtractor) -> None:
    endpoint = MangadexEndpoints.MANGA.value
    page = 0
    limit = 100
    state = db.scraper_state_controller.get_state_by_endpoint(endpoint)
    page = state.get("page", 0)
    createdAtSince = state.get("createdAtSince", "")
    total_items = api_extractor.fetch_data(endpoint).get("total", 1)

    progress_bar = ProgressBar(total_items, prefix="MANGADEX - MANGA/AUTHOR ")
    progress_bar.update_progress(0)
    nb_iter = 0

    while True:
        params = {
            "limit": limit,
            "offset": limit * page,
            "order[createdAt]": "asc",
            "createdAtSince": createdAtSince,
            "includes[]": ["artist", "author", "manga"],
        }
        if len(createdAtSince) == 0:
            params.pop("createdAtSince")
        response = api_extractor.fetch_data(endpoint, params)
        total_items = response["total"] if "total" in response else 1
        if "data" in response:
            manga_list: list[MangaModel] = []
            for item in response["data"]:
                try:
                    manga_list.append(MangaModel.model_validate(item))
                except ValidationError as e:
                    logger.error(
                        f"Failed to validate response data (id: {item['id']}): {e}"
                    )

            manga_list.extend(
                [ma.manga_related for m in manga_list for ma in m.manga_relations]
            )

            authors: list[AuthorModel] = [
                ma.author for m in manga_list for ma in m.manga_authors
            ]
            manga_relations: list[MangaRelationModel] = [
                mr for m in manga_list for mr in m.manga_relations
            ]
            manga_authors: list[MangaAuthorModel] = [
                ma for m in manga_list for ma in m.manga_authors
            ]
            manga_tags: list[MangaTagModel] = [
                mt for m in manga_list for mt in m.manga_tags
            ]

            if authors:
                db.author_controller.upsert_all(authors)
            if manga_list:
                db.manga_controller.upsert_all(manga_list)
            if manga_relations:
                db.manga_relation_controller.upsert_all(manga_relations)
            if manga_tags:
                db.manga_tag_controller.upsert_all(manga_tags)
            if manga_authors:
                db.manga_author_controller.upsert_all(manga_authors)

        db.scraper_state_controller.upsert(
            endpoint=endpoint, state={"page": page, "createdAtSince": createdAtSince}
        )
        if endpoint == MangadexEndpoints.TAG.value or len(response) == 0:
            progress_bar.update_progress(total_items)
            break
        page += 1
        progress_bar.update_progress(page * limit + nb_iter * 10000)
        # cf. https://api.mangadex.org/docs/2-limitations/#collection-result-sizes
        if limit * page >= 10000:
            page = 0
            nb_iter += 1
            createdAtSince = response["data"][-1]["attributes"]["createdAt"]
            createdAtSince = datetime.fromisoformat(createdAtSince).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )


def etl_mangadex(db: Database, api_extractor: JikanApiExtractor) -> None:
    extract_tag(db, api_extractor)
    extract_manga_and_authors(db, api_extractor)
