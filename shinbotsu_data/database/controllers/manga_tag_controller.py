import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MangaTagModel


class MangaTagController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_tag: list[MangaTagModel]) -> None:
        with self._session_maker() as session:
            stmt = pg_insert(MangaTagModel).values(manga_tag)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[MangaTagModel.id_manga, MangaTagModel.id_tag]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
