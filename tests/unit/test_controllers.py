from unittest.mock import MagicMock, patch

import pytest
from faker.proxy import Faker
from sqlalchemy.exc import SQLAlchemyError

from shinbotsu_data.core.schemas import (
    TagModel,
    ProducerModel,
    AnimeModel,
    AnimeTagModel,
    AnimeProducerModel,
)
from shinbotsu_data.database.controllers import TagController
from shinbotsu_data.database.controllers.anime_controller import AnimeController
from shinbotsu_data.database.controllers.anime_producer_controller import (
    AnimeProducerController,
)
from shinbotsu_data.database.controllers.anime_tag_controller import AnimeTagController
from shinbotsu_data.database.controllers.producer_controller import ProducerController
from shinbotsu_data.database.db_models import (
    Tag,
    Producer,
    Anime,
    AnimeTag,
    AnimeProducer,
)
from tests.mock.mock_data_generator import (
    generate_fake_tag,
    generate_fake_producer,
    generate_fake_anime,
)


@pytest.fixture
def mock_session_and_maker() -> tuple[MagicMock, MagicMock]:
    mock_session = MagicMock()
    mock_session_maker = MagicMock()
    mock_session_maker.return_value.__enter__.return_value = mock_session
    return mock_session, mock_session_maker


def test_tag_controller_upsert_all_success(
    mock_session_and_maker: tuple[MagicMock, MagicMock], faker_tag: Faker
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    tag_controller = TagController(mock_session_maker)

    tags = [TagModel.model_validate(generate_fake_tag(faker_tag)) for _ in range(2)]

    with patch(
        "shinbotsu_data.database.controllers.tag_controller.pg_insert"
    ) as mock_pg_insert:
        stmt_mock = MagicMock()
        mock_pg_insert.return_value = stmt_mock
        stmt_mock.values.return_value = stmt_mock
        stmt_mock.on_conflict_do_update.return_value = stmt_mock
        excluded_mock = MagicMock()
        stmt_mock.excluded = excluded_mock

        tag_controller.upsert_all(tags)

        mock_pg_insert.assert_called_once_with(Tag)
        stmt_mock.values.rssert_called_once_with([tag.model_dump() for tag in tags])
        stmt_mock.on_conflict_do_update.assert_called_once_with(
            index_elements=[Tag.id_mal], set_={"name": stmt_mock.excluded.name}
        )
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()


def test_tag_controller_upsert_all_failure(
    mock_session_and_maker: tuple[MagicMock, MagicMock], faker_tag: Faker
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")
    tag_controller = TagController(mock_session_maker)
    mock_logger = MagicMock()
    tag_controller.logger = mock_logger

    tags = [TagModel.model_validate(generate_fake_tag(faker_tag)) for _ in range(2)]

    with patch(
        "shinbotsu_data.database.controllers.tag_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_update.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        tag_controller.upsert_all(tags)

        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called_once()


def test_producer_controller_upsert_all_success(
    mock_session_and_maker: tuple[MagicMock, MagicMock], faker_producer: Faker
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = ProducerController(mock_session_maker)

    producers = [
        ProducerModel.model_validate(generate_fake_producer(faker_producer, 2))
        for _ in range(2)
    ]

    with patch(
        "shinbotsu_data.database.controllers.producer_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_update.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(producers)

        mock_pg_insert.assert_called_once_with(Producer)
        mock_stmt.values.assert_called_once_with(
            [producer.model_dump() for producer in producers]
        )
        mock_stmt.on_conflict_do_update.assert_called_once_with(
            index_elements=[Producer.id_mal],
            set_={
                "title": mock_stmt.excluded.title,
                "title_jp": mock_stmt.excluded.title_jp,
                "url_img": mock_stmt.excluded.url_img,
                "about": mock_stmt.excluded.about,
                "established": mock_stmt.excluded.established,
            },
        )
        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_called_once()


def test_producer_controller_upsert_all_failure(
    mock_session_and_maker: tuple[MagicMock, MagicMock], faker_producer: Faker
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")
    mock_logger = MagicMock()
    mock_controller = ProducerController(mock_session_maker)
    mock_controller.logger = mock_logger

    producers = [
        ProducerModel.model_validate(generate_fake_producer(faker_producer, 2))
        for _ in range(2)
    ]

    with patch(
        "shinbotsu_data.database.controllers.producer_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_update.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(producers)

        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called_once()


def test_anime_controller_upsert_all_success(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
    faker_tag: Faker,
    faker_producer: Faker,
    faker_anime: Faker,
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeController(mock_session_maker)

    tags = [TagModel.model_validate(generate_fake_tag(faker_tag)) for _ in range(5)]
    producers = [
        ProducerModel.model_validate(generate_fake_producer(faker_producer, 2))
        for _ in range(5)
    ]

    anime = [
        AnimeModel.model_validate(
            generate_fake_anime(
                faker_anime,
                producers=producers[:2],
                licensors=producers[2:3],
                studios=producers[3:4],
                genres=tags[:3],
                themes=tags[3:4],
            )
        ),
        AnimeModel.model_validate(
            generate_fake_anime(
                faker_anime,
                producers=producers[4:],
                licensors=producers[3:4],
                studios=producers[1:3],
                genres=tags[2:4],
                themes=tags[1:2],
                demographics=tags[4:],
            )
        ),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_update.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(anime)

        mock_pg_insert.assert_called_once_with(Anime)
        mock_stmt.values.assert_called_once_with(
            [ani.model_dump(include=Anime.__table__.columns.keys()) for ani in anime]
        )
        mock_stmt.on_conflict_do_update.assert_called_once_with(
            index_elements=[Anime.id_mal],
            set_={
                "title": mock_stmt.excluded.title,
                "title_jp": mock_stmt.excluded.title_jp,
                "type": mock_stmt.excluded.type,
                "source": mock_stmt.excluded.source,
                "episodes": mock_stmt.excluded.episodes,
                "status": mock_stmt.excluded.status,
                "aired_from": mock_stmt.excluded.aired_from,
                "aired_to": mock_stmt.excluded.aired_to,
                "rating": mock_stmt.excluded.rating,
                "synopsis": mock_stmt.excluded.synopsis,
                "season": mock_stmt.excluded.season,
                "year": mock_stmt.excluded.year,
                "url_mal": mock_stmt.excluded.url_mal,
                "url_img_jpg": mock_stmt.excluded.url_img_jpg,
                "url_img_jpg_small": mock_stmt.excluded.url_img_jpg_small,
                "url_img_jpg_large": mock_stmt.excluded.url_img_jpg_large,
                "url_img_webp": mock_stmt.excluded.url_img_webp,
                "url_img_webp_small": mock_stmt.excluded.url_img_webp_small,
                "url_img_webp_large": mock_stmt.excluded.url_img_webp_large,
                "youtube_trailer_id": mock_stmt.excluded.youtube_trailer_id,
            },
        )
        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_called_once()


def test_anime_controller_upsert_all_failure(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
    faker_tag: Faker,
    faker_producer: Faker,
    faker_anime: Faker,
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeController(mock_session_maker)
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")
    mock_logger = MagicMock()
    mock_controller.logger = mock_logger

    tags = [TagModel.model_validate(generate_fake_tag(faker_tag)) for _ in range(5)]
    producers = [
        ProducerModel.model_validate(generate_fake_producer(faker_producer, 2))
        for _ in range(5)
    ]

    anime = [
        AnimeModel.model_validate(
            generate_fake_anime(
                faker_anime,
                producers=producers[:2],
                licensors=producers[2:3],
                studios=producers[3:4],
                genres=tags[:3],
                themes=tags[3:4],
            )
        ),
        AnimeModel.model_validate(
            generate_fake_anime(
                faker_anime,
                producers=producers[4:],
                licensors=producers[3:4],
                studios=producers[1:3],
                genres=tags[2:4],
                themes=tags[1:2],
                demographics=tags[4:],
            )
        ),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_update.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(anime)

        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called_once()


def test_anime_tag_controller_upsert_all_success(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeTagController(mock_session_maker)

    anime_tags = [
        AnimeTagModel(id_anime=1, id_tag=1, relation="genre"),
        AnimeTagModel(id_anime=1, id_tag=2, relation="theme"),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_tag_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_nothing.return_value = mock_stmt

        mock_controller.upsert_all(anime_tags)

        mock_pg_insert.assert_called_once_with(AnimeTag)
        mock_stmt.values.assert_called_once_with(
            [anime_tag.model_dump() for anime_tag in anime_tags]
        )
        mock_stmt.on_conflict_do_nothing.assert_called_once_with(
            index_elements=[AnimeTag.id_anime, AnimeTag.id_tag]
        )
        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_called_once()


def test_anime_tag_controller_upsert_all_failure(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeTagController(mock_session_maker)
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")
    mock_logger = MagicMock()
    mock_controller.logger = mock_logger

    anime_tags = [
        AnimeTagModel(id_anime=1, id_tag=1, relation="genre"),
        AnimeTagModel(id_anime=1, id_tag=2, relation="theme"),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_tag_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_nothing.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(anime_tags)

        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called_once()


def test_anime_producer_controller_upsert_all_success(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeProducerController(mock_session_maker)

    anime_producers = [
        AnimeProducerModel(id_anime=1, id_producer=1, relation="studio"),
        AnimeProducerModel(id_anime=1, id_producer=2, relation="producer"),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_producer_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_nothing.return_value = mock_stmt

        mock_controller.upsert_all(anime_producers)

        mock_pg_insert.assert_called_once_with(AnimeProducer)
        mock_stmt.values.assert_called_once_with(
            [anime_producer.model_dump() for anime_producer in anime_producers]
        )
        mock_stmt.on_conflict_do_nothing.assert_called_once_with(
            index_elements=[
                AnimeProducer.id_anime,
                AnimeProducer.id_producer,
                AnimeProducer.relation,
            ]
        )
        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_called_once()


def test_anime_producer_controller_upsert_all_failure(
    mock_session_and_maker: tuple[MagicMock, MagicMock],
) -> None:
    mock_session, mock_session_maker = mock_session_and_maker
    mock_controller = AnimeProducerController(mock_session_maker)
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")
    mock_logger = MagicMock()
    mock_controller.logger = mock_logger

    anime_producers = [
        AnimeProducerModel(id_anime=1, id_producer=1, relation="studio"),
        AnimeProducerModel(id_anime=1, id_producer=2, relation="producer"),
    ]

    with patch(
        "shinbotsu_data.database.controllers.anime_producer_controller.pg_insert"
    ) as mock_pg_insert:
        mock_stmt = MagicMock()
        mock_pg_insert.return_value = mock_stmt
        mock_stmt.values.return_value = mock_stmt
        mock_stmt.on_conflict_do_nothing.return_value = mock_stmt
        mock_excluded = MagicMock()
        mock_stmt.excluded = mock_excluded

        mock_controller.upsert_all(anime_producers)

        mock_session.execute.assert_called_once_with(mock_stmt)
        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_logger.error.assert_called_once()
