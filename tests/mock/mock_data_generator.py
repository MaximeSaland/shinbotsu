import datetime
from typing import Optional, Any

from faker.proxy import Faker

from shinbotsu_data.core.schemas import ProducerModel, TagModel


def generate_fake_anime(
    fake: Faker,
    producers: list[ProducerModel],
    licensors: list[ProducerModel],
    studios: list[ProducerModel],
    genres: Optional[list[TagModel]] = None,
    themes: Optional[list[TagModel]] = None,
    demographics: Optional[list[TagModel]] = None,
) -> dict[str, Any]:
    from_date = fake.date_between_dates(
        date_start=datetime.date(1900, 1, 1), date_end=datetime.date(2020, 1, 1)
    )
    to_date = fake.past_date(start_date=from_date)
    return {
        "mal_id": fake.unique.random_int(0, 300),
        "url": fake.url(),
        "images": {
            "jpg": {
                "image_url": fake.url(),
                "small_image_url": fake.url(),
                "large_image_url": fake.url(),
            },
            "webp": {
                "image_url": fake.url(),
                "small_image_url": fake.url(),
                "large_image_url": fake.url(),
            },
        },
        "trailer": {
            "youtube_id": fake.word(),
            "url": fake.url(),
            "embed_url": fake.url(),
        },
        "approved": True,
        "titles": [
            {"type": "string", "title": "string"} for _ in range(fake.random_int(0, 3))
        ],
        "title": fake.unique.word(),
        "title_english": fake.word(),
        "title_japanese": fake.word(),
        "title_synonyms": [fake.word() for _ in range(fake.random_int(0, 2))],
        "type": fake.random_element(["tv", "movie", "ova", "special", "ona"]),
        "source": fake.random_element(["original", "manga", "novel"]),
        "episodes": fake.random_int(1, 2000),
        "status": fake.random_element(["airing", "complete", "upcoming"]),
        "airing": False,
        "aired": {
            "from": from_date.__str__(),
            "to": to_date.__str__(),
            "prop": {
                "from": {
                    "day": from_date.day,
                    "month": from_date.month,
                    "year": from_date.year,
                },
                "to": {
                    "day": to_date.day,
                    "month": to_date.month,
                    "year": to_date.year,
                },
                "string": f"{from_date.__str__()} to {to_date.__str__()}",
            },
        },
        "duration": "24 min per episodes",
        "rating": fake.random_element(["g", "pg", "pg13", "r17", "r", "rx"]),
        "score": fake.random_int(0, 1000) / 100,
        "scored_by": fake.random_int(1, 100000),
        "rank": fake.random_int(1, 30000),
        "popularity": fake.random_int(1, 30000),
        "members": fake.random_int(1, 100000),
        "favorites": fake.random_int(1, 100000),
        "synopsis": fake.paragraph(),
        "background": fake.paragraph(),
        "season": fake.random_element(["winter", "spring", "summer", "autumn"]),
        "year": from_date.year,
        "broadcast": {
            "day": fake.day_of_week(),
            "time": fake.time().__str__(),
            "timezone": "Asia/Tokyo",
            "string": "fake string",
        },
        "producers": [
            {
                "mal_id": producer.id_mal,
                "type": "anime",
                "name": producer.title,
                "url": producer.url_mal,
            }
            for producer in producers
        ],
        "licensors": [
            {
                "mal_id": licensor.id_mal,
                "type": "anime",
                "name": licensor.title,
                "url": licensor.url_mal,
            }
            for licensor in licensors
        ],
        "studios": [
            {
                "mal_id": studio.id_mal,
                "type": "anime",
                "name": studio.title,
                "url": studio.url_mal,
            }
            for studio in studios
        ],
        "genres": [
            {
                "mal_id": genre.id_mal,
                "type": "anime",
                "name": genre.name,
                "url": fake.url(),
            }
            for genre in genres
        ]
        if genres is not None
        else [],
        "explicit_genres": [],
        "themes": [
            {
                "mal_id": theme.id_mal,
                "type": "anime",
                "name": theme.name,
                "url": fake.url(),
            }
            for theme in themes
        ]
        if themes is not None
        else [],
        "demographics": [
            {
                "mal_id": demographic.id_mal,
                "type": "anime",
                "name": demographic.name,
                "url": fake.url(),
            }
            for demographic in demographics
        ]
        if demographics is not None
        else [],
    }


