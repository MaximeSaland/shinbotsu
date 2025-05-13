import datetime
import logging
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from shinbotsu_data.database.db_models import ScraperState


class ScraperStateController:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    def upsert(self, endpoint: str, state: dict[str, Any]) -> None:
        """Update scraping progress for a given endpoint
        :param endpoint: endpoint being scrapped
        :param offset: last page or offset scrapped for this endpoint
        """
        with self._session_maker() as session:
            stmt = pg_insert(ScraperState).values(endpoint=endpoint, state=state)
            stmt = stmt.on_conflict_do_update(
                index_elements=[ScraperState.endpoint],
                set_={
                    "state": stmt.excluded.state,
                    "last_updated": datetime.datetime.now(datetime.timezone.utc),
                },
            )
            try:
                session.execute(stmt)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Insert failed: {e}")

    def get_state_by_endpoint(self, endpoint: str) -> dict[str, Any]:
        session: Session
        with self._session_maker() as session:
            try:
                res = (
                    session.query(ScraperState.state)
                    .filter_by(endpoint=endpoint)
                    .one_or_none()
                )
                if res:
                    return dict(res[0])
            except SQLAlchemyError as e:
                self.logger.error(f"Selecting scraper state by endpoint failed: {e}")
        return {}
