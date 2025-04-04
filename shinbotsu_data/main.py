import logging

from shinbotsu_data.core.etl import etl_factory
from shinbotsu_data.database.database import Database
from shinbotsu_data.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()
    logger.info("Initializing database connection")
    db = Database(settings.db_uri)
    db.initialize_tables()

    scrapping_function = etl_factory(settings)
    scrapping_function(db)


if __name__ == "__main__":
    main()
