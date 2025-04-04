from typing import Callable

from shinbotsu_data.api.jikan import JikanApiExtractor
from shinbotsu_data.core.etl.jikan import etl_jikan
from shinbotsu_data.database.database import Database
from shinbotsu_data.settings import Settings

apis = {
    "JIKAN": JikanApiExtractor,
}

etl_mapping: dict[str, Callable[[Database, JikanApiExtractor], None]] = {
    "JIKAN": etl_jikan,
}


def etl_factory(settings: Settings) -> Callable[[Database], None]:
    try:
        scrapper_function = etl_mapping[settings.etl_name]
    except KeyError:
        raise ValueError(f"ETL {settings.etl_name} not found")

    return lambda db: scrapper_function(db, apis[settings.etl_name]())
