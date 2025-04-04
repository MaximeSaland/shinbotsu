from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from shinbotsu_data.database.db_models import Base


class Database:
    def __init__(self, db_uri: str):
        self._engine = create_engine(
            db_uri, pool_size=5, pool_timeout=30, pool_recycle=3600
        )
        self.session_maker = sessionmaker(self._engine)
        self.db_schema = "data"

    def _create_schema_if_not_exists(self, schema_name: str) -> None:
        with self._engine.connect() as connection:
            connection.execute(CreateSchema(schema_name, if_not_exists=True))
            connection.commit()

    def initialize_tables(self) -> None:
        self._create_schema_if_not_exists(self.db_schema)
        Base.metadata.create_all(self._engine)
