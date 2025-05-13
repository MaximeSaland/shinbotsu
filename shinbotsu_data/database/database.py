from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from shinbotsu_data.database.controllers import TagController
from shinbotsu_data.database.controllers.anime_controller import AnimeController
from shinbotsu_data.database.controllers.anime_producer_controller import (
    AnimeProducerController,
)
from shinbotsu_data.database.controllers.anime_tag_controller import AnimeTagController
from shinbotsu_data.database.controllers.author_controller import AuthorController
from shinbotsu_data.database.controllers.manga_author_controller import (
    MangaAuthorController,
)
from shinbotsu_data.database.controllers.manga_controller import MangaController
from shinbotsu_data.database.controllers.manga_relation_controller import (
    MangaRelationController,
)
from shinbotsu_data.database.controllers.manga_tag_controller import MangaTagController
from shinbotsu_data.database.controllers.producer_controller import ProducerController
from shinbotsu_data.database.controllers.scraper_state_controller import (
    ScraperStateController,
)
from shinbotsu_data.database.controllers.tag_mangadex_controller import (
    TagMangadexController,
)
from shinbotsu_data.database.db_models import Base


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(
            db_uri, pool_size=5, pool_timeout=30, pool_recycle=3600
        )
        self.session_maker = sessionmaker(self._engine)
        self.db_schema = "data"
        self.tag_controller = TagController(self.session_maker)
        self.producer_controller = ProducerController(self.session_maker)
        self.anime_controller = AnimeController(self.session_maker)
        self.manga_controller = MangaController(self.session_maker)
        self.anime_tag_controller = AnimeTagController(self.session_maker)
        self.manga_tag_controller = MangaTagController(self.session_maker)
        self.anime_producer_controller = AnimeProducerController(self.session_maker)
        self.scraper_state_controller = ScraperStateController(self.session_maker)
        self.manga_controller = MangaController(self.session_maker)
        self.manga_author_controller = MangaAuthorController(self.session_maker)
        self.manga_relation_controller = MangaRelationController(self.session_maker)
        self.tag_mangadex_controller = TagMangadexController(self.session_maker)
        self.author_controller = AuthorController(self.session_maker)

    def _create_schema_if_not_exists(self, schema_name: str) -> None:
        with self._engine.connect() as connection:
            connection.execute(CreateSchema(schema_name, if_not_exists=True))
            connection.commit()

    def initialize_tables(self) -> None:
        self._create_schema_if_not_exists(self.db_schema)
        Base.metadata.create_all(self._engine)
