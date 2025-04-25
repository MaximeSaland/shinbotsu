from enum import Enum


class ApiUrls(str, Enum):
    JIKAN = "https://api.jikan.moe/v4"
    MANGADEX = "https://api.mangadex.org"


class MangadexEndpoints(str, Enum):
    AUTHOR = "/author"
    MANGA = "/manga"
    TAG = "/manga/tag"


class JikanEndpoints(str, Enum):
    ANIME = "/anime"
    MANGA = "/manga"
    TAG_ANIME = "/genres/anime"
    TAG_MANGA = "/genres/manga"
    PRODUCERS = "/producers"
    MAGAZINES = "/magazines"
    PEOPLE = "/people"
