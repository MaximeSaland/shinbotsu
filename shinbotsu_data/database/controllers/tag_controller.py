import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from shinbotsu_data.core.schemas import TagModel
from shinbotsu_data.database.db_models import Tag
from shinbotsu_data.utils import remove_dict_with_duplicate_field


class TagController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, tags: list[TagModel]) -> None:
        """Add tags in bulk
        :param tags: list of tags to insert
        """
        tags_orm = remove_dict_with_duplicate_field(
            [tag.model_dump() for tag in tags], duplicate_field="id_mal"
        )
        with self._session_maker() as session:
            stmt = pg_insert(Tag).values(tags_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Tag.id_mal], set_={"name": stmt.excluded.name}
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")

    def get_count(self) -> int:
        with self._session_maker() as session:
            return int(session.query(Tag).count())

    def get_all(self) -> list[TagModel]:
        with self._session_maker() as session:
            try:
                tags_orm = session.execute(select(Tag)).scalars().all()
                tags = [
                    TagModel.model_validate(tag_orm.__dict__) for tag_orm in tags_orm
                ]
                return tags
            except SQLAlchemyError as e:
                self.logger.error(f"Select all failed: {e}")
        return []
