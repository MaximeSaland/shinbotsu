import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MagazineModel
from shinbotsu_data.database.db_models import Magazine


class MagazineController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, magazines: list[MagazineModel]) -> None:
        magazines_orm = [magazine.model_dump() for magazine in magazines]
        with self._session_maker() as session:
            stmt = pg_insert(Magazine).values(magazines_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Magazine.id_mal],
                set_={
                    "name": stmt.excluded.name,
                },
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(Magazine).count())
