import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import AnimeProducerModel
from shinbotsu_data.database.db_models import AnimeProducer


class AnimeProducerController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, anime_producers: list[AnimeProducerModel]) -> None:
        anime_producers_orm = [
            anime_producer.model_dump() for anime_producer in anime_producers
        ]
        with self._session_maker() as session:
            stmt = pg_insert(AnimeProducer).values(anime_producers_orm)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    AnimeProducer.id_anime,
                    AnimeProducer.id_producer,
                    AnimeProducer.relation,
                ]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(AnimeProducer).count())
