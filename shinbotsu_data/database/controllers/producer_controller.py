import logging
from typing import cast

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import ProducerModel
from shinbotsu_data.database.db_models import Producer
from shinbotsu_data.utils import remove_dict_with_duplicate_field


class ProducerController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, producers: list[ProducerModel]) -> None:
        """Insert producers in bulk
        :param producers: list of producers to insert
        """
        producers_orm = remove_dict_with_duplicate_field(
            [producer.model_dump() for producer in producers], duplicate_field="id_mal"
        )
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

    def get_all_ids(self) -> list[int]:
        with self._session_maker() as session:
            try:
                ids = session.execute(select(Producer.id_mal)).scalars().all()
                return cast(list[int], ids)
            except SQLAlchemyError as e:
                self.logger.error(f"Select all ids failed: {e}")
        return []
