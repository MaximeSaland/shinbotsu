import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.database.db_models import Anime, MangaPeople


class MangaPeopleController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_people: list[dict[str, int]]) -> None:
        with self._session_maker() as session:
            stmt = pg_insert(MangaPeople).values(manga_people)
            stmt = stmt.on_conflict_do_nothing(index_elements=[Anime.id_mal])
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(MangaPeople).count())
