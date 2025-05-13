from typing import Any, Optional
from unittest.mock import MagicMock
from faker import Faker
import pytest

from shinbotsu_data.core.etl.jikan import extract_data
from shinbotsu_data.core.schemas import AnimeModel, ProducerModel, TagModel
from shinbotsu_data.utils.constants import JikanEndpoints
from tests.mock.mock_data_generator import (
    generate_fake_anime,
    generate_fake_producer,
    generate_fake_tag,
)


faker_tag = Faker()
faker_producer = Faker()
faker_anime = Faker()
[tag1, tag2, tag3, tag4] = [generate_fake_tag(faker_tag) for _ in range(4)]

[prod1, prod2, prod3, prod4] = [
    generate_fake_producer(faker_producer, 2) for _ in range(4)
]

ani1 = generate_fake_anime(
    fake=faker_anime,
    producers=[ProducerModel.model_validate(prod) for prod in [prod1]],
    licensors=[ProducerModel.model_validate(prod) for prod in [prod2]],
    studios=[ProducerModel.model_validate(prod) for prod in [prod4]],
    genres=[TagModel.model_validate(tag) for tag in [tag4]],
    themes=[],
    demographics=[],
)
ani2 = generate_fake_anime(
    fake=faker_anime,
    producers=[ProducerModel.model_validate(prod) for prod in [prod2]],
    licensors=[ProducerModel.model_validate(prod) for prod in [prod2]],
    studios=[ProducerModel.model_validate(prod) for prod in [prod2]],
    genres=[],
    themes=[TagModel.model_validate(tag) for tag in [tag1, tag3]],
    demographics=[TagModel.model_validate(tag) for tag in [tag2]],
)
ani3 = generate_fake_anime(
    fake=faker_anime,
    producers=[ProducerModel.model_validate(prod) for prod in [prod1, prod2]],
    licensors=[ProducerModel.model_validate(prod) for prod in [prod3]],
    studios=[ProducerModel.model_validate(prod) for prod in [prod4]],
    genres=[TagModel.model_validate(tag) for tag in [tag1]],
    themes=[TagModel.model_validate(tag) for tag in [tag2]],
    demographics=[TagModel.model_validate(tag) for tag in [tag3]],
)
ani4 = generate_fake_anime(
    fake=faker_anime,
    producers=[ProducerModel.model_validate(prod) for prod in [prod4]],
    licensors=[ProducerModel.model_validate(prod) for prod in [prod1]],
    studios=[ProducerModel.model_validate(prod) for prod in [prod3]],
    genres=[TagModel.model_validate(tag) for tag in [tag1, tag2, tag3]],
    themes=[TagModel.model_validate(tag) for tag in [tag4]],
    demographics=[],
)
prods = [prod1, prod2, prod3, prod4]
tags = [tag1, tag2, tag3, tag4]
anime = [ani1, ani2, ani3, ani4]


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_api_extractor() -> MagicMock:
    return MagicMock()


def test_extract_data_producers(
    mock_db: MagicMock, mock_api_extractor: MagicMock
) -> None:
    mock_producer_controller = MagicMock()
    mock_scraper_state_controller = MagicMock()
    mock_scraper_state_controller.get_state_by_endpoint.return_value = None
    mock_db.producer_controller = mock_producer_controller
    mock_db.scraper_state_controller = mock_scraper_state_controller
    mock_db.scraper_state_controller.get_state_by_endpoint.return_value = {"page": 1}

    def get_side_effect(endpoint: str, params: dict[str, int | bool]) -> dict[str, Any]:
        if params["page"] == 1:
            return {
                "pagination": {"last_visible_page": 2, "has_next_page": True},
                "data": [prod1, prod2],
            }
        elif params["page"] == 2:
            return {
                "pagination": {"last_visible_page": 2, "has_next_page": False},
                "data": [prod3, prod4],
            }
        return {}

    mock_api_extractor.fetch_data.side_effect = get_side_effect
    extract_data(
        mock_db,
        mock_api_extractor,
        JikanEndpoints.PRODUCERS.value,
        ProducerModel,
        "test",
    )

    assert mock_api_extractor.fetch_data.call_count == 3
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.PRODUCERS.value, {"page": 1}
    )
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.PRODUCERS.value, {"page": 2}
    )
    assert mock_producer_controller.upsert_all.call_count == 2
    mock_producer_controller.upsert_all.assert_any_call(
        [ProducerModel.model_validate(p) for p in [prod1, prod2]]
    )
    mock_producer_controller.upsert_all.assert_any_call(
        [ProducerModel.model_validate(p) for p in [prod3, prod4]]
    )


