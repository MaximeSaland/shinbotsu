from enum import Enum


class ApiUrls(str, Enum):
    JIKAN = "https://api.jikan.moe/v4"
    MANGADEX = "https://api.mangadex.org"


class MangadexEndpoints(str, Enum):
    AUTHOR = ApiUrls.MANGADEX.value + "/author"
    MANGA = ApiUrls.MANGADEX.value + "/manga"
    TAG = ApiUrls.MANGADEX.value + "/manga/tag"


class JikanEndpoints(str, Enum):
    ANIME = ApiUrls.JIKAN.value + "/anime"
    MANGA = ApiUrls.JIKAN.value + "/manga"
    TAG_ANIME = ApiUrls.JIKAN.value + "/genres/anime"
    TAG_MANGA = ApiUrls.JIKAN.value + "/genres/manga"
    PRODUCERS = ApiUrls.JIKAN.value + "/producers"
    MAGAZINES = ApiUrls.JIKAN.value + "/magazines"
    PEOPLE = ApiUrls.JIKAN.value + "/people"
