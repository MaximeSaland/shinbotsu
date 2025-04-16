import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import ProducerModel
from shinbotsu_data.database.db_models import Producer


class ProducerController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, producers: list[ProducerModel]) -> None:
        """Insert producers in bulk
        :param producers: list of producers to insert
        """
        producers_orm = [producer.model_dump() for producer in producers]
        with self._session_maker() as session:
            stmt = pg_insert(Producer).values(producers_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Producer.id_mal],
                set_={
                    "title": stmt.excluded.title,
                    "title_jp": stmt.excluded.title_jp,
                    "url_img": stmt.excluded.url_img,
                    "about": stmt.excluded.about,
                    "established": stmt.excluded.established,
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
            return int(session.query(Producer).count())

    def get_all(self) -> list[ProducerModel]:
        with self._session_maker() as session:
            try:
                producers_orm = session.execute(select(Producer)).scalars().all()
                producers = [
                    ProducerModel.model_validate(producer_orm.__dict__)
                    for producer_orm in producers_orm
                ]
                return producers
            except SQLAlchemyError as e:
                self.logger.error(f"Select all failed: {e}")
        return []
