import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MangaRelationModel
from shinbotsu_data.database.db_models import MangaRelation


class MangaRelationController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_relations: list[MangaRelationModel]) -> None:
        fields = {col for col in MangaRelation.__table__.columns.keys()}
        manga_relations_orm = [
            manga_relation.model_dump(include=fields)
            for manga_relation in manga_relations
        ]
        with self._session_maker() as session:
            stmt = pg_insert(MangaRelation).values(manga_relations_orm)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    MangaRelation.id_manga,
                    MangaRelation.id_manga_related,
                ]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
