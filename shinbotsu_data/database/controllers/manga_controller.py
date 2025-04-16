import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from shinbotsu_data.database.db_models import Manga


class MangaController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, manga: list[dict[str, str | int | None]]) -> None:
        with self._session_maker() as session:
            stmt = pg_insert(Manga).values(manga)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Manga.id_mal],
                set_={
                    "title": stmt.excluded.title,
                    "title_jp": stmt.excluded.title_jp,
                    "type": stmt.excluded.type,
                    "chapters": stmt.excluded.chapters,
                    "volumes": stmt.excluded.volumes,
                    "status": stmt.excluded.status,
                    "published_from": stmt.excluded.published_from,
                    "published_to": stmt.excluded.published_to,
                    "synopsis": stmt.excluded.synopsis,
                    "url_mal": stmt.excluded.url_mal,
                    "url_img_jpg": stmt.excluded.url_img_jpg,
                    "url_img_jpg_small": stmt.excluded.url_img_jpg_small,
                    "url_img_jpg_large": stmt.excluded.url_img_jpg_large,
                    "url_img_webp": stmt.excluded.url_img_webp,
                    "url_img_webp_small": stmt.excluded.url_img_webp_small,
                    "url_img_webp_large": stmt.excluded.url_img_webp_large,
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
            return int(session.query(Manga).count())