def generate_fake_manga(fake: Faker, id: int) -> dict[str, Any]:
    from_date = fake.date_time_between_dates(
        datetime_start=datetime.date(1900, 1, 1), datetime_end=datetime.date(2020, 1, 1)
    )
    to_date = fake.past_datetime(start_date=from_date)
    return {
        "mal_id": id,
        "url": fake.unique.url(),
        "images": {
            "jpg": {
                "image_url": fake.url(),
                "small_image_url": fake.url(),
                "large_image_url": fake.url(),
            },
            "webp": {
                "image_url": fake.url(),
                "small_image_url": fake.url(),
                "large_image_url": fake.url(),
            },
        },
        "approved": fake.boolean(chance_of_getting_true=50),
        "titles": [
            {"type": fake.word(), "title": fake.word()}
            for _ in range(fake.random_int(0, 3))
        ],
        "title": fake.word(),
        "title_english": fake.word(),
        "title_japanese": fake.word(),
        "type": fake.random_element(
            ["manga", "novel", "oneshot", "doujin", "manhwa", "manhua", "light novel"]
        ),
        "chapters": fake.random_int(0, 2000),
        "volumes": fake.random_int(0, 200),
        "status": fake.random_element(
            ["publishing", "complete", "hiatus", "discontinued", "upcoming"]
        ),
        "publishing": fake.boolean(chance_of_getting_true=50),
        "published": {
            "from": from_date.__str__(),
            "to": to_date.__str__(),
            "prop": {
                "from": {
                    "day": from_date.day,
                    "month": from_date.month,
                    "year": from_date.year,
                },
                "to": {
                    "day": to_date.day,
                    "month": to_date.month,
                    "year": to_date.year,
                },
                "string": f"{from_date.__str__()} to {to_date.__str__()}",
            },
        },
        "score": fake.random_int(0, 100),
        "scored_by": fake.random_int(0, 100000),
        "rank": fake.random_int(0, 30000),
        "popularity": fake.random_int(0, 30000),
        "members": fake.random_int(0, 100000),
        "favorites": fake.random_int(0, 100000),
        "synopsis": fake.paragraph(),
        "background": fake.paragraph(),
        "authors": [
            {
                "mal_id": fake.random_int(0, 10000),
                "type": fake.word(),
                "name": fake.name(),
                "url": fake.url(),
            }
            for _ in range(fake.random_int(1, 2))
        ],
        "serializations": [
            {
                "mal_id": fake.random_int(0, 10000),
                "type": fake.word(),
                "name": fake.company(),
                "url": fake.url(),
            }
        ],
        "genres": [
            {
                "mal_id": fake.random_int(1, 200),
                "type": fake.word(),
                "name": fake.word(),
                "url": fake.url(),
            }
            for _ in range(fake.random_int(1, 4))
        ],
        "explicit_genres": [
            {
                "mal_id": fake.random_int(1, 200),
                "type": fake.word(),
                "name": fake.word(),
                "url": fake.url(),
            }
            for _ in range(fake.random_int(0, 2))
        ],
        "themes": [
            {
                "mal_id": fake.random_int(1, 200),
                "type": fake.word(),
                "name": fake.word(),
                "url": fake.url(),
            }
            for _ in range(fake.random_int(0, 4))
        ],
        "demographics": [
            {
                "mal_id": fake.random_int(1, 200),
                "type": fake.word(),
                "name": fake.word(),
                "url": fake.url(),
            }
            for _ in range(fake.random_int(0, 1))
        ],
    }


def generate_fake_tag(fake: Faker) -> dict[str, Any]:
    return {
        "mal_id": fake.unique.random_int(0, 300),
        "name": fake.word(),
        "url": fake.url(),
        "count": fake.random_int(0, 100000),
    }


def generate_fake_producer(fake: Faker, nb_titles: int = 1) -> dict[str, Any]:
    return {
        "mal_id": fake.unique.random_int(0, 300),
        "url": fake.url(),
        "titles": [
            {"type": f"type{i}", "title": fake.unique.company()}
            for i in range(nb_titles)
        ],
        "images": {"jpg": {"image_url": fake.url()}},
        "favorites": fake.random_int(0, 100000),
        "count": fake.random_int(0, 100000),
        "established": fake.past_date(datetime.date(1900, 1, 1)).__str__(),
        "about": fake.paragraph(),
    }


def generate_fake_magazine(fake: Faker) -> dict[str, Any]:
    return {
        "mal_id": fake.unique.random_int(1, 300),
        "name": fake.company(),
        "url": fake.url(),
        "count": fake.random_int(0, 100000),
    }


def generate_fake_people(fake: Faker) -> dict[str, Any]:
    first_name = fake.unique.first_name()
    last_name = fake.unique.last_name()
    return {
        "mal_id": fake.unique.random_int(0, 300),
        "url": fake.url(),
        "website_url": fake.url(),
        "images": {"jpg": {"image_url": fake.url()}},
        "name": f"{first_name} {last_name}",
        "given_name": first_name,
        "family_name": last_name,
        "alternate_names": [fake.name() for _ in range(fake.random_int(0, 2))],
        "birthday": fake.past_datetime(datetime.date(1900, 1, 1)).__str__(),
        "favorites": fake.random_int(0, 100000),
        "about": fake.paragraph(),
    }
