from typing import Any
import pytest
from faker import Faker

from shinbotsu_data.api.jikan import JikanApiExtractor, JikanEndpoints
from shinbotsu_data.core.etl.jikan import extract_data
from shinbotsu_data.core.schemas import (
    TagModel,
    ProducerModel,
    AnimeModel,
    AnimeTagModel,
    AnimeProducerModel,
)
from shinbotsu_data.database import Database
from tests.mock.api_jikan import JikanAPIMock
from tests.mock.mock_data_generator import (
    generate_fake_tag,
    generate_fake_producer,
    generate_fake_anime,
)

faker_tag = Faker()
faker_producer = Faker()
faker_anime = Faker()
[tag1, tag2, tag3, tag4] = [generate_fake_tag(faker_tag) for _ in range(4)]
tag1_updated = tag1.copy()
tag2_updated = tag2.copy()
tag1_updated["name"] = "tag 1 updated name"
tag2_updated["name"] = "tag 2 updated name"

[prod1, prod2, prod3, prod4] = [
    generate_fake_producer(faker_producer, 2) for _ in range(4)
]
prod1_updated = prod1.copy()
prod1_updated["titles"][0]["title"] = "prod1 updated title 1"
prod1_updated["titles"][1]["title"] = "prod1 updated title 1"
prod2_updated = prod2.copy()
prod2_updated["images"]["jpg"]["image_url"] = "https://new.url.com"
prod2_updated["about"] = "about updated"

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
ani1_updated = ani1.copy()
ani1_updated["title"] = "updated title ani 1"
ani1_updated["season"] = "updated season"
ani1_updated["episodes"] = 10000
ani2_updated = ani2.copy()
ani2_updated["title"] = "updated title ani 2"
ani2_updated["year"] = 2035
ani2_updated["status"] = "updated status"


@pytest.mark.parametrize(
    "initial_data, incoming_data, expected_data",
    [
        ([], [tag1, tag2], [tag1, tag2]),
        ([tag1, tag2], [tag3, tag4], [tag1, tag2, tag3, tag4]),
        ([tag1, tag2], [tag1, tag2], [tag1, tag2]),
        ([tag1, tag2], [tag2, tag3], [tag1, tag2, tag3]),
        (
            [tag1, tag2],
            [tag1_updated, tag2_updated, tag3],
            [tag1_updated, tag2_updated, tag3],
        ),
    ],
    ids=[
        "empty_state-new_inputs",
        "existing_state-new_inputs",
        "existing_state-same_inputs",
        "existing_state-mixed_inputs",
        "existing_state-updated_input",
    ],
)
def test_extract_data_tag(
    db: Database,
    jikan_api_extractor: JikanApiExtractor,
    initial_data: list[dict[str, int | str | None]],
    incoming_data: list[dict[str, int | str | None]],
    expected_data: list[dict[str, int | str | None]],
    mock_time_sleep: Any,
) -> None:
    if len(initial_data) > 0:
        db.tag_controller.upsert_all(
            [TagModel.model_validate(tag) for tag in initial_data]
        )

    with JikanAPIMock(tag_data=incoming_data):
        extract_data(
            db, jikan_api_extractor, JikanEndpoints.TAG_MANGA, TagModel, "test"
        )

    actual_data = sorted(db.tag_controller.get_all(), key=lambda tag: tag.id_mal)
    expected_data_sorted = sorted(
        [TagModel.model_validate(tag) for tag in expected_data],
        key=lambda tag: tag.id_mal,
    )

    assert actual_data == expected_data_sorted


@pytest.mark.parametrize(
    "initial_data, incoming_data, expected_data",
    [
        ([], [prod1, prod2], [prod1, prod2]),
        ([prod1, prod2], [prod3, prod4], [prod1, prod2, prod3, prod4]),
        ([prod1, prod2], [prod1, prod2], [prod1, prod2]),
        ([prod1, prod2], [prod2, prod3], [prod1, prod2, prod3]),
        (
            [prod1, prod2],
            [prod1_updated, prod2_updated, prod3],
            [prod1_updated, prod2_updated, prod3],
        ),
    ],
    ids=[
        "empty_state-new_inputs",
        "existing_state-new_inputs",
        "existing_state-same_inputs",
        "existing_state-mixed_inputs",
        "existing_state-updated_input",
    ],
)
def test_extract_data_producer(
    db: Database,
    jikan_api_extractor: JikanApiExtractor,
    initial_data: list[dict[str, int | str | None]],
    incoming_data: list[dict[str, int | str | None]],
    expected_data: list[dict[str, int | str | None]],
    mock_time_sleep: Any,
) -> None:
    if len(initial_data) > 0:
        db.producer_controller.upsert_all(
            [ProducerModel.model_validate(producer) for producer in initial_data]
        )

    with JikanAPIMock(producer_data=incoming_data):
        extract_data(
            db,
            jikan_api_extractor,
            JikanEndpoints.PRODUCERS.value,
            ProducerModel,
            "test",
        )

    actual_data = sorted(db.producer_controller.get_all(), key=lambda prod: prod.id_mal)
    expected_data_sorted = sorted(
        [ProducerModel.model_validate(prod) for prod in expected_data],
        key=lambda prod: prod.id_mal,
    )

    assert actual_data == expected_data_sorted


@pytest.mark.parametrize(
    "initial_data, incoming_data, expected_data",
    [
        ([], [ani1, ani2], [ani1, ani2]),
        ([ani1, ani2], [ani3, ani4], [ani1, ani2, ani3, ani4]),
        ([ani1, ani2], [ani1, ani2], [ani1, ani2]),
        ([ani1, ani2], [ani2, ani3], [ani1, ani2, ani3]),
        (
            [ani1, ani2],
            [ani1_updated, ani2_updated, ani3],
            [ani1_updated, ani2_updated, ani3],
        ),
    ],
    ids=[
        "empty_state-new_inputs",
        "existing_state-new_inputs",
        "existing_state-same_inputs",
        "existing_state-mixed_inputs",
        "existing_state-updated_input",
    ],
)
def test_extract_data_anime(
    db: Database,
    jikan_api_extractor: JikanApiExtractor,
    initial_data: list[dict[str, int | str | None]],
    incoming_data: list[dict[str, int | str | None]],
    expected_data: list[dict[str, int | str | None]],
    mock_time_sleep: Any,
) -> None:
    db.tag_controller.upsert_all(
        [TagModel.model_validate(t) for t in [tag1, tag2, tag3, tag4]]
    )
    db.producer_controller.upsert_all(
        [ProducerModel.model_validate(p) for p in [prod1, prod2, prod3, prod4]]
    )
    if len(initial_data) > 0:
        validated_initial_data = [
            AnimeModel.model_validate(ani) for ani in initial_data
        ]
        anime_genres = []
        anime_producers = []
        for anime in validated_initial_data:
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
        db.anime_controller.upsert_all(validated_initial_data)
        db.anime_tag_controller.upsert_all(anime_genres)
        db.anime_producer_controller.upsert_all(anime_producers)

    with JikanAPIMock(anime_data=incoming_data):
        extract_data(
            db, jikan_api_extractor, JikanEndpoints.ANIME.value, AnimeModel, "test"
        )

    actual_data = sorted(
        db.anime_controller.get_all_with_relation(), key=lambda ani: ani.id_mal
    )
    expected_data_sorted = sorted(
        [AnimeModel.model_validate(ani) for ani in expected_data],
        key=lambda ani: ani.id_mal,
    )

    assert actual_data == expected_data_sorted