def test_extract_data_tags(mock_db: MagicMock, mock_api_extractor: MagicMock) -> None:
    mock_tag_controller = MagicMock()
    mock_scraper_state_controller = MagicMock()
    mock_scraper_state_controller.get_state_by_endpoint.return_value = None
    mock_db.tag_controller = mock_tag_controller
    mock_db.scraper_state_controller = mock_scraper_state_controller
    mock_db.scraper_state_controller.get_state_by_endpoint.return_value = {"page": 1}

    def get_side_effect(endpoint: str, params: dict[str, int | bool]) -> dict[str, Any]:
        if params["page"] == 1:
            return {
                "pagination": {"last_visible_page": 2, "has_next_page": True},
                "data": [tag1, tag2],
            }
        elif params["page"] == 2:
            return {
                "pagination": {"last_visible_page": 2, "has_next_page": False},
                "data": [tag3, tag4],
            }
        return {}

    mock_api_extractor.fetch_data.side_effect = get_side_effect

    extract_data(
        mock_db, mock_api_extractor, JikanEndpoints.TAG_MANGA.value, TagModel, "test"
    )

    assert mock_api_extractor.fetch_data.call_count == 3
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.TAG_MANGA.value, {"page": 1}
    )
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.TAG_MANGA.value, {"page": 2}
    )
    assert mock_tag_controller.upsert_all.call_count == 2
    mock_tag_controller.upsert_all.assert_any_call(
        [TagModel.model_validate(t) for t in [tag1, tag2]]
    )
    mock_tag_controller.upsert_all.assert_any_call(
        [TagModel.model_validate(t) for t in [tag3, tag4]]
    )


def test_extract_data_anime(mock_db: MagicMock, mock_api_extractor: MagicMock) -> None:
    mock_anime_controller = MagicMock()
    mock_anime_tag_controller = MagicMock()
    mock_anime_producer_controller = MagicMock()
    mock_producer_controller = MagicMock()
    mock_producer_controller.get_all_ids.side_effect = [
        [prod1["mal_id"], prod2["mal_id"], prod3["mal_id"]],
        [prod1["mal_id"], prod2["mal_id"], prod3["mal_id"], prod4["mal_id"]],
    ]
    mock_scraper_state_controller = MagicMock()
    mock_scraper_state_controller.get_state_by_endpoint.return_value = None
    mock_db.anime_controller = mock_anime_controller
    mock_db.scraper_state_controller = mock_scraper_state_controller
    mock_db.scraper_state_controller.get_state_by_endpoint.return_value = {"page": 1}
    mock_db.anime_tag_controller = mock_anime_tag_controller
    mock_db.anime_producer_controller = mock_anime_producer_controller
    mock_db.producer_controller = mock_producer_controller

    def get_side_effect(
        endpoint: str, params: Optional[dict[str, int | bool]] = None
    ) -> dict[str, Any]:
        if endpoint == JikanEndpoints.ANIME.value:
            if params is not None and params["page"] == 1:
                return {
                    "pagination": {"last_visible_page": 2, "has_next_page": True},
                    "data": [ani1, ani2],
                }
            elif params is not None and params["page"] == 2:
                return {
                    "pagination": {"last_visible_page": 2, "has_next_page": False},
                    "data": [ani3, ani4],
                }
        elif endpoint.startswith(JikanEndpoints.PRODUCERS.value):
            return {"data": prod4}
        return {}

    mock_api_extractor.fetch_data.side_effect = get_side_effect

    extract_data(
        mock_db, mock_api_extractor, JikanEndpoints.ANIME.value, AnimeModel, "test"
    )

    assert mock_api_extractor.fetch_data.call_count == 4
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.ANIME.value, {"page": 1}
    )
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.ANIME.value, {"page": 2}
    )
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.PRODUCERS.value + f"/{prod4['mal_id']}"
    )
    assert mock_anime_controller.upsert_all.call_count == 2
    mock_anime_controller.upsert_all.assert_any_call(
        [AnimeModel.model_validate(a) for a in [ani1, ani2]]
    )
    mock_anime_controller.upsert_all.assert_any_call(
        [AnimeModel.model_validate(a) for a in [ani3, ani4]]
    )
    assert mock_producer_controller.get_all_ids.call_count == 2


def test_extract_data_tags_existing_scraper_state(
    mock_db: MagicMock, mock_api_extractor: MagicMock
) -> None:
    mock_tag_controller = MagicMock()
    mock_scraper_state_controller = MagicMock()
    mock_scraper_state_controller.get_state_by_endpoint.return_value = 2
    mock_db.tag_controller = mock_tag_controller
    mock_db.scraper_state_controller = mock_scraper_state_controller
    mock_db.scraper_state_controller.get_state_by_endpoint.return_value = {"page": 2}

    def get_side_effect(endpoint: str, params: dict[str, int | bool]) -> dict[str, Any]:
        if params["page"] == 1:
            return {
                "pagination": {"last_visible_page": 3, "has_next_page": True},
                "data": [tag1],
            }
        elif params["page"] == 2:
            return {
                "pagination": {"last_visible_page": 3, "has_next_page": True},
                "data": [tag2],
            }
        elif params["page"] == 3:
            return {
                "pagination": {"last_visible_page": 3, "has_next_page": False},
                "data": [tag3],
            }
        return {}

    mock_api_extractor.fetch_data.side_effect = get_side_effect

    extract_data(
        mock_db, mock_api_extractor, JikanEndpoints.TAG_MANGA.value, TagModel, "test"
    )

    assert mock_api_extractor.fetch_data.call_count == 3
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.TAG_MANGA.value, {"page": 2}
    )
    mock_api_extractor.fetch_data.assert_any_call(
        JikanEndpoints.TAG_MANGA.value, {"page": 3}
    )
    assert mock_tag_controller.upsert_all.call_count == 2
    mock_tag_controller.upsert_all.assert_any_call(
        [TagModel.model_validate(t) for t in [tag2]]
    )
    mock_tag_controller.upsert_all.assert_any_call(
        [TagModel.model_validate(t) for t in [tag3]]
    )
