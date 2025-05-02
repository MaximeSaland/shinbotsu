import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.core.schemas import MangaModel
from shinbotsu_data.database.db_models import Manga
from shinbotsu_data.utils.helpers import remove_dict_with_duplicate_field


class MangaController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga: list[MangaModel]) -> None:
        manga_orm = remove_dict_with_duplicate_field(
            [m.model_dump(include=Manga.__table__.columns.keys()) for m in manga],
            duplicate_field="id",
        )
        with self._session_maker() as session:
            stmt = pg_insert(Manga).values(manga_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Manga.id],
                set_={
                    "title": stmt.excluded.title,
                    "title_jp": stmt.excluded.title_jp,
                    "synopsis": stmt.excluded.synopsis,
                    "synopsis_jp": stmt.excluded.synopsis_jp,
                    "last_volume": stmt.excluded.last_volume,
                    "last_chapter": stmt.excluded.last_chapter,
                    "demographic": stmt.excluded.demographic,
                    "status": stmt.excluded.status,
                    "publication_year": stmt.excluded.publication_year,
                    "rating": stmt.excluded.rating,
                    "id_anilist": stmt.excluded.id_anilist,
                    "id_amazon": stmt.excluded.id_amazon,
                    "id_bookwalker": stmt.excluded.id_bookwalker,
                    "id_mal": stmt.excluded.id_mal,
                },
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Bulk insert failed: {e}")
