import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.database.db_models import People


class PeopleController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, people: list[dict[str, str | int | None]]) -> None:
        with self._session_maker() as session:
            stmt = pg_insert(People).values(people)
            stmt = stmt.on_conflict_do_update(
                index_elements=[People.id_mal],
                set_={
                    "name": stmt.excluded.name,
                    "given_name": stmt.excluded.given_name,
                    "family_name": stmt.excluded.family_name,
                    "url_img": stmt.excluded.url_img,
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
            return int(session.query(People).count())
