import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, selectinload

from shinbotsu_data.core.schemas import AnimeModel
from shinbotsu_data.database.db_models import Anime
from shinbotsu_data.utils import remove_dict_with_duplicate_field


class AnimeController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert_all(self, anime: list[AnimeModel]) -> None:
        anime_orm = remove_dict_with_duplicate_field(
            [ani.model_dump(include=Anime.__table__.columns.keys()) for ani in anime],
            duplicate_field="id_mal",
        )
        with self._session_maker() as session:
            stmt = pg_insert(Anime).values(anime_orm)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Anime.id_mal],
                set_={
                    "title": stmt.excluded.title,
                    "title_jp": stmt.excluded.title_jp,
                    "type": stmt.excluded.type,
                    "source": stmt.excluded.source,
                    "episodes": stmt.excluded.episodes,
                    "status": stmt.excluded.status,
                    "aired_from": stmt.excluded.aired_from,
                    "aired_to": stmt.excluded.aired_to,
                    "rating": stmt.excluded.rating,
                    "synopsis": stmt.excluded.synopsis,
                    "season": stmt.excluded.season,
                    "year": stmt.excluded.year,
                    "url_mal": stmt.excluded.url_mal,
                    "url_img_jpg": stmt.excluded.url_img_jpg,
                    "url_img_jpg_small": stmt.excluded.url_img_jpg_small,
                    "url_img_jpg_large": stmt.excluded.url_img_jpg_large,
                    "url_img_webp": stmt.excluded.url_img_webp,
                    "url_img_webp_small": stmt.excluded.url_img_webp_small,
                    "url_img_webp_large": stmt.excluded.url_img_webp_large,
                    "youtube_trailer_id": stmt.excluded.youtube_trailer_id,
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
            return int(session.query(Anime).count())

    def get_all_with_relation(self) -> list[AnimeModel]:
        """Return the list of anime with their relations (tags and producers)"""
        with self._session_maker() as session:
            stmt = select(Anime).options(
                selectinload(Anime.anime_tag), selectinload(Anime.anime_producer)
            )
            try:
                anime_orm = session.execute(stmt).scalars().all()
                anime = []
                for ani_orm in anime_orm:
                    ani = ani_orm.__dict__
                    ani["producers"] = [
                        ap.id_producer
                        for ap in ani_orm.anime_producer
                        if ap.relation == "producer"
                    ]
                    ani["licensors"] = [
                        ap.id_producer
                        for ap in ani_orm.anime_producer
                        if ap.relation == "licensor"
                    ]
                    ani["studios"] = [
                        ap.id_producer
                        for ap in ani_orm.anime_producer
                        if ap.relation == "studio"
                    ]
                    ani["genres"] = [
                        at.id_tag for at in ani_orm.anime_tag if at.relation == "genre"
                    ]
                    ani["themes"] = [
                        at.id_tag for at in ani_orm.anime_tag if at.relation == "theme"
                    ]
                    ani["demographics"] = [
                        at.id_tag
                        for at in ani_orm.anime_tag
                        if at.relation == "demographic"
                    ]
                    anime.append(AnimeModel.model_validate(ani))
                return anime
            except SQLAlchemyError as e:
                self.logger.error(f"Failed to fetch all anime: {e}")
        return []
