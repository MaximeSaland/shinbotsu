import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import AuthorModel
from shinbotsu_data.database.db_models import Author
from shinbotsu_data.utils import remove_dict_with_duplicate_field


class AuthorController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, authors: list[AuthorModel]) -> None:
        """Insert authors in bulk
        :param authors: list of authors to insert
        """
        authors_orm = remove_dict_with_duplicate_field(
            [author.model_dump() for author in authors], duplicate_field="id"
        )
        with self._session_maker() as session:
            stmt = pg_insert(Author).values(authors_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Author.id],
                set_={"name": stmt.excluded.name},
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
