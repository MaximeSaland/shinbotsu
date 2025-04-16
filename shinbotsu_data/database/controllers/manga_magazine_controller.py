import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.database.db_models import MangaMagazine


class MangaMagazineController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_magazine: list[dict[str, str | int | None]]) -> None:
        with self._session_maker() as session:
            stmt = pg_insert(MangaMagazine).values(manga_magazine)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[MangaMagazine.id_manga, MangaMagazine.id_magazine]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(MangaMagazine).count())
