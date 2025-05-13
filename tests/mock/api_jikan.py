from typing import Any, Optional

from requests_mock.mocker import Mocker

from shinbotsu_data.utils import JikanEndpoints


class JikanAPIMock(Mocker):
    """Mock response from request to jikan api"""

    def __init__(
        self,
        tag_data: Optional[list[dict[str, Any]]] = None,
        producer_data: Optional[list[dict[str, Any]]] = None,
        anime_data: Optional[list[dict[str, Any]]] = None,
        items_per_page: int = 5,
    ):
        super().__init__()
        self.tag_data = tag_data
        self.producer_data = producer_data
        self.anime_data = anime_data
        self.items_per_page = items_per_page

    def _pagination(
        self, current_page: int, last_page: int, count: int, total_items: int
    ) -> dict[str, Any]:
        return {
            "last_visible_page": last_page,
            "has_next_page": current_page == last_page,
            "current_page": current_page,
            "items": {
                "count": count,
                "total": total_items,
                "per_page": self.items_per_page,
            },
        }

    def __enter__(self) -> Any:
        mocker = super().__enter__()

        if self.tag_data is not None:
            mocker.get(
                url=JikanEndpoints.TAG_MANGA.value,
                json={"data": self.tag_data},
            )

        if self.producer_data is not None:
            nb_pages_producers = (
                1 + (len(self.producer_data) - 1) // self.items_per_page
            )
            for page in range(nb_pages_producers):
                start = self.items_per_page * page
                end = min(start + self.items_per_page, len(self.producer_data))
                mocker.get(
                    url=JikanEndpoints.PRODUCERS.value + f"?page={page + 1}",
                    json={
                        "pagination": self._pagination(
                            page,
                            nb_pages_producers,
                            end - start,
                            len(self.producer_data),
                        ),
                        "data": self.producer_data[start:end],
                    },
                )

        if self.anime_data is not None:
            nb_pages_anime = 1 + (len(self.anime_data) - 1) // self.items_per_page
            for page in range(nb_pages_anime):
                start = self.items_per_page * page
                end = min(start + self.items_per_page, len(self.anime_data))
                mocker.get(
                    url=JikanEndpoints.ANIME.value + f"?page={page + 1}",
                    json={
                        "pagination": self._pagination(
                            page, nb_pages_anime, end - start, len(self.anime_data)
                        ),
                        "data": self.anime_data[start:end],
                    },
                )
        return mocker
