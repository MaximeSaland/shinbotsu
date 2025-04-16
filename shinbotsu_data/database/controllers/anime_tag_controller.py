import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import AnimeTagModel
from shinbotsu_data.database.db_models import AnimeTag


class AnimeTagController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, anime_tags: list[AnimeTagModel]) -> None:
        anime_tags_orm = [anime_tag.model_dump() for anime_tag in anime_tags]
        with self._session_maker() as session:
            stmt = pg_insert(AnimeTag).values(anime_tags_orm)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[AnimeTag.id_anime, AnimeTag.id_tag]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(AnimeTag).count())
