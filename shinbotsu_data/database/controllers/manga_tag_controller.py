import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MangaTagModel
from shinbotsu_data.database.db_models import MangaTag


class MangaTagController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_tags: list[MangaTagModel]) -> None:
        fields = {col for col in MangaTag.__table__.columns.keys()}
        manga_tags_orm = [
            manga_tag.model_dump(include=fields) for manga_tag in manga_tags
        ]
        with self._session_maker() as session:
            stmt = pg_insert(MangaTag).values(manga_tags_orm)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[MangaTag.id_manga, MangaTag.id_tag]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
