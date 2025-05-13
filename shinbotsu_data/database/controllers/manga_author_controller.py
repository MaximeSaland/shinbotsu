import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MangaAuthorModel
from shinbotsu_data.database.db_models import MangaAuthor


class MangaAuthorController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga_authors: list[MangaAuthorModel]) -> None:
        fields = {col for col in MangaAuthor.__table__.columns.keys()}
        manga_authors_orm = [
            manga_author.model_dump(include=fields) for manga_author in manga_authors
        ]
        with self._session_maker() as session:
            stmt = pg_insert(MangaAuthor).values(manga_authors_orm)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[
                    MangaAuthor.id_manga,
                    MangaAuthor.id_author,
                    MangaAuthor.relation,
                ]
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
