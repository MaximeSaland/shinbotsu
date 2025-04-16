from typing import Generator

import pytest
from faker import Faker
from sqlalchemy_utils import database_exists, drop_database, create_database

from shinbotsu_data.api.jikan import JikanApiExtractor
from shinbotsu_data.database.database import Database
from shinbotsu_data.settings import Settings


@pytest.fixture(scope="function")
def settings() -> Generator[Settings, None, None]:
    yield Settings()


@pytest.fixture(scope="function")
def db(settings: Settings) -> Generator[Database, None, None]:
    """Creates an empty db in memory and initializes it with all its tables
    Returns
    -------
    The initialized database.
    """
    db_uri = settings.db_uri_test
    if database_exists(db_uri):
        drop_database(db_uri)
    create_database(db_uri)
    db = Database(db_uri)
    db.initialize_tables()
    yield db

    drop_database(db_uri)


@pytest.fixture
def faker_tag() -> Faker:
    return Faker()


@pytest.fixture
def faker_producer() -> Faker:
    return Faker()


@pytest.fixture
def faker_anime() -> Faker:
    return Faker()


@pytest.fixture
def jikan_api_extractor() -> JikanApiExtractor:
    return JikanApiExtractor()
